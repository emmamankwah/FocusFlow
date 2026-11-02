import SectionHeading from './SectionHeading.jsx'

const faqs = [
  {
    q: 'Is FocusFlow free?',
    a: 'FocusFlow is free to start. If paid tools arrive later, they will be optional and clearly separate from the core planner.',
  },
  {
    q: 'What can I add?',
    a: 'Syllabi, assignment lists, your class schedule, calendar events, and one-off tasks. Upload a PDF or document, paste text, or type things in yourself.',
  },
  {
    q: 'Does it do my work for me?',
    a: 'No. FocusFlow organizes and schedules your work. It does not write, complete, or submit coursework.',
  },
  {
    q: 'What happens when I miss something?',
    a: 'The plan recalculates. Unfinished work is moved into the next realistic opening instead of being left behind as a red overdue item.',
  },
  {
    q: 'Do I need to connect Canvas?',
    a: 'No. Start with a syllabus, a screenshot, or a single deadline. Calendar and course connections are optional.',
  },
  {
    q: 'What happens to my data?',
    a: 'Your schedule and course details are used to build your plan. FocusFlow does not sell your personal data.',
  },
]

export default function Faq() {
  return (
    <section id="faq" className="border-t border-line py-16 sm:py-20">
      <div className="mx-auto grid max-w-[1180px] gap-8 px-7 lg:grid-cols-[0.8fr_1.2fr] lg:gap-14">
        <SectionHeading
          eyebrow="Questions"
          title="Before you hand over your week"
          description="The short answers. Anything else, ask us directly."
        />

        <div className="divide-y divide-line border-y border-line">
          {faqs.map((faq) => (
            <details key={faq.q} className="group py-4">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-[0.95rem] font-semibold text-ink [&::-webkit-details-marker]:hidden">
                {faq.q}
                <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full border border-line font-mono text-[0.8rem] text-dim transition-transform duration-200 group-open:rotate-45">
                  +
                </span>
              </summary>
              <p className="mt-3 max-w-[62ch] text-[0.86rem] leading-relaxed text-dim">{faq.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  )
}
