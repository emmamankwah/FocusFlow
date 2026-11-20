const rows = [
  {
    course: 'CS 240',
    title: 'Project checkpoint',
    due: 'Fri, 11:59 PM',
    blocks: 'Tue 6-8 PM / Thu 7-9 PM / Fri 4-5 PM',
    label: 'On track',
    tone: 'cyan',
  },
  {
    course: 'BIO 172',
    title: 'Lab notebook',
    due: 'Tue, 6:00 PM',
    blocks: 'Moved to tonight, 7-9 PM',
    label: 'Re-planned',
    tone: 'amber',
  },
  {
    course: 'ECON 201',
    title: 'Problem Set 4',
    due: 'Fri, 11:59 PM',
    blocks: 'Wed 4:30 PM / Fri 8 PM',
    label: '2h left',
    tone: 'coral',
  },
]

const tones = {
  cyan: 'border-cyan/40 bg-cyan/10 text-cyan',
  amber: 'border-amber/40 bg-amber/10 text-amber',
  coral: 'border-coral/40 bg-coral/10 text-coral',
}

export default function HeroPlan() {
  return (
    <aside aria-label="Sample FocusFlow week" className="relative mx-auto w-full max-w-[460px]">
      <div className="artifact overflow-hidden shadow-[0_36px_90px_-50px_rgba(0,0,0,0.95)]">
        <header className="flex items-center justify-between gap-4 border-b border-line px-5 py-4">
          <div>
            <p className="font-mono text-[0.62rem] tracking-[0.16em] text-dim uppercase">
              This week
            </p>
            <p className="mt-1 text-sm font-semibold text-ink">Nov 2 - 8</p>
          </div>
          <span className="chip">6 due</span>
        </header>

        <ul className="divide-y divide-line">
          {rows.map((row) => (
            <li key={row.title} className="px-5 py-4">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-mono text-[0.62rem] tracking-[0.14em] text-dim uppercase">
                    {row.course}
                  </p>
                  <p className="mt-1 truncate text-[0.92rem] font-semibold text-ink">{row.title}</p>
                </div>
                <span
                  className={`shrink-0 rounded-full border px-2 py-0.5 font-mono text-[0.6rem] tracking-[0.06em] uppercase ${tones[row.tone]}`}
                >
                  {row.label}
                </span>
              </div>

              <div className="mt-2.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-[0.74rem] text-dim">
                <span>Due {row.due}</span>
                <span aria-hidden className="h-1 w-1 rounded-full bg-line" />
                <span>{row.blocks}</span>
              </div>
            </li>
          ))}
        </ul>

        <footer className="flex items-center justify-between gap-3 border-t border-line bg-deck/50 px-5 py-3">
          <span className="font-mono text-[0.62rem] tracking-[0.14em] text-dim uppercase">
            Re-planned 2 min ago
          </span>
          <span className="text-[0.7rem] text-cyan">3 changes</span>
        </footer>
      </div>

      <div className="absolute -right-2 -bottom-4 hidden rounded-lg border border-line bg-canvas px-3 py-2 shadow-lg sm:block">
        <p className="font-mono text-[0.58rem] tracking-[0.14em] text-dim uppercase">
          No manual reshuffle
        </p>
        <p className="mt-0.5 text-[0.72rem] text-ink">You just keep the plan honest.</p>
      </div>
    </aside>
  )
}
