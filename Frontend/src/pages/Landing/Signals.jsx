import SectionHeading from './SectionHeading.jsx'

const signals = [
  {
    title: 'Deadlines',
    desc: 'How close each one is, and how much work is actually left before it arrives.',
    dot: 'bg-amber',
  },
  {
    title: 'Free time',
    desc: 'What is genuinely open on your calendar, not what a static plan assumes.',
    dot: 'bg-cyan',
  },
  {
    title: 'Your habits',
    desc: 'Slow coding sessions, strong mornings, the weeknights you tend to skip.',
    dot: 'bg-coral',
  },
  {
    title: 'Conflicts',
    desc: 'Practice, shifts, and events that quietly eat into the hours you planned to study.',
    dot: 'bg-dim',
  },
]

export default function Signals() {
  return (
    <section id="signals" className="border-t border-line py-16 sm:py-20">
      <div className="mx-auto max-w-[1180px] px-7">
        <SectionHeading
          eyebrow="How it thinks"
          title="Four signals, watched at once"
          description="None of these alone would catch a bad week. Together, they do."
        />

        <div className="mt-10 grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-2 lg:grid-cols-4">
          {signals.map((signal) => (
            <div key={signal.title} className="bg-canvas px-5 py-6">
              <div className="mb-4 grid h-8 w-8 place-items-center rounded-full border border-line">
                <i className={`h-2 w-2 rounded-full ${signal.dot}`} />
              </div>
              <h3 className="mb-2 text-[0.98rem] font-semibold text-ink">{signal.title}</h3>
              <p className="text-[0.85rem] leading-relaxed text-dim">{signal.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
