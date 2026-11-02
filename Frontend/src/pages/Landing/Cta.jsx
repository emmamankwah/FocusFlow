import { Link } from 'react-router-dom'

const steps = [
  'Add a syllabus, a deadline, or a single task',
  'FocusFlow places the work around your real calendar',
  'Change anything and the plan rebuilds itself',
]

export default function Cta() {
  return (
    <section id="start" className="border-t border-line py-16 sm:py-20">
      <div className="mx-auto max-w-[1180px] px-7">
        <div className="relative overflow-hidden rounded-2xl border border-line bg-surface px-6 py-10 sm:px-10 sm:py-12">
          <div aria-hidden className="pointer-events-none absolute inset-0">
            <div className="absolute -top-24 -right-16 h-[300px] w-[420px] rounded-full bg-amber/[0.07] blur-3xl" />
            <div className="absolute -bottom-28 -left-10 h-[280px] w-[380px] rounded-full bg-cyan/[0.06] blur-3xl" />
          </div>

          <div className="relative grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
            <div>
              <p className="eyebrow">Start with one deadline</p>
              <h2 className="mt-3 max-w-[18ch] text-[clamp(1.8rem,3.4vw,2.6rem)] leading-[1.08] font-bold tracking-[-0.02em] text-ink">
                Give your week to something that keeps up with it.
              </h2>
              <p className="mt-4 max-w-[46ch] text-[0.98rem] leading-relaxed text-dim">
                Set up your first week in a few minutes. No credit card, no perfect calendar
                required.
              </p>

              <div className="mt-7 flex flex-wrap items-center gap-3">
                <Link to="/signup" className="btn btn-primary">
                  Start planning free
                </Link>
                <Link to="/login" className="btn btn-ghost">
                  I have an account
                </Link>
              </div>

              <p className="mt-5 text-[0.72rem] text-dim">
                Free to start &middot; Plans stay editable &middot; It never does the work for you
              </p>
            </div>

            <ol className="space-y-3">
              {steps.map((step, i) => (
                <li
                  key={step}
                  className="flex items-start gap-3 rounded-lg border border-line bg-canvas/50 p-3.5"
                >
                  <span className="font-mono text-[0.68rem] text-amber">0{i + 1}</span>
                  <span className="text-[0.83rem] leading-relaxed text-dim">{step}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>
    </section>
  )
}
