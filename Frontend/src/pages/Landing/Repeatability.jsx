const chains = [
  { source: 'Canvas assignment', result: 'Three study blocks before Friday' },
  { source: 'Syllabus exam date', result: 'Review spread across two weeks' },
  { source: 'A missed session', result: 'Moved to the next open hour' },
  { source: 'Practice at 6 PM', result: 'Study shifted to the morning' },
  { source: 'A heavy Wednesday', result: 'Thursday lightened automatically' },
]

export default function Repeatability() {
  return (
    <section className="border-t border-line py-16 sm:py-20">
      <div className="mx-auto grid max-w-[1180px] gap-10 px-7 lg:grid-cols-[0.85fr_1.15fr] lg:gap-14">
        <div>
          <p className="eyebrow">And it keeps going</p>
          <h2 className="mt-3 max-w-[16ch] text-[1.75rem] font-bold tracking-[-0.01em] text-ink sm:text-[2rem]">
            Every input turns into a decision
          </h2>
          <p className="mt-3 max-w-[40ch] text-[0.98rem] leading-relaxed text-dim">
            A planner is only useful if it keeps up. FocusFlow treats every change as a new
            constraint, not an exception to apologize for.
          </p>
        </div>

        <ol className="divide-y divide-line border-y border-line">
          {chains.map((chain) => (
            <li key={chain.source} className="flex items-center gap-4 py-3.5">
              <span className="w-[42%] shrink-0 text-[0.8rem] text-dim sm:w-[38%]">
                {chain.source}
              </span>
              <span aria-hidden className="font-mono text-[0.8rem] text-amber">
                &rarr;
              </span>
              <span className="text-[0.84rem] font-medium text-ink">{chain.result}</span>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
