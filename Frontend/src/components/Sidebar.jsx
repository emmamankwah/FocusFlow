import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';

const links = [
  { label: 'How it works', href: '#how' },
  { label: 'Your week', href: '#week' },
  { label: 'Features', href: '#features' },
  { label: 'FAQ', href: '#faq' },
];

export default function Sidebar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <aside
      className={`hidden lg:flex flex-col h-screen w-64 border-r bg-canvas/85 backdrop-blur transition-colors duration-300 ${
        scrolled ? 'border-line' : 'border-transparent'
      }`}
    >
      <nav className="flex flex-col flex-1 p-6 space-y-4">
        <Link to="/" className="text-2xl font-bold text-ink">Focus<span className="text-amber">Flow</span></Link>
        {links.map((link) => (
          <a key={link.href} href={link.href} className="text-dim hover:text-ink transition-colors">
            {link.label}
          </a>
        ))}
        <div className="mt-auto space-y-2">
          <Link to="/login" className="btn btn-ghost btn-sm w-full justify-center">
            Log in
          </Link>
          <Link to="/signup" className="btn btn-primary btn-sm w-full justify-center">
            Get started
+          </Link>
        </div>
      </nav>
    </aside>
  );
}
