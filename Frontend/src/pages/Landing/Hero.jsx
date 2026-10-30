import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'

const pad = (n) => String(n).padStart(2, '0')

function useCountdown() {
  // Fixed demo deadline so the countdown is stable across re-renders.
  const deadlineRef = useRef(null)
  if (deadlineRef.current === null) {
    deadlineRef.current = Date.now() + (18 * 3600 + 42 * 60) * 1000
  }

  const [label, setLabel] = useState('--:--:--')

  useEffect(() => {
    const tick = () => {
      const diff = Math.max(0, deadlineRef.current - Date.now())
      const h = Math.floor(diff / 3600000)
      const m = Math.floor((diff % 3600000) / 60000)
      const s = Math.floor((diff % 60000) / 1000)
      setLabel(`${pad(h)}:${pad(m)}:${pad(s)}`)
    }
    tick()
    const id = window.setInterval(tick, 1000)
    return () => window.clearInterval(id)
  }, [])

  return label
}

const stats = [
  { value: '4', label: 'signals watched at once, every day' },
  { value: '24/7', label: 'adaptive re-planning as things change' },
  { value: '100%', label: 'built from your real calendar' },
]

export default function Hero() {
  const countdown = useCountdown()

  return (
    <section className="pt-[48px] pb-12">
      <div className="mx-auto max-w-[820px] px-7">
        <div>
          <span className="inline-flex items-center gap-2 font-mono text-[0.72rem] tracking-[0.18em] text-amber uppercase">
            <span className="h-1.5 w-1.5 rounded-full bg-amber" />
            AI-powered productivity coach
          </span>

          <h1 className="mt-5 max-w-[13ch] text-[clamp(2.5rem,5vw,3.9rem)] leading-[1.02] font-bold tracking-[-0.02em] text-ink">
            Your week, run by something that&apos;s actually watching it
          </h1>

          <p className="mt-[22px] max-w-[44ch] text-[1.08rem] leading-relaxed text-dim">
            FocusFlow tracks every deadline, every free hour, and every habit that makes you
            late — then rebuilds your schedule the moment any of it changes.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3.5">
            <Link to="/signup" className="btn btn-primary">
              Start planning free
            </Link>
            <a href="#features" className="btn btn-ghost">
              See how it works
            </a>
            <span className="inline-flex items-baseline gap-2 rounded-[3px] border border-line px-3.5 py-2.5 text-[0.82rem] text-dim">
              Next deadline in
              <span className="font-mono text-[0.95rem] text-coral">{countdown}</span>
            </span>
          </div>

          <dl className="mt-11 grid max-w-lg grid-cols-3 gap-6 border-t border-line pt-6">
            {stats.map((stat) => (
              <div key={stat.label}>
                <dt className="font-mono text-xl text-ink sm:text-2xl">{stat.value}</dt>
                <dd className="mt-1.5 text-[0.72rem] leading-snug text-dim">{stat.label}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  )
}
