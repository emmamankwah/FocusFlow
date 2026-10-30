import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import usePageTitle from '@/lib/usePageTitle'
import '../Dashboard/dashboard.css'
import {
  FOCUS_GOAL_HOURS,
  baseTasks,
  fmtLongDate,
  getChartData,
  getRisks,
  greeting,
  loadBoard,
  makeNotes,
  makeSuggestions,
  saveBoard,
  userFirstName,
  userFullName,
  userInitials,
} from '../Dashboard/data.js'
import { buildPlannerContext, sendPlannerMessage } from '@/lib/ai'
import { getSessionUser } from '@/lib/mockAuth'
import {
  BrandMark,
  BTN,
  BTN_PRIMARY,
  MenuIcon,
  SectionLabel,
  SparkIcon,
  cx,
} from '../Dashboard/ui.jsx'
import { ChatSection } from '../Dashboard/ChatNotes.jsx'

const initialChat = (name) => [
  {
    role: 'ai',
    text: `Hi ${name}. Ask me what to focus on next, why a deadline is risky, or whether your workload is too heavy.`,
  },
]

function AiPlannerNav({ open, onClose, active, unread, user }) {
  useEffect(() => {
    if (!open) return undefined

    const onKeyDown = (event) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKeyDown)

    return () => {
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open, onClose])

  const nav = [
    { id: 'ai-top', label: 'AI Planner', to: '/ai-planner' },
    { id: 'dashboard', label: 'Dashboard', to: '/dashboard' },
    { id: 'focus', label: 'Focus', to: '/dashboard#sec-focus' },
    { id: 'work', label: 'Work Inbox', to: '/dashboard#sec-work' },
    { id: 'modules', label: 'Modules', to: '/dashboard#sec-modules' },
    { id: 'chat', label: 'Chat', to: '/ai-planner' },
  ]

  if (!open) return null

  return (
    <>
      <button
        type="button"
        aria-label="Close navigation menu"
        onClick={onClose}
        className="fixed inset-0 z-30 h-full w-full cursor-default bg-inkwell/35 backdrop-blur-sm lg:hidden"
      />

      <aside
        id="ff-ai-nav"
        aria-label="AI planner navigation"
        className="fixed top-14 bottom-0 left-0 z-40 flex w-[min(300px,86vw)] flex-col border-r border-line/80 bg-canvas p-5 shadow-[0_24px_60px_-25px_rgba(16,27,59,0.35)] lg:static lg:z-auto lg:w-[200px] lg:shrink-0 lg:border-r-0 lg:bg-transparent lg:p-0 lg:shadow-none"
      >
        <div className="flex items-center gap-3">
          <Link
            to="/"
            onClick={onClose}
            className="inline-flex min-w-0 items-center gap-2.5"
            aria-label="FocusFlow home"
          >
            <BrandMark />
            <span className="font-grotesk text-[1.05rem] font-bold tracking-[-0.02em] text-ink">
              Focus<span className="text-amber">Flow</span>
            </span>
          </Link>
        </div>

        <nav aria-label="AI planner navigation" className="mt-6 grid gap-1">
          {nav.map((item) => {
            const isActive = active === item.id
            return (
              <Link
                key={item.id}
                to={item.to}
                onClick={onClose}
                aria-current={isActive ? 'true' : undefined}
                className={cx(
                  'flex min-h-9 items-center justify-between gap-2 rounded-lg border-l-2 px-3 py-2 text-left font-mono text-[0.63rem] tracking-[0.13em] uppercase transition',
                  isActive
                    ? 'border-amber bg-amber/10 text-amber'
                    : 'border-transparent text-dim hover:bg-deck/60 hover:text-ink',
                )}
              >
                <span>{item.label}</span>
                {item.id === 'chat' && unread > 0 && (
                  <span
                    className="rounded-full bg-amber px-1.5 py-0.5 font-mono text-[0.56rem] font-semibold tracking-normal text-white"
                    aria-label={`${unread} unread notifications`}
                  >
                    {unread}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>

        <div className="mt-auto border-t border-line/60 pt-4">
          <Link
            to="/dashboard"
            onClick={onClose}
            className="flex items-center gap-2.5 rounded-xl border border-line/80 bg-surface/70 p-2.5"
          >
            <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full border border-amber/30 bg-amber/10 font-grotesk text-[0.7rem] font-bold text-amber">
              {userInitials(user)}
            </span>
            <span className="min-w-0">
              <span className="block truncate text-[0.78rem] font-semibold text-ink">
                {userFullName(user)}
              </span>
              <span className="block font-mono text-[0.54rem] tracking-[0.14em] text-dim uppercase">Back to dashboard</span>
            </span>
          </Link>
        </div>
      </aside>
    </>
  )
}

export default function AiPlanner() {
  usePageTitle('AI Planner — FocusFlow')

  const today = useMemo(() => new Date(), [])
  const user = useMemo(() => getSessionUser(), [])
  const [board, setBoard] = useState(() => loadBoard(today))
  const [active, setActive] = useState('ai-top')
  const [navOpen, setNavOpen] = useState(false)
  const [toast, setToast] = useState('')
  const toastTimer = useRef(null)

  const openNav = useCallback(() => setNavOpen(true), [])
  const closeNav = useCallback(() => setNavOpen(false), [])

  const [chat, setChat] = useState(() => initialChat(userFirstName(user)))
  const [chatInput, setChatInput] = useState('')
  const [chatPending, setChatPending] = useState(false)
  const chatTimer = useRef(null)
  const chatLogRef = useRef(null)

  const suggestions = useMemo(() => makeSuggestions(today), [today])
  const notes = useMemo(() => makeNotes(today), [today])
  const risks = useMemo(() => getRisks(today, board.sugs), [today, board.sugs])

  const allTasks = useMemo(
    () => [...baseTasks, ...board.custom].sort((a, b) => a.t.localeCompare(b.t)),
    [board.custom],
  )
  const score = board.sugs.s2 === 'done' ? 33 : 41
  const unread = notes.filter((note) => !board.read[note.id]).length

  const showToast = useCallback((message) => {
    setToast(message)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(''), 2800)
  }, [])

  useEffect(() => {
    saveBoard(board, today)
  }, [board, today])

  useEffect(() => () => clearTimeout(toastTimer.current), [])
  useEffect(() => () => clearTimeout(chatTimer.current), [])

  useEffect(() => {
    const el = chatLogRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [chat])

  const ask = useCallback(
    async (raw) => {
      const question = raw.trim()
      if (!question || chatPending) return

      const nextMessages = [...chat, { role: 'user', text: question }]
      setChat(nextMessages)
      setChatPending(true)

      const context = buildPlannerContext({
        dateLabel: fmtLongDate(today),
        score,
        restPlanned: board.sugs.s2 === 'done',
        pendingTasks: allTasks.filter((task) => !board.done[task.id]),
        risks,
      })

      try {
        const reply = await sendPlannerMessage(nextMessages, context)
        setChat((prev) => [...prev, { role: 'ai', text: reply }])
      } catch {
        setChat((prev) => [
          ...prev,
          {
            role: 'ai',
            error: true,
            text: 'I could not reach the AI service. Check that the backend is running, then try again.',
          },
        ])
      } finally {
        setChatPending(false)
      }
    },
    [allTasks, board.done, board.sugs.s2, chat, chatPending, risks, score, today],
  )

  function handleSend(event) {
    event.preventDefault()
    if (!chatInput.trim() || chatPending) return
    ask(chatInput)
    setChatInput('')
  }

  function handleAttach(type) {
    if (type === 'image') {
      showToast('Image upload coming soon (demo)')
      setChat((prev) => [
        ...prev,
        { role: 'user', text: '[Attached image]' },
      ])
      clearTimeout(chatTimer.current)
      chatTimer.current = setTimeout(() => {
        setChat((prev) => [...prev, { role: 'ai', text: 'I can see the image. Share details and I’ll factor it into your plan.' }])
      }, 360)
      return
    }
    if (type === 'document') {
      showToast('Document attached (demo)')
      setChat((prev) => [
        ...prev,
        { role: 'user', text: '[Attached document]' },
      ])
      clearTimeout(chatTimer.current)
      chatTimer.current = setTimeout(() => {
        setChat((prev) => [...prev, { role: 'ai', text: 'Got the document. I’ll extract key deadlines/tasks and suggest next steps.' }])
      }, 360)
      return
    }
    showToast('Files attached (demo)')
    setChat((prev) => [
      ...prev,
      { role: 'user', text: '[Attached file]' },
    ])
    clearTimeout(chatTimer.current)
    chatTimer.current = setTimeout(() => {
      setChat((prev) => [...prev, { role: 'ai', text: 'Files received. Tell me what you’d like me to do with them.' }])
    }, 360)
  }

  function handleVoice() {
    showToast('Voice input (demo)')
    setChat((prev) => [
      ...prev,
      { role: 'user', text: '[Voice message]' },
    ])
    clearTimeout(chatTimer.current)
    chatTimer.current = setTimeout(() => {
      setChat((prev) => [...prev, { role: 'ai', text: 'I heard you. Want me to prioritize based on your current plan?' }])
    }, 360)
  }

  function handleDeepSearch() {
    showToast('Deep search started (demo)')
    setChat((prev) => [
      ...prev,
      { role: 'user', text: '[Deep search requested]' },
    ])
    clearTimeout(chatTimer.current)
    chatTimer.current = setTimeout(() => {
      setChat((prev) => [...prev, { role: 'ai', text: 'Running a deeper search across your plan, deadlines, and suggestions to find the best next action.' }])
    }, 360)
  }

  function handleWebSearch() {
    showToast('Web search enabled (demo)')
    setChat((prev) => [
      ...prev,
      { role: 'user', text: '[Web search requested]' },
    ])
    clearTimeout(chatTimer.current)
    chatTimer.current = setTimeout(() => {
      setChat((prev) => [...prev, { role: 'ai', text: 'I’ll look for relevant resources online and summarize actionable results for your plan.' }])
    }, 360)
  }

  function handleSearchPriorities() {
    showToast('Searching priorities (demo)')
    setChat((prev) => [
      ...prev,
      { role: 'user', text: '[Search priorities]' },
    ])
    clearTimeout(chatTimer.current)
    chatTimer.current = setTimeout(() => {
      setChat((prev) => [...prev, { role: 'ai', text: 'Priorities ranked by urgency/risk: focus on your highest-risk deadline first, then quick wins.' }])
    }, 360)
  }

  return (
    <div id="dashboard" className="ff-product ff-dashboard ff-app relative h-[100dvh] overflow-hidden bg-canvas font-sans text-ink">
      <div aria-hidden="true" className="pointer-events-none fixed inset-0">
        <div className="absolute -top-40 -left-32 h-[520px] w-[520px] rounded-full bg-amber/[0.06] blur-3xl" />
        <div className="absolute top-1/4 -right-40 h-[420px] w-[420px] rounded-full bg-cyan/[0.04] blur-3xl" />
        <div className="absolute bottom-[-160px] left-1/3 h-[420px] w-[420px] rounded-full bg-coral/[0.04] blur-3xl" />
        <div className="ffd-grid-bg absolute inset-0" />
      </div>

      <div className="relative mx-auto flex h-full w-full max-w-[1320px] flex-col px-4 py-4 sm:px-6 lg:px-8 lg:py-6">
        <div className="relative z-50 flex h-10 shrink-0 items-center">
          <button
            type="button"
            onClick={navOpen ? closeNav : openNav}
            aria-expanded={navOpen}
            aria-controls="ff-ai-nav"
            aria-label={navOpen ? 'Close navigation menu' : 'Open navigation menu'}
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-line bg-surface text-ink transition duration-150 hover:border-dim focus-visible:ring-2 focus-visible:ring-amber/35 focus-visible:ring-offset-2 focus-visible:ring-offset-canvas focus-visible:outline-none"
          >
            <MenuIcon open={navOpen} className="h-4 w-4" />
          </button>
        </div>

        <div className="flex min-h-0 w-full flex-1 gap-4 lg:gap-6">
          <AiPlannerNav
            open={navOpen}
            onClose={closeNav}
            active={active}
            unread={unread}
            user={user}
          />

          <main className="ff-main flex min-h-0 min-w-0 flex-1 flex-col">
            <ChatSection
              messages={chat}
              chatInput={chatInput}
              onChatInput={setChatInput}
              onSend={handleSend}
              onAsk={ask}
              logRef={chatLogRef}
              pending={chatPending}
              variant="full"
              onAttach={handleAttach}
              onVoice={handleVoice}
              onDeepSearch={handleDeepSearch}
              onWebSearch={handleWebSearch}
              onSearchPriorities={handleSearchPriorities}
            />
          </main>
        </div>
      </div>

      <div
        role="status"
        aria-live="polite"
        className={cx(
          'ffd-toast fixed bottom-5 left-1/2 z-40 w-[92vw] max-w-[420px] -translate-x-1/2 rounded-xl border border-amber/30 bg-surface px-4 py-3 text-center text-[0.8rem] font-medium text-ink shadow-[0_22px_70px_-30px_rgba(16,27,59,0.35)]',
          toast ? 'translate-y-0 opacity-100' : 'pointer-events-none translate-y-2 opacity-0',
        )}
      >
        {toast}
      </div>
    </div>
  )
}
