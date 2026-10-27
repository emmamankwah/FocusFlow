import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import usePageTitle from '@/lib/usePageTitle'
import '../Dashboard/dashboard.css'
import {
  FOCUS_GOAL_HOURS,
  baseTasks,
  chatReply,
  fmtLongDate,
  getChartData,
  getRisks,
  greeting,
  loadBoard,
  makeNotes,
  makeSuggestions,
  saveBoard,
} from '../Dashboard/data.js'
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

const INITIAL_CHAT = [
  {
    role: 'ai',
    text: 'Hi Ama. Ask me what to focus on next, why a deadline is risky, or whether your workload is too heavy.',
  },
]

function prefersReducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

function DashboardRailLite({ active, unread }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef(null)
  const menuButtonRef = useRef(null)

  useEffect(() => {
    if (!menuOpen) return undefined

    const onKeyDown = (event) => {
      if (event.key === 'Escape') {
        setMenuOpen(false)
        menuButtonRef.current?.focus()
      }
    }
    const onPointerDown = (event) => {
      if (
        !menuRef.current?.contains(event.target) &&
        !menuButtonRef.current?.contains(event.target)
      ) {
        setMenuOpen(false)
      }
    }
    const desktop = window.matchMedia?.('(min-width: 64rem)')
    const closeOnDesktop = () => {
      if (desktop?.matches) setMenuOpen(false)
    }

    document.addEventListener('keydown', onKeyDown)
    document.addEventListener('pointerdown', onPointerDown)
    desktop?.addEventListener('change', closeOnDesktop)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.removeEventListener('pointerdown', onPointerDown)
      desktop?.removeEventListener('change', closeOnDesktop)
    }
  }, [menuOpen])

  const nav = [
    { id: 'ai-top', label: 'AI Planner', to: '/ai-planner' },
    { id: 'dashboard', label: 'Dashboard', to: '/dashboard' },
    { id: 'focus', label: 'Focus', to: '/dashboard#sec-focus' },
    { id: 'work', label: 'Work Inbox', to: '/dashboard#sec-work' },
    { id: 'modules', label: 'Modules', to: '/dashboard#sec-modules' },
    { id: 'chat', label: 'Chat', to: '/ai-planner' },
  ]

  return (
    <aside className="ff-rail relative lg:sticky lg:top-8">
      <div className="flex flex-col gap-3 lg:gap-5">
        <div className="flex items-center justify-between gap-3">
          <Link
            to="/"
            className="inline-flex min-w-0 items-center gap-2.5"
            aria-label="FocusFlow home"
          >
            <BrandMark />
            <span className="font-grotesk text-[1.05rem] font-bold tracking-[-0.02em] text-ink">
              Focus<span className="text-amber">Flow</span>
            </span>
          </Link>
          <button
            ref={menuButtonRef}
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            aria-expanded={menuOpen}
            aria-controls="ff-ai-menu"
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-[3px] border border-line bg-surface text-ink transition duration-150 hover:border-dim focus-visible:ring-2 focus-visible:ring-amber/35 focus-visible:ring-offset-2 focus-visible:ring-offset-canvas focus-visible:outline-none lg:hidden"
          >
            <MenuIcon open={menuOpen} className="h-4 w-4" />
          </button>
        </div>

        <div
          id="ff-ai-menu"
          ref={menuRef}
          className={cx(
            'ffd-menu absolute top-full right-0 z-30 mt-2 max-h-[calc(100vh-6rem)] w-[min(280px,calc(100vw-2rem))] overflow-y-auto rounded-2xl border border-line/80 bg-surface p-2 shadow-[0_24px_70px_-30px_rgba(0,0,0,0.95)] lg:static lg:mt-0 lg:w-full lg:overflow-visible lg:rounded-none lg:border-0 lg:bg-transparent lg:p-0 lg:shadow-none lg:contents',
            menuOpen ? 'block' : 'hidden',
          )}
        >
          <nav aria-label="AI planner navigation" className="ff-nav grid w-full gap-1 lg:flex lg:flex-col">
            {nav.map((item) => {
              const isActive = active === item.id
              const common = cx(
                'flex min-h-9 shrink-0 items-center justify-between gap-2 rounded-lg border-l-2 px-3 py-2 text-left font-mono text-[0.63rem] tracking-[0.13em] uppercase transition lg:w-full',
                isActive
                  ? 'border-amber bg-amber/10 text-amber'
                  : 'border-transparent text-dim hover:bg-deck/60 hover:text-ink',
              )
              if (item.to.startsWith('/')) {
                return (
                  <Link key={item.id} to={item.to} onClick={() => setMenuOpen(false)} className={common}>
                    <span>{item.label}</span>
                    {item.id === 'chat' && unread > 0 && (
                      <span
                        className="rounded-full bg-amber px-1.5 py-0.5 font-mono text-[0.56rem] font-semibold tracking-normal text-[#171205]"
                        aria-label={`${unread} unread notifications`}
                      >
                        {unread}
                      </span>
                    )}
                  </Link>
                )
              }
              return (
                <a key={item.id} href={item.to} onClick={() => setMenuOpen(false)} className={common}>
                  <span>{item.label}</span>
                </a>
              )
            })}
          </nav>

          <div className="mt-2 border-t border-line/60 px-1 pt-3 pb-1 lg:hidden">
            <Link
              to="/dashboard"
              className="flex items-center gap-2.5 rounded-xl border border-line/80 bg-surface/70 p-2.5"
            >
              <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full border border-amber/30 bg-amber/10 font-grotesk text-[0.7rem] font-bold text-amber">
                AM
              </span>
              <span className="min-w-0">
                <span className="block truncate text-[0.78rem] font-semibold text-ink">Ama Mensah</span>
                <span className="block font-mono text-[0.54rem] tracking-[0.14em] text-dim uppercase">Back to dashboard</span>
              </span>
            </Link>
          </div>
        </div>

        <div className="hidden lg:block">
          <Link
            to="/dashboard"
            className="flex items-center gap-2.5 rounded-xl border border-line/80 bg-surface/70 p-2.5"
          >
            <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full border border-amber/30 bg-amber/10 font-grotesk text-[0.7rem] font-bold text-amber">
              AM
            </span>
            <span className="min-w-0">
              <span className="block truncate text-[0.78rem] font-semibold text-ink">Ama Mensah</span>
              <span className="block font-mono text-[0.54rem] tracking-[0.14em] text-dim uppercase">Back to dashboard</span>
            </span>
          </Link>
        </div>
      </div>
    </aside>
  )
}

