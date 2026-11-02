import SectionHeading from './SectionHeading.jsx'

const blocks = [
  { day: 'Tue, Nov 3', time: '6:00 - 8:00 PM' },
  { day: 'Thu, Nov 5', time: '7:00 - 9:00 PM' },
  { day: 'Fri, Nov 6', time: '4:00 - 5:00 PM' },
]

export default function FromDeadline() {
  return (
    <section id="how" className="border-t border-line py-16 sm:py-20">
      <div className="mx-auto max-w-[1180px] px-7">
        <SectionHeading
          eyebrow="From deadline to plan"
          title="One line in. A week of work out."
          description="FocusFlow reads the date, checks what is already on your calendar, and places the work where it actually fits. Nothing is guessed silently."
        />

        <div className="mt-10 grid items-stretch gap-4 lg:grid-cols-[1fr_auto_1fr]">
          <article className="artifact flex flex-col p-5">
            <header className="flex items-start justify-between gap-3">
              <div>
                <p className="font-mono text-[0.62rem] tracking-[0.16em] text-dim uppercase">
                  The source
                </p>
                <p className="mt-1 text-sm font-semibold text-ink">CS 240 &middot; Syllabus</p>
              </div>
              <span className="chip">Page 3</span>
            </header>

            <div className="mt-4 flex-1 rounded-lg border border-line bg-canvas/60 p-4">
              <p className="font-mono text-[0.6rem] tracking-[0.14em] text-dim uppercase">
                Course schedule
              </p>
              <p className="mt-3 text-[0.8rem] leading-6 text-dim">
                Week 11 &mdash; Trees and graphs. Lab meets Thursday at 4:00 PM in Haslett 210.
              </p>
              <p className="mt-3 rounded-md bg-amber/10 px-2.5 py-2 text-[0.82rem] leading-6 text-ink ring-1 ring-amber/30">
                Project checkpoint: due Friday, November 6 at 11:59 PM. Submit on Gradescope.
              </p>
              <p className="mt-3 text-[0.8rem] leading-6 text-dim">
                Late submissions lose 10% per day. Questions? Post on the course forum.
              </p>
            </div>

            <p className="mt-4 flex items-center gap-2 text-[0.72rem] text-dim">
              <span className="h-1.5 w-1.5 rounded-full bg-amber" />
              The highlighted line becomes a deadline
            </p>
          </article>

          <div aria-hidden className="hidden items-center justify-center lg:flex">
            <span className="grid h-9 w-9 place-items-center rounded-full border border-line bg-canvas text-dim">
              <svg
                viewBox="0 0 24 24"
                width="15"
                height="15"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
            </span>
          </div>

          <article className="artifact flex flex-col p-5">
            <header className="flex items-start justify-between gap-3">
              <div>
                <p className="font-mono text-[0.62rem] tracking-[0.16em] text-dim uppercase">
                  The plan
                </p>
                <p className="mt-1 text-sm font-semibold text-ink">CS 240 &middot; Project checkpoint</p>
              </div>
              <span className="chip">5h planned</span>
            </header>

            <div className="mt-4 flex items-baseline justify-between gap-3 border-b border-line pb-4">
              <div>
                <p className="font-mono text-[0.6rem] tracking-[0.14em] text-dim uppercase">
                  Deadline
                </p>
                <p className="mt-1 text-[0.9rem] font-semibold text-ink">Fri, Nov 6 &middot; 11:59 PM</p>
              </div>
              <span className="font-mono text-[0.66rem] text-cyan">On track</span>
            </div>

            <ol className="mt-4 flex-1 space-y-2">
              {blocks.map((block) => (
                <li
                  key={block.day}
                  className="flex items-center justify-between gap-3 rounded-md border border-line bg-deck/50 px-3 py-2.5"
                >
                  <span className="text-[0.82rem] text-ink">{block.day}</span>
                  <span className="font-mono text-[0.7rem] text-dim">{block.time}</span>
                </li>
              ))}
            </ol>

            <p className="mt-4 text-[0.72rem] leading-relaxed text-dim">
              Placed around your Thursday 4 PM lab and 7 PM practice. Move a block and the rest
              reflows.
            </p>
          </article>
        </div>
      </div>
    </section>
  )
}
