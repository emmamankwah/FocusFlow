const words = [
  'Smart Scheduling',
  'Adaptive Re-planning',
  'Deadline Risk Prediction',
  'Focus Analytics',
  'Burnout Detection',
  'Habit Learning',
  'Smart Notifications',
  'Auto-nudges',
  'Rest-Day Planning',
  'Weekly Insights',
]

export default function Marquee() {
  const row = [...words, ...words]

  return (
    <section aria-hidden className="overflow-hidden border-y border-line py-4">
      <div className="flex w-max animate-marquee items-center gap-10">
        {row.map((word, i) => (
          <span
            key={i}
            className="flex items-center gap-10 font-mono text-[0.74rem] tracking-[0.18em] whitespace-nowrap text-dim uppercase"
          >
            {word}
            <span className="text-amber">+</span>
          </span>
        ))}
      </div>
    </section>
  )
}
