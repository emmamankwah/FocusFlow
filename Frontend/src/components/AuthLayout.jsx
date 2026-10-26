import { Link } from 'react-router-dom'

const planRows = [
  { time: '09:30', title: 'Database assignment', risk: 'high' },
  { time: '13:00', title: 'Group project outline', risk: 'medium' },
  { time: '17:30', title: 'Essay drafting', risk: 'low' },
]

const RISK_PILL = {
  high: 'bg-coral/15 text-coral',
  medium: 'bg-amber/15 text-amber',
  low: 'bg-cyan/15 text-cyan',
}

const signals = [
  { label: 'Deadlines', dot: 'bg-amber' },
  { label: 'Free time', dot: 'bg-cyan' },
  { label: 'Habits', dot: 'bg-coral' },
  { label: 'Conflicts', dot: 'bg-dim' },
]

function BrandMark() {
  return (
    <span
      aria-hidden
      className="grid h-8 w-8 shrink-0 grid-cols-2 place-items-center gap-[3px] rounded-[10px] bg-amber shadow-[0_10px_30px_-10px_rgba(242,184,75,0.9)]"
    >
      <i className="h-[5px] w-[5px] rounded-full bg-[#171205]" />
      <i className="h-[5px] w-[5px] rounded-full bg-[#171205]/50" />
      <i className="h-[5px] w-[5px] rounded-full bg-[#171205]/50" />
      <i className="h-[5px] w-[5px] rounded-full bg-[#171205]" />
    </span>
  )
}

function Logo() {
  return (
    <Link to="/" className="inline-flex items-center gap-2.5">
      <BrandMark />
      <span className="text-[1.05rem] font-bold tracking-[-0.01em] text-ink">
        Focus<span className="text-amber">Flow</span>
      </span>
    </Link>
  )
}

function PlanPreview() {
  return (
    <div className="mt-9 hidden [@media(min-height:820px)]:block">
      <div className="rounded-2xl border border-line/80 bg-surface/75 p-5 shadow-[0_30px_80px_-40px_rgba(0,0,0,0.95)] backdrop-blur-md">
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <i className="h-1.5 w-1.5 animate-pulse-soft rounded-full bg-cyan" />
            <span className="font-mono text-[0.62rem] tracking-[0.16em] text-dim uppercase">
              Today · rebuilt 2m ago
            </span>
          </span>
          <span className="rounded-full border border-line px-2 py-0.5 font-mono text-[0.58rem] tracking-[0.14em] text-dim uppercase">
            Live
          </span>
        </div>

        <div className="mt-4 space-y-2.5">
          {planRows.map((row) => (
            <div
              key={row.title}
              className="flex items-center gap-3 rounded-xl border border-line/60 bg-canvas/50 px-3 py-2.5"
            >
              <span className="font-mono text-[0.66rem] text-dim">{row.time}</span>
              <span className="min-w-0 flex-1 truncate text-[0.8rem] font-medium text-ink/90">
                {row.title}
              </span>
              <span
                className={`shrink-0 rounded-full px-2 py-0.5 font-mono text-[0.56rem] tracking-wide uppercase ${RISK_PILL[row.risk]}`}
              >
                {row.risk}
              </span>
            </div>
          ))}
        </div>

        <div className="mt-5">
          <div className="h-1.5 overflow-hidden rounded-full bg-deck">
            <div className="h-full w-[72%] rounded-full bg-gradient-to-r from-cyan via-amber to-coral" />
          </div>
          <div className="mt-2 flex items-center justify-between font-mono text-[0.6rem] text-dim">
            <span>72% confident you finish on time</span>
            <span>5 tasks due</span>
          </div>
        </div>
      </div>

      <div className="relative z-10 -mt-4 ml-10 animate-float rounded-2xl border border-amber/25 bg-[#1b1a17] px-4 py-3 shadow-[0_20px_50px_-20px_rgba(0,0,0,0.9)]">
        <p className="flex gap-2 text-[0.78rem] leading-snug text-ink/90">
          <span className="text-amber">✦</span>
          Start Database now — finishing it tonight buys you a free Friday.
        </p>
      </div>
    </div>
  )
}

