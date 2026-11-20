import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'

const BARS = [30, 38, 34, 46, 42, 56, 50, 62, 58, 72, 66, 80, 74, 88]

const signals = [
  { label: 'Deadlines', dot: 'bg-highlight' },
  { label: 'Free time', dot: 'bg-mint' },
  { label: 'Habits', dot: 'bg-blush' },
  { label: 'Conflicts', dot: 'bg-periwinkle' },
]

function BrandMark({ tone = 'light' }) {
  return (
    <svg viewBox="0 0 30 20" className="h-5 w-[30px]" aria-hidden="true">
      <rect width="18" height="20" rx="5" fill={tone === 'light' ? '#E4F24F' : '#2F45FF'} />
      <rect x="21" width="9" height="20" rx="4.5" fill="currentColor" />
    </svg>
  )
}

function Logo({ tone = 'light' }) {
  const color = tone === 'light' ? 'text-white' : 'text-inkwell'
  return (
    <Link to="/" className={`inline-flex items-center gap-2.5 ${color}`} aria-label="FocusFlow home">
      <BrandMark tone={tone} />
      <span className="font-display text-[1.2rem] font-bold tracking-[-0.02em]">
        Focus<span className={tone === 'light' ? 'text-highlight' : 'text-cobalt'}>Flow</span>
      </span>
    </Link>
  )
}

function Collage() {
  return (
    <div className="relative mt-10 h-[300px]">
      <div className="absolute top-0 left-0 w-[56%] rounded-[26px] border border-white/25 bg-white/12 p-5 backdrop-blur-md">
        <p className="text-[1.15rem] font-semibold tracking-tight text-white">Performance</p>
        <p className="text-[0.72rem] text-white/65">Up 24% this week</p>
        <div className="mt-3 flex h-[92px] items-end gap-[3px]" aria-hidden="true">
          {BARS.map((height, index) => (
            <i
              key={index}
              className={`flex-1 rounded-[3px] ${index % 3 === 0 ? 'bg-periwinkle/85' : 'bg-blush/85'}`}
              style={{ height: `${height}%` }}
            />
          ))}
        </div>
      </div>

      <div className="absolute top-9 right-0 w-[50%] rounded-[26px] border border-white/35 bg-gradient-to-br from-blush to-[#ffb1c4] p-4 text-inkwell shadow-[0_24px_50px_-30px_rgba(0,0,0,0.6)]">
        <p className="text-[1rem] font-semibold tracking-[-0.01em]">Database assignment</p>
        <p className="mt-1 text-[0.74rem] leading-snug text-inkwell/70">
          Two focused hours today keep it on track.
        </p>
        <span className="mt-3 inline-block rounded-xl bg-inkwell px-3 py-1.5 text-[0.72rem] font-semibold text-white">
          Start now
        </span>
      </div>

      <div className="absolute bottom-1 left-[8%] w-[52%] rounded-[26px] border border-white/35 bg-gradient-to-br from-periwinkle to-lilac p-4 text-inkwell shadow-[0_24px_50px_-30px_rgba(0,0,0,0.5)]">
        <p className="text-[1rem] font-semibold tracking-[-0.01em]">Econ 204 reading</p>
        <p className="mt-1 text-[0.74rem] leading-snug text-inkwell/70">
          Best done in your morning slot.
        </p>
      </div>

      <div className="absolute right-[1%] -bottom-2 w-[46%] animate-float rounded-[22px] border border-white/25 bg-white/12 p-2.5 backdrop-blur-md">
        <div className="flex flex-col gap-1.5">
          <span className="self-end rounded-[14px] rounded-br-[4px] bg-white px-3 py-2 text-[0.7rem] leading-snug text-inkwell">
            Football tomorrow. Rearrange my week.
          </span>
          <span className="self-start rounded-[14px] rounded-bl-[4px] bg-white/15 px-3 py-2 text-[0.7rem] leading-snug text-white">
            Done. Reading moved to tonight.
          </span>
        </div>
      </div>
    </div>
  )
}

