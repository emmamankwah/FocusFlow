import SectionHeading from './SectionHeading.jsx'

const signals = [
  {
    title: 'Deadlines',
    desc: 'How close each one is, and how much is left to do before it arrives.',
    dot: 'bg-amber',
  },
  {
    title: 'Free time',
    desc: "What's actually open on your calendar, not what a static plan assumes.",
    dot: 'bg-cyan',
  },
  {
    title: 'Your habits',
    desc: 'Slow coding sessions, strong mornings, the Wednesdays you tend to skip.',
    dot: 'bg-coral',
  },
  {
    title: 'Conflicts',
    desc: 'Practice, meetings, and events that quietly eat into study time.',
    dot: 'bg-dim',
  },
]

export default function Signals() {
  return (
    <section id="signals" className="border-t border-line py-12">
      <div className="mx-auto max-w-[1180px] px-7">
        <div className="mb-9">
          <SectionHeading
            eyebrow="How it works"
            title="Four signals, watched at once"
            description="None of these alone would catch a bad week. Together, they do."
          />
        </div>

        <div className="grid grid-cols-4 gap-px border border-line bg-line max-[860px]:grid-cols-2">
          {signals.map((signal) => (
            <div key={signal.title} className="bg-canvas px-[22px] py-[26px]">
              <div className="mb-4 grid h-[30px] w-[30px] place-items-center rounded-full border-[1.5px] border-line">
                <i className={`h-2 w-2 rounded-full ${signal.dot}`} />
              </div>
              <h3 className="mb-2 text-[0.98rem] font-semibold">{signal.title}</h3>
              <p className="text-[0.86rem] leading-normal text-dim">{signal.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
