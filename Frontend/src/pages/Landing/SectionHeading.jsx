export default function SectionHeading({ eyebrow, title, description, align = 'left' }) {
  return (
    <div className={align === 'center' ? 'mx-auto max-w-[46ch] text-center' : 'max-w-[46ch]'}>
      {eyebrow && (
        <p className="font-mono text-[0.72rem] tracking-[0.18em] text-amber uppercase">{eyebrow}</p>
      )}
      <h2 className="mt-3 text-[1.75rem] font-bold tracking-[-0.01em] text-ink sm:text-[2rem]">
        {title}
      </h2>
      {description && <p className="mt-3 text-[0.98rem] leading-relaxed text-dim">{description}</p>}
    </div>
  )
}