export default function AuthLayout({
  eyebrow,
  title,
  subtitle,
  footer,
  children,
  brandTitle = 'Your plan is waiting',
  brandLead = 'Log in to see what is due, what moved, and what to do next.',
}) {
  const headingRef = useRef(null)

  useEffect(() => {
    headingRef.current?.focus({ preventScroll: true })
  }, [title])

  return (
    <main className="auth-shell relative min-h-screen overflow-hidden bg-paper font-sans text-inkwell lg:grid lg:grid-cols-[1.05fr_1fr]">
      <aside className="on-cobalt relative hidden flex-col justify-between overflow-hidden bg-cobalt p-10 text-white lg:flex xl:p-14">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0">
          <div className="absolute -top-32 -left-24 h-[430px] w-[430px] rounded-full bg-blush/35 blur-[100px]" />
          <div className="absolute -right-28 -bottom-40 h-[460px] w-[460px] rounded-full bg-lilac/45 blur-[110px]" />
          <div className="absolute top-1/2 left-1/3 h-[320px] w-[320px] rounded-full bg-highlight/15 blur-[100px]" />
        </div>

        <div className="relative flex items-center justify-between">
          <Logo />
          <span className="rounded-full border border-white/25 bg-white/10 px-3 py-1 text-[0.62rem] font-semibold tracking-[0.14em] text-white/85 uppercase">
            AI planner
          </span>
        </div>

        <div className="relative max-w-[30rem]">
          <p className="display font-display text-[clamp(2.4rem,3.6vw,3.4rem)] text-balance">
            {brandTitle}
          </p>
          <p className="mt-5 max-w-[38ch] text-[0.98rem] leading-relaxed text-white/80">{brandLead}</p>
          <div className="hidden [@media(min-height:800px)]:block">
            <Collage />
          </div>
        </div>

        <div className="relative flex flex-wrap items-center gap-x-5 gap-y-2 text-[0.62rem] font-semibold tracking-[0.14em] text-white/70 uppercase">
          {signals.map((signal) => (
            <span key={signal.label} className="inline-flex items-center gap-2">
              <i className={`h-1.5 w-1.5 rounded-full ${signal.dot}`} />
              {signal.label}
            </span>
          ))}
        </div>
      </aside>

      <section className="relative flex min-h-screen flex-col px-5 py-7 sm:px-8 lg:px-10">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -top-24 -right-20 h-[420px] w-[420px] rounded-full bg-blush/25 blur-3xl" />
          <div className="absolute -bottom-40 -left-24 h-[420px] w-[420px] rounded-full bg-periwinkle/35 blur-3xl" />
        </div>

        <div className="relative lg:hidden">
          <Logo tone="dark" />
        </div>

        <div className="relative flex flex-1 items-center justify-center py-8 sm:py-12">
          <div className="w-full max-w-[27rem]">
            <div className="mb-6">
              {eyebrow && (
                <p className="inline-flex items-center rounded-full border border-cobalt/15 bg-cobalt/5 px-3 py-1 text-[0.66rem] font-semibold tracking-[0.14em] text-cobalt uppercase">
                  {eyebrow}
                </p>
              )}
              <h1
                ref={headingRef}
                tabIndex={-1}
                className="mt-3 font-display text-[2.1rem] leading-[1.05] font-bold tracking-[-0.02em] outline-none"
              >
                {title}
              </h1>
              {subtitle && <p className="mt-2.5 text-[0.92rem] leading-relaxed text-inkwell/65">{subtitle}</p>}
            </div>

            <div className="relative rounded-[28px] border border-white/80 bg-white/80 p-6 shadow-[0_30px_80px_-42px_rgba(16,27,59,0.45)] backdrop-blur-xl sm:p-8">
              {children}
            </div>

            {footer && <p className="mt-6 text-[0.86rem] text-inkwell/65">{footer}</p>}
            <p className="mt-5 text-[0.7rem] text-inkwell/40">
              Preview build · accounts stay in this browser.
            </p>
          </div>
        </div>
      </section>
    </main>
  )
}