export default function AuthLayout({ eyebrow, title, subtitle, onSubmit, footer, children }) {
  return (
    <main className="relative min-h-screen overflow-hidden bg-canvas font-grotesk text-ink lg:grid lg:grid-cols-[1.05fr_1fr]">
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -left-32 h-[520px] w-[520px] rounded-full bg-amber/10 blur-3xl" />
        <div className="absolute right-[-160px] bottom-[-180px] h-[520px] w-[520px] rounded-full bg-coral/10 blur-3xl" />
        <div className="absolute top-1/3 left-1/2 h-[360px] w-[360px] -translate-x-1/2 rounded-full bg-cyan/10 blur-3xl" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(38,44,60,0.35)_1px,transparent_1px),linear-gradient(to_bottom,rgba(38,44,60,0.35)_1px,transparent_1px)] bg-[size:48px_48px] [mask-image:radial-gradient(ellipse_at_center,black,transparent_78%)]" />
      </div>

      <aside className="relative hidden flex-col justify-between overflow-hidden border-r border-line/60 p-10 lg:flex xl:p-14">
        <div className="flex items-center justify-between">
          <Logo />
          <span className="rounded-full border border-line px-3 py-1 font-mono text-[0.6rem] tracking-[0.16em] text-dim uppercase">
            AI planner
          </span>
        </div>

        <div className="max-w-[30rem]">
          <p className="font-mono text-[0.68rem] tracking-[0.2em] text-amber uppercase">
            The week, under control
          </p>
          <h2 className="mt-4 text-[clamp(2.1rem,3.4vw,3rem)] leading-[1.04] font-bold tracking-[-0.02em]">
            Your week,{' '}
            <span className="animate-gradient-x bg-gradient-to-r from-amber via-coral to-amber bg-[length:220%_100%] bg-clip-text text-transparent">
              already planned
            </span>
            .
          </h2>
          <p className="mt-4 max-w-[40ch] text-[0.95rem] leading-relaxed text-dim">
            FocusFlow reads your deadlines, free hours, habits and conflicts — then rebuilds
            today the moment anything changes.
          </p>
          <PlanPreview />
        </div>

        <div className="flex flex-wrap items-center gap-x-5 gap-y-2 font-mono text-[0.62rem] tracking-[0.14em] text-dim uppercase">
          {signals.map((signal) => (
            <span key={signal.label} className="inline-flex items-center gap-2">
              <i className={`h-1.5 w-1.5 rounded-full ${signal.dot}`} />
              {signal.label}
            </span>
          ))}
        </div>
      </aside>

      <section className="relative flex min-h-screen flex-col px-5 py-7 sm:px-8 lg:px-10">
        <div className="lg:hidden">
          <Logo />
        </div>

        <div className="flex flex-1 items-center justify-center py-8 sm:py-12">
          <div className="w-full max-w-[26rem]">
            <div className="mb-7">
              {eyebrow && (
                <p className="font-mono text-[0.66rem] tracking-[0.2em] text-amber uppercase">
                  {eyebrow}
                </p>
              )}
              <h1 className="mt-2 text-[2rem] leading-[1.1] font-bold tracking-[-0.02em]">
                {title}
              </h1>
              {subtitle && <p className="mt-2.5 text-[0.92rem] text-dim">{subtitle}</p>}
            </div>

            <form
              onSubmit={onSubmit}
              className="relative space-y-4 overflow-hidden rounded-[24px] border border-line/80 bg-surface/80 p-6 shadow-[0_30px_90px_-40px_rgba(0,0,0,0.95)] backdrop-blur-xl sm:p-8"
            >
              <span
                aria-hidden
                className="absolute inset-x-10 top-0 h-px bg-gradient-to-r from-transparent via-amber/70 to-transparent"
              />
              {children}
            </form>

            {footer && <p className="mt-6 text-[0.86rem] text-dim">{footer}</p>}
          </div>
        </div>
      </section>
    </main>
  )
}
