import { Link } from 'react-router-dom'

const cols = [
  {
    title: 'Product',
    links: [
      { label: 'How it works', href: '#signals' },
      { label: 'Features', href: '#features' },
      { label: "Who it's for", href: '#audience' },
    ],
  },
  {
    title: 'Resources',
    links: [
      { label: 'Blog' },
      { label: 'Documentation' },
      { label: 'Guides' },
      { label: 'Help center' },
    ],
  },
  {
    title: 'Company',
    links: [{ label: 'About' }, { label: 'Careers' }, { label: 'Contact' }, { label: 'Press' }],
  },
  {
    title: 'Legal',
    links: [{ label: 'Privacy' }, { label: 'Terms' }, { label: 'Security' }, { label: 'Cookies' }],
  },
]

export default function Footer() {
  return (
    <footer className="border-t border-line py-14">
      <div className="mx-auto max-w-[1180px] px-7">
        <div className="grid gap-10 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <Link to="/" className="text-[1.1rem] font-bold tracking-[-0.01em] text-ink">
              Focus<span className="text-amber">Flow</span>
            </Link>
            <p className="mt-4 max-w-sm text-[0.86rem] leading-relaxed text-dim">
              An intelligent productivity coach that watches your deadlines, free time, habits
              and conflicts — then rebuilds your week the moment any of it changes.
            </p>
          </div>

          {cols.map((col) => (
            <div key={col.title}>
              <p className="font-mono text-[0.72rem] tracking-[0.18em] text-ink uppercase">
                {col.title}
              </p>
              <ul className="mt-4 space-y-3">
                {col.links.map((link) => (
                  <li key={link.label}>
                    {link.href ? (
                      <a
                        href={link.href}
                        className="text-[0.86rem] text-dim transition-colors hover:text-ink"
                      >
                        {link.label}
                      </a>
                    ) : (
                      <span
                        className="cursor-default text-[0.86rem] text-dim"
                        title="Coming soon"
                      >
                        {link.label}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-start justify-between gap-3 border-t border-line pt-7 sm:flex-row sm:items-center">
          <p className="font-mono text-[0.72rem] text-dim">
            © {new Date().getFullYear()} FocusFlow AI
          </p>
          <p className="font-mono text-[0.72rem] text-dim">
            Built to keep you ahead of your own deadlines.
          </p>
        </div>
      </div>
    </footer>
  )
}
