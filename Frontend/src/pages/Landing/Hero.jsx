import { Link } from 'react-router-dom'
import HeroPlan from './HeroPlan.jsx'

const stats = [
  { value: '4', label: 'signals watched at once' },
  { value: '24/7', label: 're-planning as things change' },
  { value: '0', label: 'manual reshuffles' },
]

export default function Hero() {
  return (
    <section className="relative overflow-hidden pt-12 pb-14 sm:pt-16 sm:pb-20">
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <div className="absolute -top-48 left-1/2 h-[440px] w-[820px] -translate-x-1/2 rounded-full bg-amber/[0.06] blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-[1180px] px-7">
        <div className="grid items-center gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,0.9fr)] lg:gap-14">
          <div>
            <p className="eyebrow inline-flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-amber" />
              A planner that re-plans itself
            </p>

            <h1 className="mt-5 max-w-[14ch] text-[clamp(2.6rem,5.4vw,4.1rem)] leading-[1.02] font-bold tracking-[-0.025em] text-ink">
              Your semester, already planned.
            </h1>

            <p className="mt-6 max-w-[46ch] text-[1.05rem] leading-relaxed text-dim">
              Add your syllabi, deadlines, and calendar once. FocusFlow builds the week around
              what is actually due, then rebuilds it the moment anything changes.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link to="/signup" className="btn btn-primary">
                Start planning free
              </Link>
              <a href="#week" className="btn btn-ghost">
                See a sample week
              </a>
            </div>

            <p className="mt-4 text-[0.76rem] text-dim">
              Free to start &middot; No credit card &middot; Every block stays editable
            </p>

            <dl className="mt-10 grid max-w-lg grid-cols-3 gap-5 border-t border-line pt-6">
              {stats.map((stat) => (
                <div key={stat.label}>
                  <dt className="font-mono text-xl text-ink sm:text-2xl">{stat.value}</dt>
                  <dd className="mt-1.5 text-[0.7rem] leading-snug text-dim">{stat.label}</dd>
                </div>
              ))}
            </dl>
          </div>

          <HeroPlan />
        </div>
      </div>
    </section>
  )
}
