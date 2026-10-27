import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import usePageTitle from '@/lib/usePageTitle'
import './dashboard.css'
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
  riskStyles,
  saveBoard,
  sections,
} from './data.js'
import {
  BrandMark,
  BTN,
  BTN_PRIMARY,
  MenuIcon,
  SectionLabel,
  SparkIcon,
  StatCard,
  cx,
} from './ui.jsx'
import { FocusSection, PlanSection } from './FocusPlan.jsx'
import {
  DeadlinesSection,
  ProgressSection,
  SuggestionsSection,
  WellbeingSection,
} from './Insights.jsx'
import { ChatSection, NotificationsSection } from './ChatNotes.jsx'

const INITIAL_CHAT = [
  {
    role: 'ai',
    text: 'Hi Ama. Ask me what to focus on next, why a deadline is risky, or whether your workload is too heavy.',
  },
]

function prefersReducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

function UserCard() {
  return (
    <div className="flex items-center gap-2.5 rounded-xl border border-line/80 bg-surface/70 p-2.5 lg:w-full">
      <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full border border-amber/30 bg-amber/10 font-grotesk text-[0.7rem] font-bold text-amber">
        AM
      </span>
      <span className="min-w-0">
        <span className="block truncate text-[0.78rem] font-semibold text-ink">Ama Mensah</span>
        <span className="block font-mono text-[0.54rem] tracking-[0.14em] text-dim uppercase">
          Student
        </span>
      </span>
    </div>
  )
}

function DashboardRail({ active, onNav, unread }) {
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

  function handleNav(id) {
    setMenuOpen(false)
    requestAnimationFrame(() => onNav(id))
  }

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
            aria-controls="ff-dashboard-menu"
            aria-label={menuOpen ? 'Close dashboard menu' : 'Open dashboard menu'}
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-[3px] border border-line bg-surface text-ink transition duration-150 hover:border-dim focus-visible:ring-2 focus-visible:ring-amber/35 focus-visible:ring-offset-2 focus-visible:ring-offset-canvas focus-visible:outline-none lg:hidden"
          >
            <MenuIcon open={menuOpen} className="h-4 w-4" />
          </button>
        </div>

        <div
          id="ff-dashboard-menu"
          ref={menuRef}
          className={cx(
            'ffd-menu absolute top-full right-0 z-30 mt-2 max-h-[calc(100vh-6rem)] w-[min(280px,calc(100vw-2rem))] overflow-y-auto rounded-2xl border border-line/80 bg-surface p-2 shadow-[0_24px_70px_-30px_rgba(0,0,0,0.95)] lg:static lg:mt-0 lg:w-full lg:overflow-visible lg:rounded-none lg:border-0 lg:bg-transparent lg:p-0 lg:shadow-none lg:contents',
            menuOpen ? 'block' : 'hidden',
          )}
        >
          <nav
            aria-label="Dashboard sections"
            className="ff-nav ffd-nav-scroll grid w-full gap-1 lg:flex lg:flex-col"
          >
            {sections.map((section) => {
              const isActive = active === section.id
              return (
                <button
                  key={section.id}
                  type="button"
                  onClick={() => handleNav(section.id)}
                  aria-current={isActive ? 'true' : undefined}
                  className={cx(
                    'flex min-h-9 shrink-0 items-center justify-between gap-2 rounded-lg border-l-2 px-3 py-2 text-left font-mono text-[0.63rem] tracking-[0.13em] uppercase transition lg:w-full',
                    isActive
                      ? 'border-amber bg-amber/10 text-amber'
                      : 'border-transparent text-dim hover:bg-deck/60 hover:text-ink',
                  )}
                >
                  <span>{section.label}</span>
                  {section.id === 'sec-notes' && unread > 0 && (
                    <span
                      className="rounded-full bg-amber px-1.5 py-0.5 font-mono text-[0.56rem] font-semibold tracking-normal text-[#171205]"
                      aria-label={`${unread} unread notifications`}
                    >
                      {unread}
                    </span>
                  )}
                </button>
              )
            })}
          </nav>

          <div className="mt-2 border-t border-line/60 px-1 pt-3 pb-1 lg:hidden">
            <UserCard />
          </div>
        </div>

        <div className="hidden lg:block">
          <UserCard />
        </div>
      </div>
    </aside>
  )
}

