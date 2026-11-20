const sample = [
  { value: '6', label: 'deadlines tracked' },
  { value: '11h', label: 'study time placed' },
  { value: '3', label: 'automatic re-plans' },
  { value: '0', label: 'manual reshuffles' },
]

const principles = [
  {
    title: 'Plans, not lists',
    desc: 'A list tells you what exists. A plan tells you when you will actually do it.',
  },
  {
    title: 'Re-plans, not guilt',
    desc: 'When the week breaks, the work moves. It does not just turn red and wait for you.',
  },
  {
    title: 'You stay in control',
    desc: 'Every block is editable. The planner proposes; you decide what your week looks like.',
  },
]

export default function Principles() {
  return (
    <section className="border-t border-line py-16 sm:py-20">
      <div className="mx-auto max-w-[1180px] px-7">
        <div className="rounded-xl border border-line bg-surface/60 px-5 py-6 sm:px-8">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
            <p className="font-mono text-[0.64rem] tracking-[0.16em] text-dim uppercase">
              A sample week in FocusFlow
            </p>
            <p className="text-[0.68rem] text-dim">Illustrative, not a live account</p>
          </div>

          <dl className="mt-6 grid grid-cols-2 gap-6 sm:grid-cols-4">
            {sample.map((item) => (
              <div key={item.label}>
                <dt className="font-mono text-2xl text-ink sm:text-3xl">{item.value}</dt>
                <dd className="mt-1.5 text-[0.72rem] leading-snug text-dim">{item.label}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className="mt-14 grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:gap-14">
          <div>
            <p className="eyebrow">Why it is built this way</p>
            <h2 className="mt-3 max-w-[18ch] text-[1.75rem] font-bold tracking-[-0.01em] text-ink sm:text-[2rem]">
              Built for the week you actually have
            </h2>
            <p className="mt-3 max-w-[40ch] text-[0.98rem] leading-relaxed text-dim">
              Not the week you meant to have. FocusFlow starts from the real calendar, the real
              energy, and the work that is genuinely due.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {principles.map((principle, i) => (
              <div key={principle.title} className="rounded-xl border border-line bg-surface p-5">
                <span className="font-mono text-[0.66rem] text-amber">0{i + 1}</span>
                <h3 className="mt-3 text-[0.95rem] font-semibold text-ink">{principle.title}</h3>
                <p className="mt-2 text-[0.82rem] leading-relaxed text-dim">{principle.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <p className="mt-10 flex items-start gap-2.5 rounded-lg border border-line bg-canvas px-4 py-3 text-[0.78rem] leading-relaxed text-dim">
          <span aria-hidden className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan" />
          FocusFlow organizes your work. It never writes, completes, or submits coursework for you.
        </p>
      </div>
    </section>
  )
}
