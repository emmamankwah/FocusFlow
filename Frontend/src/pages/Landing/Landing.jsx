import Navbar from './Navbar.jsx'
import Hero from './Hero.jsx'
import Marquee from './Marquee.jsx'
import FromDeadline from './FromDeadline.jsx'
import WeekPreview from './WeekPreview.jsx'
import Signals from './Signals.jsx'
import Features from './Features.jsx'
import Repeatability from './Repeatability.jsx'
import Audience from './Audience.jsx'
import Principles from './Principles.jsx'
import Faq from './Faq.jsx'
import Cta from './Cta.jsx'
import Footer from './Footer.jsx'
import usePageTitle from '@/lib/usePageTitle'

export default function Landing() {
  usePageTitle('FocusFlow AI - Your semester, already planned')

  return (
    <div className="ff-product min-h-screen bg-canvas font-grotesk text-ink">
      <Navbar />
      <main>
        <Hero />
        <Marquee />
        <FromDeadline />
        <WeekPreview />
        <Signals />
        <Features />
        <Repeatability />
        <Audience />
        <Principles />
        <Faq />
      </main>
      <Cta />
      <Footer />
    </div>
  )
}
