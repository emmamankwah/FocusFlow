import { Link } from 'react-router-dom'

export default function AuthLayout({ title, subtitle, onSubmit, footer, children }) {
  return (
    <main className="relative grid min-h-screen place-items-center overflow-hidden bg-canvas px-6 py-16 font-grotesk text-ink">
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -left-32 h-[480px] w-[480px] rounded-full bg-amber/10 blur-3xl" />
        <div className="absolute right-[-160px] bottom-[-160px] h-[460px] w-[460px] rounded-full bg-coral/10 blur-3xl" />
        <div className="absolute top-1/3 right-1/3 h-[320px] w-[320px] rounded-full bg-cyan/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="mb-8 text-center">
          <Link to="/" className="text-[1.1rem] font-bold tracking-[-0.01em]">
            Focus<span className="text-amber">Flow</span>
          </Link>
          <h1 className="mt-6 text-[1.75rem] font-bold tracking-[-0.01em]">{title}</h1>
          {subtitle && <p className="mt-2.5 text-[0.9rem] text-dim">{subtitle}</p>}
        </div>

        <form
          onSubmit={onSubmit}
          className="space-y-4 rounded-[4px] border border-line bg-surface p-7"
        >
          {children}
        </form>

        {footer && <p className="mt-6 text-center text-[0.86rem] text-dim">{footer}</p>}
      </div>
    </main>
  )
}
