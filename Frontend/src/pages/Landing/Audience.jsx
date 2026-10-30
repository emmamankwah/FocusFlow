import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import SectionHeading from './SectionHeading.jsx'

const audiences = [
  {
    emoji: '🎓',
    title: 'Students',
    desc: 'University, college & high-school — tame exams, essays and group projects.',
    accent: 'bg-amber',
  },
  {
    emoji: '💻',
    title: 'Developers',
    desc: 'Ship features on time across repos, tickets, sprints and side projects.',
    accent: 'bg-cyan',
  },
  {
    emoji: '🏠',
    title: 'Remote workers',
    desc: 'Structure flexible hours with a coach that adapts to your energy.',
    accent: 'bg-coral',
  },
  {
    emoji: '🧑‍💻',
    title: 'Freelancers',
    desc: 'Juggle multiple clients and deadlines without missing a single one.',
    accent: 'bg-amber',
  },
  {
    emoji: '🔬',
    title: 'Researchers',
    desc: 'Plan long projects, papers and experiments across weeks of focus.',
    accent: 'bg-cyan',
  },
  {
    emoji: '🤝',
    title: 'Teams',
    desc: 'Shared schedules can be delegated and coordinated by leadership.',
    accent: 'bg-coral',
  },
]

export default function Audience() {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, amount: 0.2 })

  return (
    <section id="audience" className="border-t border-line py-12">
      <div className="mx-auto max-w-[1180px] px-7">
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        >
          <SectionHeading
            align="center"
            eyebrow="Who it's for"
            title="Built for everyone who has too much to do"
            description="One adaptive engine, reshaped around whatever your week actually looks like."
          />
        </motion.div>

        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {audiences.map((audience, i) => (
            <motion.div
              key={audience.title}
              initial={{ opacity: 0, y: 26 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.55, delay: (i % 3) * 0.1, ease: 'easeOut' }}
              className="group rounded-[4px] border border-line bg-surface p-6 transition-colors duration-300 hover:border-dim"
            >
              <span className="inline-block text-2xl transition-transform duration-300 group-hover:scale-110">
                {audience.emoji}
              </span>
              <h3 className="mt-4 text-base font-semibold text-ink">{audience.title}</h3>
              <p className="mt-2 text-[0.85rem] leading-relaxed text-dim">{audience.desc}</p>
              <span
                className={`mt-5 block h-0.5 w-8 rounded-full ${audience.accent} transition-all duration-500 group-hover:w-16`}
              />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
