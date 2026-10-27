export function cx(...parts) {
  return parts.filter(Boolean).join(' ')
}

export const BTN =
  'inline-flex items-center justify-center gap-1.5 rounded-[3px] border border-line bg-surface px-3 py-1.5 text-[0.78rem] font-semibold text-ink transition duration-150 hover:border-dim disabled:cursor-not-allowed disabled:opacity-45'

export const BTN_PRIMARY =
  'inline-flex items-center justify-center gap-1.5 rounded-[3px] border border-amber bg-amber px-3 py-1.5 text-[0.78rem] font-semibold text-[#171205] transition duration-150 hover:-translate-y-px hover:bg-amber/90 disabled:cursor-not-allowed disabled:opacity-45 disabled:hover:translate-y-0'

export const BTN_QUIET =
  'inline-flex items-center justify-center gap-1.5 rounded-[3px] border border-transparent bg-transparent px-2.5 py-1 text-[0.72rem] font-semibold text-dim transition hover:border-line hover:text-ink disabled:cursor-not-allowed disabled:opacity-45'

export function BrandMark({ className = '' }) {
  return (
    <span
      aria-hidden="true"
      className={cx(
        'grid h-8 w-8 shrink-0 place-items-center rounded-[9px] bg-amber shadow-[0_10px_30px_-12px_rgba(242,184,75,0.85)]',
        className,
      )}
    >
      <span className="grid grid-cols-2 gap-[3px]">
        <span className="h-[3px] w-[3px] rounded-full bg-canvas" />
        <span className="h-[3px] w-[3px] rounded-full bg-canvas/70" />
        <span className="h-[3px] w-[3px] rounded-full bg-canvas/70" />
        <span className="h-[3px] w-[3px] rounded-full bg-canvas" />
      </span>
    </span>
  )
}

export function SectionLabel({ children, className = '' }) {
  return (
    <span
      className={cx(
        'font-mono text-[0.6rem] font-medium tracking-[0.18em] uppercase',
        className || 'text-dim',
      )}
    >
      {children}
    </span>
  )
}

export function Panel({ id, title, hint, action, children, className = '', ariaLabel }) {
  const showHeader = title || hint || action
  return (
    <section
      id={id}
      aria-labelledby={title ? `${id}-title` : undefined}
      aria-label={title ? undefined : ariaLabel}
      className={cx(
        'ffd-section relative overflow-hidden rounded-2xl border border-line/80 bg-surface/80 p-5 shadow-[0_24px_70px_-45px_rgba(0,0,0,0.95)]',
        className,
      )}
    >
      {showHeader && (
        <div className="mb-4 flex flex-wrap items-baseline justify-between gap-x-3 gap-y-2">
          {title ? (
            <h2
              id={`${id}-title`}
              className="font-grotesk text-[1.02rem] font-bold tracking-[-0.01em] text-ink"
            >
              {title}
            </h2>
          ) : (
            <span />
          )}
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            {hint && <SectionLabel>{hint}</SectionLabel>}
            {action}
          </div>
        </div>
      )}
      {children}
    </section>
  )
}

export function StatCard({ label, children, note, meter, className = '' }) {
  return (
    <div
      className={cx(
        'ff-stat rounded-2xl border border-line/80 bg-surface/80 p-4 shadow-[0_24px_70px_-50px_rgba(0,0,0,0.95)]',
        className,
      )}
    >
      <SectionLabel>{label}</SectionLabel>
      <div className="mt-1.5 font-grotesk text-[1.65rem] leading-tight font-bold tracking-[-0.02em] text-ink">
        {children}
      </div>
      {meter !== undefined && (
        <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-deck">
          <div
            className="h-full rounded-full bg-amber transition-[width] duration-500"
            style={{ width: `${Math.max(0, Math.min(100, meter))}%` }}
          />
        </div>
      )}
      {note && <div className="mt-1.5 text-[0.72rem] leading-snug text-dim">{note}</div>}
    </div>
  )
}

export function CheckIcon({ className = '' }) {
  return (
    <svg
      viewBox="0 0 16 16"
      aria-hidden="true"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2.6"
    >
      <path d="m3.2 8.3 3.1 3.1 6.5-6.7" />
    </svg>
  )
}

export function MenuIcon({ open = false, className = '' }) {
  return (
    <svg
      viewBox="0 0 16 16"
      aria-hidden="true"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.7"
    >
      {open ? (
        <path d="m3.5 3.5 9 9M12.5 3.5l-9 9" />
      ) : (
        <path d="M2.5 4.25h11M2.5 8h11M2.5 11.75h11" />
      )}
    </svg>
  )
}

export function SparkIcon({ className = '' }) {
  return (
    <svg
      viewBox="0 0 16 16"
      aria-hidden="true"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.6"
    >
      <path d="M8 1.8 9.4 6l4.2 1.4-4.2 1.4L8 13l-1.4-4.2L2.4 7.4 6.6 6 8 1.8Z" />
    </svg>
  )
}

export function SendIcon({ className = '' }) {
  return (
    <svg
      viewBox="0 0 16 16"
      aria-hidden="true"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.6"
    >
      <path d="M2.3 2.6 14 8 2.3 13.4l1.1-4.6 6.1-1.8-6.1-1.8-1.1-2.6Z" />
    </svg>
  )
}
