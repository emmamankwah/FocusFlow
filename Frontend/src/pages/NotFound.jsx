import { Link } from 'react-router-dom'
import usePageTitle from '@/lib/usePageTitle'

export default function NotFound() {
  usePageTitle('Page not found — FocusFlow')
  return (
    <main className="relative grid min-h-screen place-items-center overflow-hidden bg-canvas px-6 py-16 text-center font-grotesk text-ink">
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -left-32 h-[480px] w-[480px] rounded-full bg-amber/10 blur-3xl" />
        <div className="absolute right-[-160px] bottom-[-160px] h-[460px] w-[460px] rounded-full bg-coral/10 blur-3xl" />
      </div>

      <div className="relative">
        <p className="font-mono text-7xl font-medium text-amber sm:text-9xl">404</p>
        <h1 className="mt-5 text-2xl font-bold tracking-[-0.01em] sm:text-3xl">
          This page drifted off schedule
        </h1>
        <p className="mx-auto mt-3 max-w-md text-[0.9rem] text-dim">
          The page you&apos;re looking for doesn&apos;t exist or has moved.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link to="/" className="btn btn-primary">
            Back to home
          </Link>
          <Link to="/login" className="btn btn-ghost">
            Log in
          </Link>
        </div>
      </div>
    </main>
  )
}