export default function AiPlanner() {
  usePageTitle('AI Planner — FocusFlow')

  const today = useMemo(() => new Date(), [])
  const [board, setBoard] = useState(() => loadBoard(today))
  const [active, setActive] = useState('ai-top')
  const [toast, setToast] = useState('')
  const toastTimer = useRef(null)

  const [chat, setChat] = useState(INITIAL_CHAT)
  const [chatInput, setChatInput] = useState('')
  const chatTimer = useRef(null)
  const chatLogRef = useRef(null)

  const suggestions = useMemo(() => makeSuggestions(today), [today])
  const notes = useMemo(() => makeNotes(today), [today])
  const risks = useMemo(() => getRisks(today, board.sugs), [today, board.sugs])

  const allTasks = useMemo(
    () => [...baseTasks, ...board.custom].sort((a, b) => a.t.localeCompare(b.t)),
    [board.custom],
  )
  const heroTask = allTasks.find((task) => task.type === 'focus' && !board.done[task.id]) ?? null
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
    (raw) => {
      const question = raw.trim()
      if (!question) return
      setChat((prev) => [...prev, { role: 'user', text: question }])
      clearTimeout(chatTimer.current)
      const context = {
        firstFocus: heroTask,
        score,
        labRisk: risks[0],
        restPlanned: board.sugs.s2 === 'done',
      }
      chatTimer.current = setTimeout(() => {
        setChat((prev) => [...prev, { role: 'ai', text: chatReply(question, context) }])
      }, 360)
    },
    [heroTask, score, risks, board.sugs.s2],
  )

  function handleSend(event) {
    event.preventDefault()
    if (!chatInput.trim()) return
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
    <div id="dashboard" className="ff-dashboard ff-app relative min-h-screen bg-canvas font-sans text-ink">
      <div aria-hidden="true" className="pointer-events-none fixed inset-0">
        <div className="absolute -top-40 -left-32 h-[520px] w-[520px] rounded-full bg-amber/[0.06] blur-3xl" />
        <div className="absolute top-1/4 -right-40 h-[420px] w-[420px] rounded-full bg-cyan/[0.04] blur-3xl" />
        <div className="absolute bottom-[-160px] left-1/3 h-[420px] w-[420px] rounded-full bg-coral/[0.04] blur-3xl" />
        <div className="ffd-grid-bg absolute inset-0" />
      </div>

      <div className="relative mx-auto w-full max-w-[1320px] px-4 py-6 sm:px-6 lg:grid lg:grid-cols-[200px_minmax(0,1fr)] lg:items-start lg:gap-8 lg:px-8 lg:py-8">
        <DashboardRailLite active={active} unread={unread} />

        <main className="ff-main mt-5 min-w-0 lg:mt-0">
          <ChatSection
            messages={chat}
            chatInput={chatInput}
            onChatInput={setChatInput}
            onSend={handleSend}
            onAsk={ask}
            logRef={chatLogRef}
            variant="full"
            onAttach={handleAttach}
            onVoice={handleVoice}
            onDeepSearch={handleDeepSearch}
            onWebSearch={handleWebSearch}
            onSearchPriorities={handleSearchPriorities}
          />

          <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-line/60 pt-4 font-mono text-[0.58rem] tracking-[0.1em] text-dim uppercase">
            <span>FocusFlow AI · Planner</span>
            <div className="flex flex-wrap items-center gap-3">
              <Link to="/dashboard" className="transition hover:text-ink">
                Back to dashboard
              </Link>
              <span>All changes stay in this browser</span>
            </div>
          </div>
        </main>
      </div>

      <div
        role="status"
        aria-live="polite"
        className={cx(
          'ffd-toast fixed bottom-5 left-1/2 z-40 w-[92vw] max-w-[420px] -translate-x-1/2 rounded-xl border border-amber/30 bg-[#1b1a17] px-4 py-3 text-center text-[0.8rem] font-medium text-ink shadow-[0_22px_70px_-24px_rgba(0,0,0,0.9)]',
          toast ? 'translate-y-0 opacity-100' : 'pointer-events-none translate-y-2 opacity-0',
        )}
      >
        {toast}
      </div>
    </div>
  )
}
