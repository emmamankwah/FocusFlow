import { Link } from 'react-router-dom'

const columns = [
  {
    title: 'Product',
    links: [
      { label: 'How it works', href: '#how' },
      { label: 'Your week', href: '#week' },
      { label: 'Features', href: '#features' },
      { label: 'FAQ', href: '#faq' },
    ],
  },
  {
    title: 'Company',
    links: [{ label: 'About' }, { label: 'Contact' }, { label: 'Careers' }],
  },
  {
    title: 'Legal',
    links: [{ label: 'Privacy' }, { label: 'Terms' }, { label: 'Security' }],
  },
]

export default function Footer() {
  return (
    <footer className="border-t border-line py-10">
      <div className="mx-auto max-w-[1180px] px-7">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-[1.6fr_1fr_1fr_1fr]">
          <div>
            <Link to="/" className="text-[1.1rem] font-bold tracking-[-0.01em] text-ink">
              Focus<span className="text-amber">Flow</span>
            </Link>
            <p className="mt-4 max-w-[38ch] text-[0.85rem] leading-relaxed text-dim">
              An intelligent productivity coach that watches your deadlines, free time, habits,
              and conflicts &mdash; then rebuilds your week the moment any of it changes.
            </p>
          </div>

          {columns.map((column) => (
            <div key={column.title}>
              <p className="font-mono text-[0.66rem] tracking-[0.18em] text-ink uppercase">
                {column.title}
              </p>
              <ul className="mt-4 space-y-3">
                {column.links.map((link) => (
                  <li key={link.label}>
                    {link.href ? (
                      <a
                        href={link.href}
                        className="text-[0.85rem] text-dim transition-colors hover:text-ink"
                      >
                        {link.label}
                      </a>
                    ) : (
                      <span className="cursor-default text-[0.85rem] text-dim" title="Coming soon">
                        {link.label}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-line pt-7 sm:flex-row sm:items-center sm:justify-between">
          <p className="font-mono text-[0.68rem] text-dim">
            &copy; {new Date().getFullYear()} FocusFlow AI
          </p>
          <p className="max-w-[52ch] text-[0.72rem] leading-relaxed text-dim">
            FocusFlow organizes your school. It does not complete or submit coursework for you.
          </p>
        </div>
      </div>
    </footer>
  )
}
