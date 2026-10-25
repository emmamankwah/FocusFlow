import { useEffect, useState } from 'react'

const DAY_ABBR = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const DAY_START_HOUR = 8
const DAY_END_HOUR = 22
const DAY_HOURS = DAY_END_HOUR - DAY_START_HOUR

const COLOR_CLASS = {
  amber: 'bg-amber',
  cyan: 'bg-cyan',
  coral: 'bg-coral',
}

// Columns start on Sunday, matching DAY_ABBR index order.
const PATTERN = [
  [{ s: 1, e: 3, c: 'cyan' }],
  [{ s: 2, e: 4, c: 'cyan' }, { s: 8, e: 9, c: 'amber' }],
  [{ s: 0, e: 2, c: 'amber' }, { s: 5, e: 7, c: 'coral' }],
  [{ s: 3, e: 6, c: 'cyan' }],
  [{ s: 1, e: 2, c: 'coral' }, { s: 6, e: 9, c: 'amber' }],
  [{ s: 4, e: 5, c: 'cyan' }],
  [],
]

const legend = [
  { label: 'Deadline work', className: 'bg-amber' },
  { label: 'Study session', className: 'bg-cyan' },
  { label: 'At risk', className: 'bg-coral' },
]

const pad = (n) => String(n).padStart(2, '0')

export default function WeekCard() {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 30000)
    return () => window.clearInterval(id)
  }, [])

  // Rebuilt on every tick so "today" stays correct after midnight; seven dates
  // are cheap, and keying by the day string keeps the columns from remounting.
  const start = new Date(now)
  start.setDate(now.getDate() - now.getDay())
  const days = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(start)
    date.setDate(start.getDate() + i)
    return {
      date,
      isToday: date.toDateString() === now.toDateString(),
      blocks: PATTERN[i],
    }
  })

  const hour = now.getHours() + now.getMinutes() / 60
  const inDayWindow = hour >= DAY_START_HOUR && hour <= DAY_END_HOUR
  const nowTop = inDayWindow ? ((hour - DAY_START_HOUR) / DAY_HOURS) * 100 : null

  return (
    <div className="rounded-[4px] border border-line bg-surface p-5">
      <div className="mb-4 flex items-center justify-between">
        <span className="text-[0.95rem] font-semibold">This week</span>
        <span className="font-mono text-[0.8rem] text-cyan">
          {pad(now.getHours())}:{pad(now.getMinutes())}
        </span>
      </div>

      <div className="grid grid-cols-7 gap-1.5">
        {days.map((day) => (
          <div key={day.date.toDateString()} className="flex flex-col gap-1">
            <div
              className={`pb-1.5 text-center text-[0.68rem] ${
                day.isToday ? 'font-semibold text-amber' : 'text-dim'
              }`}
            >
              {DAY_ABBR[day.date.getDay()]} {day.date.getDate()}
            </div>
            <div className="relative h-[152px] overflow-hidden rounded-[2px] bg-deck">
              {day.blocks.map((block, i) => (
                <span
                  key={i}
                  aria-hidden
                  className={`absolute right-0.5 left-0.5 rounded-[2px] opacity-90 ${
                    COLOR_CLASS[block.c]
                  }`}
                  style={{
                    top: `${(block.s / DAY_HOURS) * 100}%`,
                    height: `${((block.e - block.s) / DAY_HOURS) * 100}%`,
                  }}
                />
              ))}
              {day.isToday && nowTop !== null && (
                <span
                  aria-hidden
                  className="absolute inset-x-0 z-10 h-0.5 bg-amber shadow-[0_0_6px_var(--color-amber)]"
                  style={{ top: `${nowTop}%` }}
                />
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap gap-4">
        {legend.map((item) => (
          <span key={item.label} className="inline-flex items-center gap-1.5 text-[0.72rem] text-dim">
            <i className={`inline-block h-[7px] w-[7px] rounded-full ${item.className}`} />
            {item.label}
          </span>
        ))}
      </div>
    </div>
  )
}
