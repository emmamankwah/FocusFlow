import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'

const links = [
  { label: 'How it works', href: '#signals' },
  { label: 'Features', href: '#features' },
  { label: "Who it's for", href: '#audience' },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)
  const headerRef = useRef(null)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    if (!open) return

    const onKeyDown = (e) => {
      if (e.key === 'Escape') setOpen(false)
    }
    const onPointerDown = (e) => {
      if (headerRef.current && !headerRef.current.contains(e.target)) setOpen(false)
    }

    document.addEventListener('keydown', onKeyDown)
    document.addEventListener('pointerdown', onPointerDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.removeEventListener('pointerdown', onPointerDown)
    }
  }, [open])

  return (
    <header
      ref={headerRef}
      className={`sticky top-0 z-50 border-b border-line backdrop-blur transition-colors duration-300 ${
        scrolled ? 'bg-canvas/85' : 'bg-canvas/60'
      }`}
    >
      <nav className="mx-auto flex max-w-[1180px] items-center justify-between px-7 py-5">
        <Link to="/" className="text-[1.1rem] font-bold tracking-[-0.01em] text-ink">
          Focus<span className="text-amber">Flow</span>
        </Link>

        <div className="hidden items-center gap-7 text-[0.9rem] text-dim lg:flex">
          {links.map((link) => (
            <a key={link.href} href={link.href} className="transition-colors hover:text-ink">
              {link.label}
            </a>
          ))}
        </div>

        <div className="hidden items-center gap-3 lg:flex">
          <Link to="/login" className="btn btn-ghost btn-sm">
            Sign in
          </Link>
          <Link to="/signup" className="btn btn-primary btn-sm">
            Get started
          </Link>
        </div>

        <button
          onClick={() => setOpen((o) => !o)}
          className="grid h-10 w-10 place-items-center text-ink lg:hidden"
          aria-label="Toggle menu"
          aria-expanded={open}
          aria-controls="landing-mobile-menu"
        >
          <span className="flex w-5 flex-col gap-1.5">
            <span
              className={`h-0.5 w-full bg-current transition-transform ${
                open ? 'translate-y-2 rotate-45' : ''
              }`}
            />
            <span
              className={`h-0.5 w-full bg-current transition-opacity ${open ? 'opacity-0' : ''}`}
            />
            <span
              className={`h-0.5 w-full bg-current transition-transform ${
                open ? '-translate-y-2 -rotate-45' : ''
              }`}
            />
          </span>
        </button>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            id="landing-mobile-menu"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden border-t border-line bg-canvas lg:hidden"
          >
            <div className="flex flex-col gap-4 px-7 py-6">
              {links.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="text-[0.9rem] text-dim transition-colors hover:text-ink"
                >
                  {link.label}
                </a>
              ))}
              <div className="mt-2 flex flex-col gap-2">
                <Link to="/login" className="btn btn-ghost w-full justify-center">
                  Sign in
                </Link>
                <Link to="/signup" className="btn btn-primary w-full justify-center">
                  Get started
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
