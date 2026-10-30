import { Link } from 'react-router-dom'

export default function Cta() {
  return (
    <section id="start" className="relative overflow-hidden border-t border-line py-16">
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/2 left-1/2 h-[420px] w-[720px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-amber/10 blur-3xl" />
        <div className="absolute top-1/2 left-1/2 h-[300px] w-[520px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-coral/10 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-[1180px] px-7 text-center">
        <h2 className="mx-auto max-w-[18ch] text-[clamp(2rem,4.4vw,3rem)] font-bold tracking-[-0.02em] text-ink">
          Stop reorganizing your own week by hand
        </h2>
        <p className="mx-auto mt-5 max-w-[46ch] text-[1rem] leading-relaxed text-ink/75">
          Create your account in under a minute — FocusFlow rebuilds your first week tonight.
        </p>
        <div className="mt-9 flex flex-wrap items-center justify-center gap-3.5">
          <Link to="/signup" className="btn btn-primary">
            Start planning free
          </Link>
          <Link to="/login" className="btn btn-ghost">
            I have an account
          </Link>
        </div>
      </div>
    </section>
  )
}
