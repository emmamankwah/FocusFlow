import { useEffect, useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'
import SectionHeading from './SectionHeading.jsx'

const BAR_DATA = [
  { day: 'Mon', value: 35 },
  { day: 'Tue', value: 58 },
  { day: 'Wed', value: 88, peak: true },
  { day: 'Thu', value: 42 },
  { day: 'Fri', value: 70 },
  { day: 'Sat', value: 20 },
  { day: 'Sun', value: 12 },
]

const RISK_PCT = 82
const RING_CIRCUMFERENCE = 175.9
const EASE = [0.3, 0.8, 0.3, 1]

function useReducedMotion() {
  const [reduced, setReduced] = useState(false)
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReduced(mq.matches)
    const onChange = (e) => setReduced(e.matches)
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])
  return reduced
}

function useCountUp(target, active, duration = 1100) {
  const reduced = useReducedMotion()
  const [value, setValue] = useState(0)

  useEffect(() => {
    if (!active) return
    if (reduced) {
      setValue(target)
      return
    }
    let raf
    let start
    const step = (ts) => {
      if (!start) start = ts
      const p = Math.min((ts - start) / duration, 1)
      setValue(Math.round(p * target))
      if (p < 1) raf = requestAnimationFrame(step)
    }
    raf = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf)
  }, [active, target, duration, reduced])

  return value
}

const tileClass = 'rounded-[4px] border border-line bg-surface p-6'

function ChartTile() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.4 })

  return (
    <div ref={ref} className={`${tileClass} md:row-span-2`}>
      <h3 className="mb-1.5 text-base font-semibold">Your week, at a glance</h3>
      <p className="mb-4 text-[0.85rem] leading-normal text-dim">
        Focus time by day, so you can see what&apos;s actually working — not just what&apos;s
        scheduled.
      </p>

      <div className="flex h-[140px] items-end gap-2.5">
        {BAR_DATA.map((bar, i) => (
          <div key={bar.day} className="flex h-full flex-1 flex-col items-center justify-end gap-2">
            <motion.div
              initial={{ height: 0 }}
              animate={inView ? { height: `${bar.value}%` } : { height: 0 }}
              transition={{ duration: 1, delay: i * 0.05, ease: EASE }}
              className={`w-full rounded-t-[2px] ${bar.peak ? 'bg-amber' : 'bg-cyan'}`}
            />
            <span className="text-[0.66rem] text-dim">{bar.day}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function RiskTile() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.4 })
  const label = useCountUp(RISK_PCT, inView)

  return (
    <div ref={ref} className={tileClass}>
      <h3 className="mb-1.5 text-base font-semibold">Odds before it&apos;s too late</h3>
      <p className="mb-4 text-[0.85rem] leading-normal text-dim">
        A live estimate of finishing on time — and what closes the gap.
      </p>

      <div className="flex items-center gap-4">
        <div className="relative h-16 w-16 flex-shrink-0">
          <svg viewBox="0 0 64 64" width="64" height="64" className="-rotate-90">
            <circle
              cx="32"
              cy="32"
              r="28"
              fill="none"
              strokeWidth="5"
              className="stroke-deck"
            />
            <motion.circle
              cx="32"
              cy="32"
              r="28"
              fill="none"
              strokeWidth="5"
              strokeLinecap="round"
              className="stroke-coral"
              strokeDasharray={RING_CIRCUMFERENCE}
              initial={{ strokeDashoffset: RING_CIRCUMFERENCE }}
              animate={{
                strokeDashoffset: inView
                  ? RING_CIRCUMFERENCE * (1 - RISK_PCT / 100)
                  : RING_CIRCUMFERENCE,
              }}
              transition={{ duration: 1.1, ease: EASE }}
            />
          </svg>
          <span className="absolute inset-0 flex items-center justify-center text-[0.85rem] font-semibold text-coral">
            {label}%
          </span>
        </div>
        <p className="text-[0.82rem] leading-normal text-dim">
          chance of missing{' '}
          <b className="font-semibold text-ink">Database assignment</b> without two hours today.
        </p>
      </div>
    </div>
  )
}

function ChatTile() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.4 })
  const reduced = useReducedMotion()
  const [showReply, setShowReply] = useState(false)

  useEffect(() => {
    if (!inView) return
    const id = window.setTimeout(() => setShowReply(true), reduced ? 0 : 1300)
    return () => window.clearTimeout(id)
  }, [inView, reduced])

  return (
    <div ref={ref} className={tileClass}>
      <h3 className="mb-1.5 text-base font-semibold">Ask it directly</h3>
      <p className="mb-4 text-[0.85rem] leading-normal text-dim">
        Plain questions, answered from your real calendar.
      </p>

      <div className="max-w-[90%] rounded-[10px_10px_10px_2px] bg-deck px-3.5 py-3 text-[0.85rem]">
        &ldquo;I have football tomorrow — rearrange my week.&rdquo;
      </div>

      <div className="mt-2.5 h-5" aria-hidden={showReply}>
        <span className={`inline-flex gap-1 ${showReply ? 'hidden' : 'inline-flex'}`}>
          {[0, 0.15, 0.3].map((delay) => (
            <i
              key={delay}
              className="h-[5px] w-[5px] animate-typing rounded-full bg-dim"
              style={{ animationDelay: `${delay}s` }}
            />
          ))}
        </span>
      </div>

      <div
        className={`mt-2 max-w-[90%] rounded-[10px_10px_10px_2px] bg-deck px-3.5 py-3 text-[0.85rem] transition-opacity duration-[400ms] ${
          showReply ? 'opacity-100' : 'opacity-0'
        }`}
      >
        Moved Thursday&apos;s reading to tonight, kept Friday clear.
      </div>
    </div>
  )
}

function OverloadTile() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.4 })

  return (
    <div ref={ref} className={tileClass}>
      <h3 className="mb-1.5 text-base font-semibold">Catches overload early</h3>
      <p className="mb-4 text-[0.85rem] leading-normal text-dim">
        This week compared with your normal pace.
      </p>

      <div className="h-2 overflow-hidden rounded-[4px] bg-deck">
        <motion.div
          initial={{ width: 0 }}
          animate={inView ? { width: '78%' } : { width: 0 }}
          transition={{ duration: 1.1, ease: EASE }}
          className="h-full bg-gradient-to-r from-cyan to-coral"
        />
      </div>
      <div className="mt-1.5 flex justify-between text-[0.7rem] text-dim">
        <span>Usual load</span>
        <span>This week</span>
      </div>
    </div>
  )
}

export default function Features() {
  return (
    <section id="features" className="border-t border-line pt-8 pb-12">
      <div className="mx-auto max-w-[1180px] px-7">
        <div className="mb-9">
          <SectionHeading
            eyebrow="Features"
            title="What it does with that"
            description="Live widgets, not static plans — every tile below is rebuilt from your real week."
          />
        </div>

        <div className="grid gap-4 md:grid-cols-[1.3fr_1fr]">
          <ChartTile />
          <RiskTile />
          <ChatTile />
          <OverloadTile />
        </div>
      </div>
    </section>
  )
}