function DeadlineStat({ risk }) {
  const tone = riskStyles[risk.level]
  return (
    <div className="ff-stat rounded-2xl border border-line/80 bg-surface/80 p-4 shadow-[0_24px_70px_-50px_rgba(0,0,0,0.95)]">
      <SectionLabel>Next deadline</SectionLabel>
      <div className="mt-1.5 font-grotesk text-[1.02rem] leading-tight font-bold tracking-[-0.01em] text-ink">
        {risk.n}
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-2">
        <span
          className={cx(
            'inline-flex rounded-[3px] border px-1.5 py-0.5 font-mono text-[0.54rem] tracking-[0.08em] uppercase',
            tone.pill,
          )}
        >
          {risk.label}
        </span>
        <span className="font-mono text-[0.62rem] text-dim">
          {risk.due} · {risk.p}%
        </span>
      </div>
    </div>
  )
}

export default function Dashboard() {
  usePageTitle('Dashboard — FocusFlow')

  const today = useMemo(() => new Date(), [])
  const [board, setBoard] = useState(() => loadBoard(today))
  const [active, setActive] = useState('sec-focus')
  const [toast, setToast] = useState('')
  const toastTimer = useRef(null)
  const navLockRef = useRef(0)

  const [addOpen, setAddOpen] = useState(false)
  const [form, setForm] = useState({ title: '', time: '16:00', duration: '45', type: 'focus' })
  const [formError, setFormError] = useState('')
  const titleRef = useRef(null)
  const planRef = useRef(null)

  const [durationMin, setDurationMin] = useState(45)
  const [remainSec, setRemainSec] = useState(45 * 60)
  const [running, setRunning] = useState(false)
  const remainRef = useRef(remainSec)
  const sessionTaskRef = useRef(null)

  const [chat, setChat] = useState(INITIAL_CHAT)
  const [chatInput, setChatInput] = useState('')
  const chatTimer = useRef(null)
  const chatLogRef = useRef(null)

  const suggestions = useMemo(() => makeSuggestions(today), [today])
  const notes = useMemo(() => makeNotes(today), [today])
  const risks = useMemo(() => getRisks(today, board.sugs), [today, board.sugs])
  const chart = useMemo(() => getChartData(today), [today])

  const allTasks = useMemo(
    () =>
      [...baseTasks, ...board.custom].sort((a, b) => a.t.localeCompare(b.t)),
    [board.custom],
  )
  const nextTask = allTasks.find((task) => !board.done[task.id]) ?? null
  const heroTask =
    allTasks.find((task) => task.type === 'focus' && !board.done[task.id]) ?? null
  const doneCount = allTasks.filter((task) => board.done[task.id]).length
  const undoneCount = allTasks.length - doneCount
  const focusMinutes =
    board.extraMin +
    allTasks
      .filter((task) => task.type === 'focus' && board.done[task.id] && !board.timed[task.id])
      .reduce((sum, task) => sum + task.dur, 0)
  const focusHours = focusMinutes / 60
  const focusPct = Math.min(100, (focusMinutes / (FOCUS_GOAL_HOURS * 60)) * 100)
  const planPct = allTasks.length ? (doneCount / allTasks.length) * 100 : 0
  const score = board.sugs.s2 === 'done' ? 33 : 41
  const unread = notes.filter((note) => !board.read[note.id]).length
  const chartTotal = chart.reduce((sum, day) => sum + day.hours, 0)
  const chartAverage = chartTotal / chart.length

  const showToast = useCallback((message) => {
    setToast(message)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(''), 2800)
  }, [])

  useEffect(() => {
    saveBoard(board, today)
  }, [board, today])

  useEffect(() => () => clearTimeout(toastTimer.current), [])

  useEffect(() => {
    remainRef.current = remainSec
  }, [remainSec])

  useEffect(() => {
    if (!addOpen) return
    setFormError('')
    titleRef.current?.focus()
  }, [addOpen])

  useEffect(() => {
    const el = chatLogRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [chat])

  useEffect(() => () => clearTimeout(chatTimer.current), [])

  const scrollToSection = useCallback((id) => {
    const el = document.getElementById(id)
    if (!el) return
    el.scrollIntoView({
      behavior: prefersReducedMotion() ? 'auto' : 'smooth',
      block: 'start',
    })
  }, [])

  useEffect(() => {
    const updateActive = () => {
      if (Date.now() < navLockRef.current) return
      if (
        window.innerHeight + window.scrollY >=
        document.documentElement.scrollHeight - 8
      ) {
        setActive(sections[sections.length - 1].id)
        return
      }
      const probe = window.scrollY + 160
      let current = sections[0].id
      sections.forEach((section) => {
        const el = document.getElementById(section.id)
        if (!el) return
        if (el.getBoundingClientRect().top + window.scrollY <= probe) {
          current = section.id
        }
      })
      setActive(current)
    }

    updateActive()
    window.addEventListener('scroll', updateActive, { passive: true })
    return () => window.removeEventListener('scroll', updateActive)
  }, [])

  const completeSession = useCallback(() => {
    const taskId = sessionTaskRef.current
    const task = allTasks.find((item) => item.id === taskId)
    setBoard((prev) => {
      const next = { ...prev, extraMin: prev.extraMin + durationMin }
      if (task) {
        next.timed = { ...prev.timed, [task.id]: true }
        if (durationMin >= task.dur) {
          next.done = { ...prev.done, [task.id]: true }
        }
      }
      return next
    })
    setRunning(false)
    setRemainSec(0)
    remainRef.current = 0
    sessionTaskRef.current = null
    showToast('Session complete. Take a 5 minute break.')
  }, [allTasks, durationMin, showToast])

  useEffect(() => {
    if (!running) return undefined
    const id = setInterval(() => {
      const next = Math.max(0, remainRef.current - 1)
      remainRef.current = next
      setRemainSec(next)
      if (next === 0) {
        clearInterval(id)
        completeSession()
      }
    }, 1000)
    return () => clearInterval(id)
  }, [running, completeSession])

  function handleStartPause() {
    if (running) {
      setRunning(false)
      return
    }
    const startingFresh = remainSec === 0 || remainSec === durationMin * 60
    if (remainSec === 0) {
      setRemainSec(durationMin * 60)
      remainRef.current = durationMin * 60
    }
    if (startingFresh) sessionTaskRef.current = heroTask?.id ?? null
    setRunning(true)
  }

  function resetTimer() {
    setRunning(false)
    setRemainSec(durationMin * 60)
    remainRef.current = durationMin * 60
    sessionTaskRef.current = null
  }

  function chooseDuration(minutes) {
    setRunning(false)
    setDurationMin(minutes)
    setRemainSec(minutes * 60)
    remainRef.current = minutes * 60
    sessionTaskRef.current = null
  }

  function handleToggle(taskId) {
    setBoard((prev) => ({
      ...prev,
      done: { ...prev.done, [taskId]: !prev.done[taskId] },
    }))
  }

  function handleRemove(taskId) {
    setBoard((prev) => {
      const done = { ...prev.done }
      const timed = { ...prev.timed }
      delete done[taskId]
      delete timed[taskId]
      return {
        ...prev,
        custom: prev.custom.filter((task) => task.id !== taskId),
        done,
        timed,
      }
    })
    showToast('Task removed from today’s plan.')
  }

  function handleAdd(event) {
    event.preventDefault()
    const title = form.title.trim()
    if (!title) {
      setFormError('Give the block a name.')
      titleRef.current?.focus()
      return
    }
    if (!form.time) {
      setFormError('Choose a start time.')
      return
    }

    const createdTask = {
      id: `c${Date.now()}`,
      t: form.time,
      dur: Number(form.duration),
      title,
      meta: 'Added by you',
      type: form.type,
      custom: true,
    }
    setBoard((prev) => ({ ...prev, custom: [...prev.custom, createdTask] }))
    setForm((prev) => ({ ...prev, title: '' }))
    setFormError('')
    showToast('Task added to today’s plan.')
    titleRef.current?.focus()
  }

  function handleFormChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
    if (formError) setFormError('')
  }

  function toggleAddForm() {
    const next = !addOpen
    setAddOpen(next)
    if (!next) setFormError('')
  }

  function handleSuggestion(id, decision) {
    const item = suggestions.find((suggestion) => suggestion.id === id)
    setBoard((prev) => ({
      ...prev,
      sugs: { ...prev.sugs, [id]: decision },
    }))
    showToast(
      decision === 'done'
        ? item?.ok || 'Added to your plan.'
        : 'Noted. I’ll only bring this back if things change.',
    )
  }

  function markRead(id) {
    setBoard((prev) => ({ ...prev, read: { ...prev.read, [id]: true } }))
  }

  function markAllRead() {
    setBoard((prev) => ({
      ...prev,
      read: Object.fromEntries(notes.map((note) => [note.id, true])),
    }))
  }

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
        setChat((prev) => [
          ...prev,
          { role: 'ai', text: chatReply(question, context) },
        ])
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

  function replan() {
    showToast('Week re-planned. Review the suggestions.')
    navLockRef.current = Date.now() + 1200
    setActive('sec-ai')
    scrollToSection('sec-ai')
    ask('Re-plan my week')
  }

  function handleNav(id) {
    navLockRef.current = Date.now() + 1200
    setActive(id)
    scrollToSection(id)
  }

  const nextCopy = nextTask
    ? `Next up: ${nextTask.t} · ${nextTask.title}.`
    : 'Everything planned is done. Protect the rest of the evening.'

  return (
    <div
      id="dashboard"
      className="ff-dashboard ff-app relative min-h-screen bg-canvas font-sans text-ink"
    >
      <div aria-hidden="true" className="pointer-events-none fixed inset-0">
        <div className="absolute -top-40 -left-32 h-[520px] w-[520px] rounded-full bg-amber/[0.06] blur-3xl" />
        <div className="absolute top-1/4 -right-40 h-[420px] w-[420px] rounded-full bg-cyan/[0.04] blur-3xl" />
        <div className="absolute bottom-[-160px] left-1/3 h-[420px] w-[420px] rounded-full bg-coral/[0.04] blur-3xl" />
        <div className="ffd-grid-bg absolute inset-0" />
      </div>

      <div className="relative mx-auto w-full max-w-[1320px] px-4 py-6 sm:px-6 lg:grid lg:grid-cols-[200px_minmax(0,1fr)] lg:items-start lg:gap-8 lg:px-8 lg:py-8">
        <DashboardRail active={active} onNav={handleNav} unread={unread} />

        <main className="ff-main mt-5 min-w-0 lg:mt-0">
          <div className="ff-top flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <SectionLabel className="text-amber/85">{fmtLongDate(today)}</SectionLabel>
              <h1 className="mt-2 font-grotesk text-[1.65rem] leading-tight font-bold tracking-[-0.03em] text-ink sm:text-[1.9rem]">
                {greeting(today)}
              </h1>
              <p className="mt-1 max-w-xl text-[0.82rem] leading-relaxed text-dim">
                {nextCopy}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button type="button" onClick={replan} className={cx(BTN, 'ff-btn')}>
                <SparkIcon className="h-3.5 w-3.5" />
                Re-plan my week
              </button>
              <button
                type="button"
                onClick={toggleAddForm}
                className={cx(BTN_PRIMARY, 'ff-btn')}
                aria-expanded={addOpen}
                aria-controls="ff-addform"
              >
                Add task
              </button>
            </div>
          </div>

          <div className="ff-stats mt-5 grid gap-4 sm:grid-cols-3">
            <StatCard
              label="Focus today"
              meter={focusPct}
              note={`${Math.round(focusPct)}% of the ${FOCUS_GOAL_HOURS} h daily goal`}
            >
              {focusHours.toFixed(1)}
              <small className="ml-1 font-sans text-[0.72rem] font-semibold text-dim">h</small>
            </StatCard>

            <StatCard
              label="Today’s plan"
              meter={planPct}
              note={undoneCount === 0 ? 'All blocks done' : `${undoneCount} blocks left`}
            >
              {doneCount}
              <small className="ml-1 font-sans text-[0.72rem] font-semibold text-dim">
                of {allTasks.length} done
              </small>
            </StatCard>

            <DeadlineStat risk={risks[0]} />
          </div>

          <div className="ff-grid mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
            <div className="space-y-5">
              <FocusSection
                heroTask={heroTask}
                durationMin={durationMin}
                remainSec={remainSec}
                running={running}
                onDuration={chooseDuration}
                onStartPause={handleStartPause}
                onReset={resetTimer}
              />
              <PlanSection
                tasks={allTasks}
                done={board.done}
                nextId={nextTask?.id}
                addOpen={addOpen}
                form={form}
                onFormChange={handleFormChange}
                onAdd={handleAdd}
                formError={formError}
                onToggle={handleToggle}
                onRemove={handleRemove}
                titleRef={titleRef}
                sectionRef={planRef}
              />
            </div>

            <div className="space-y-5">
              <SuggestionsSection
                suggestions={suggestions}
                sugs={board.sugs}
                onSuggestion={handleSuggestion}
              />
              <DeadlinesSection risks={risks} />
            </div>
          </div>

          <div className="ff-grid mt-5 grid gap-5 xl:grid-cols-2">
            <WellbeingSection score={score} restPlanned={board.sugs.s2 === 'done'} />
            <ProgressSection chart={chart} total={chartTotal} average={chartAverage} />
          </div>

          <div className="ff-grid mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
            <ChatSection
              messages={chat}
              chatInput={chatInput}
              onChatInput={setChatInput}
              onSend={handleSend}
              onAsk={ask}
              logRef={chatLogRef}
            />
            <NotificationsSection
              notes={notes}
              read={board.read}
              unread={unread}
              onRead={markRead}
              onMarkAll={markAllRead}
            />
          </div>

          <footer className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-line/60 pt-4 font-mono text-[0.58rem] tracking-[0.1em] text-dim uppercase">
            <span>FocusFlow · Local dashboard demo</span>
            <span>All changes stay in this browser</span>
          </footer>
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
