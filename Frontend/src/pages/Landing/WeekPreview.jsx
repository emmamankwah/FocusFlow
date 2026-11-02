import { Link } from 'react-router-dom'

const days = [
  {
    day: 'Mon',
    date: 'Nov 2',
    items: [
      { time: '9:00 AM', label: 'PSYCH 101', kind: 'class' },
      { time: '11:00 AM', label: 'CS 240', kind: 'class' },
      { time: '2:30 PM', label: 'WRITING 160', kind: 'class' },
      { time: '5:00 PM', label: 'Workout', kind: 'personal' },
    ],
  },
  {
    day: 'Tue',
    date: 'Nov 3',
    items: [
      { time: '11:00 AM', label: 'BIO 172', kind: 'class' },
      { time: '1:00 PM', label: 'ECON 201', kind: 'class' },
      { time: '3:00 PM', label: 'DESIGN 210', kind: 'class' },
      { time: '6:00 PM', label: 'Lab notebook due', kind: 'due', focus: true },
    ],
  },
  {
    day: 'Wed',
    date: 'Nov 4',
    items: [
      { time: '9:00 AM', label: 'PSYCH 101', kind: 'class' },
      { time: '11:00 AM', label: 'CS 240', kind: 'class' },
      { time: '2:30 PM', label: 'WRITING 160', kind: 'class' },
      { time: '4:30 PM', label: 'CS 240 project block', kind: 'study' },
      { time: '7:00 PM', label: 'Robotics', kind: 'personal' },
    ],
  },
  {
    day: 'Thu',
    date: 'Nov 5',
    items: [
      { time: '11:00 AM', label: 'BIO 172', kind: 'class' },
      { time: '1:00 PM', label: 'ECON 201', kind: 'class' },
      { time: '3:00 PM', label: 'DESIGN 210', kind: 'class' },
      { time: '7:00 PM', label: 'CS 240 project block', kind: 'study' },
    ],
  },
  {
    day: 'Fri',
    date: 'Nov 6',
    items: [
      { time: '9:00 AM', label: 'CS 240 lab', kind: 'class' },
      { time: '1:00 PM', label: 'BIO 172 lab', kind: 'class' },
      { time: '4:00 PM', label: 'Project buffer', kind: 'study' },
      { time: '8:00 PM', label: 'ECON problem set', kind: 'study' },
    ],
  },
  {
    day: 'Sat',
    date: 'Nov 7',
    items: [
      { time: '11:00 AM', label: 'Laundry', kind: 'personal' },
      { time: '2:00 PM', label: 'Reading catch-up', kind: 'study' },
    ],
  },
  {
    day: 'Sun',
    date: 'Nov 8',
    items: [
      { time: '5:00 PM', label: 'Rest', kind: 'personal' },
      { time: '7:00 PM', label: 'Weekly review', kind: 'study' },
    ],
  },
]

const kindStyles = {
  class: 'border-cyan/40 bg-cyan/[0.05] text-ink',
  study: 'border-amber/50 bg-amber/[0.07] text-ink',
  personal: 'border-line bg-transparent text-dim',
  due: 'border-amber/50 bg-amber/[0.12] text-ink ring-1 ring-amber/20',
}

const legend = [
  { label: 'Class', dot: 'bg-cyan' },
  { label: 'Study block', dot: 'bg-amber' },
  { label: 'Personal', dot: 'bg-dim' },
  { label: 'Due', dot: 'bg-amber ring-2 ring-amber/25' },
]

export default function WeekPreview() {
  return (
    <section id="week" className="border-t border-line py-16 sm:py-20">
      <div className="mx-auto max-w-[1180px] px-7">
        <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="eyebrow">From one class to the whole picture</p>
            <h2 className="mt-3 max-w-[20ch] text-[1.75rem] font-bold tracking-[-0.01em] text-ink sm:text-[2rem]">
              See your week before it happens
            </h2>
            <p className="mt-3 max-w-[52ch] text-[0.98rem] leading-relaxed text-dim">
              Classes, study blocks, and the rest of your life in one view. The plan protects the
              work that matters and leaves room for the things that are not school.
            </p>
          </div>

          <Link to="/signup" className="btn btn-ghost btn-sm shrink-0 self-start">
            Build your own week
          </Link>
        </div>

        <div className="mt-8 overflow-hidden rounded-xl border border-line bg-surface/40">
          <div className="grid grid-cols-1 gap-px bg-line sm:grid-cols-2 lg:grid-cols-7">
            {days.map((day) => (
              <div key={day.day} className="bg-canvas p-3">
                <div className="flex items-baseline justify-between lg:block">
                  <p className="font-mono text-[0.66rem] tracking-[0.14em] text-ink uppercase">
                    {day.day}
                  </p>
                  <p className="font-mono text-[0.6rem] text-dim lg:mt-0.5">{day.date}</p>
                </div>

                <ul className="mt-3 space-y-1.5">
                  {day.items.map((item) => (
                    <li
                      key={`${item.time}-${item.label}`}
                      className={`border-l-2 px-2 py-1.5 ${kindStyles[item.kind]}`}
                    >
                      <span
                        className={`block font-mono text-[0.58rem] tracking-[0.04em] ${
                          item.kind === 'due' ? 'text-ink/70' : 'text-dim'
                        }`}
                      >
                        {item.time}
                      </span>
                      <span className="mt-0.5 block text-[0.75rem] leading-tight">{item.label}</span>
                      {item.focus ? (
                        <span className="mt-1 inline-block font-mono text-[0.55rem] tracking-[0.1em] text-amber uppercase">
                          Focus today
                        </span>
                      ) : null}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <ul className="flex flex-wrap items-center gap-x-5 gap-y-2">
            {legend.map((item) => (
              <li key={item.label} className="flex items-center gap-2 text-[0.72rem] text-dim">
                <span aria-hidden className={`h-1.5 w-1.5 rounded-full ${item.dot}`} />
                {item.label}
              </li>
            ))}
          </ul>
          <p className="text-[0.7rem] text-dim">
            Illustrative sample week. Your plan is built from your own schedule.
          </p>
        </div>
      </div>
    </section>
  )
}
