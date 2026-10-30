import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import SectionHeading from './SectionHeading.jsx'

const exchanges = [
  {
    q: 'Am I likely to finish everything?',
    a: 'Gets a confidence estimate with the exact blockers to fix now.',
  },
  {
    q: 'I feel overwhelmed.',
    a: 'Drops low-priority work from the schedule and re-plans around what matters.',
  },
  {
    q: 'Does finishing today buy me a free Saturday?',
    a: 'Surfaces the upside of finishing early, so the trade-off is obvious.',
  },
]

const planRows = [
  { title: 'Database Assignment', time: 'Today · 2 hrs', risk: 'high' },
  { title: 'Group Project Outline', time: 'Today · 1 hr', risk: 'medium' },
  { title: 'Essay Drafting', time: 'Tomorrow · 1.5 hrs', risk: 'low' },
]

const RISK_PILL = {
  high: 'bg-coral/15 text-coral',
  medium: 'bg-amber/15 text-amber',
  low: 'bg-cyan/15 text-cyan',
}

const EASE = [0.3, 0.8, 0.3, 1]

export default function AiShowcase() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.3 })

  return (
    <section id="ai" className="border-t border-line py-[84px]">
      <div className="mx-auto grid max-w-[1180px] items-center gap-14 px-7 lg:grid-cols-2">
        <div>
          <SectionHeading
            eyebrow="AI Assistant"
            title="Talk to your schedule like a coach"
            description="FocusFlow answers using your real deadlines, calendar events, task history and habits — not generic advice."
          />

          <ul className="mt-8 space-y-5">
            {exchanges.map((item, i) => (
              <motion.li
                key={item.q}
                initial={{ opacity: 0, y: 16 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.15 + i * 0.1, ease: 'easeOut' }}
                className="flex items-start gap-3"
              >
                <span className="mt-1.5 grid h-6 w-6 shrink-0 place-items-center rounded-full border border-cyan/40 text-[0.7rem] text-cyan">
                  ✓
                </span>
                <div>
                  <p className="font-medium text-ink">&ldquo;{item.q}&rdquo;</p>
                  <p className="mt-1 text-[0.86rem] leading-relaxed text-dim">{item.a}</p>
                </div>
              </motion.li>
            ))}
          </ul>
        </div>

        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 28 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, ease: EASE }}
          className="w-full overflow-hidden rounded-[4px] border border-line bg-surface"
        >
          <div className="flex items-center gap-3 border-b border-line px-5 py-4">
            <span className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-amber to-coral text-sm text-white">
              ✦
            </span>
            <div>
              <p className="text-sm font-semibold text-ink">FocusFlow Coach</p>
              <p className="font-mono text-[0.68rem] text-cyan">
                online · knows your deadlines
              </p>
            </div>
          </div>

          <div className="space-y-3 p-5">
            <div className="ml-auto max-w-[85%] rounded-[10px_10px_2px_10px] bg-gradient-to-r from-amber to-coral px-4 py-2.5 text-[0.85rem] font-medium text-white">
              I have 5 assignments due next week. What should I work on today?
            </div>
            <div className="max-w-[85%] rounded-[10px_10px_10px_2px] bg-deck px-4 py-2.5 text-[0.85rem]">
              You have ~9 hrs free before Friday. Here&apos;s your optimized plan:
            </div>

            <div className="space-y-3 rounded-[4px] border border-line p-4">
              {planRows.map((row, i) => (
                <motion.div
                  key={row.title}
                  initial={{ opacity: 0, x: -12 }}
                  animate={inView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.5, delay: 0.5 + i * 0.15, ease: 'easeOut' }}
                  className="flex items-center justify-between gap-3"
                >
                  <div className="min-w-0">
                    <p className="truncate text-[0.82rem] font-semibold text-ink">{row.title}</p>
                    <p className="font-mono text-[0.7rem] text-dim">{row.time}</p>
                  </div>
                  <span
                    className={`shrink-0 rounded-full px-2 py-0.5 font-mono text-[0.65rem] uppercase ${
                      RISK_PILL[row.risk]
                    }`}
                  >
                    {row.risk}
                  </span>
                </motion.div>
              ))}

              <div className="h-1.5 w-full overflow-hidden rounded-full bg-deck">
                <motion.div
                  initial={{ width: 0 }}
                  animate={inView ? { width: '72%' } : {}}
                  transition={{ duration: 1.2, delay: 1.1, ease: EASE }}
                  className="h-full rounded-full bg-cyan"
                />
              </div>
              <p className="font-mono text-[0.7rem] text-dim">
                72% confident you finish all 5 on time
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 border-t border-line px-5 py-3.5">
            <div className="flex-1 rounded-[3px] border border-line px-3.5 py-2.5 text-[0.8rem] text-dim">
              Ask about your schedule...
            </div>
            <span className="grid h-9 w-9 place-items-center rounded-[3px] bg-amber text-sm text-white">
              →
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
