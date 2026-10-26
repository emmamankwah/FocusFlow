export default function Checkbox({ id, label, registration }) {
  return (
    <label
      htmlFor={id}
      className="group inline-flex cursor-pointer items-center gap-2.5 select-none"
    >
      <input id={id} type="checkbox" className="peer sr-only" {...registration} />
      <span
        aria-hidden
        className="grid h-[18px] w-[18px] shrink-0 place-items-center rounded-md border border-line bg-deck text-transparent transition-colors peer-checked:border-amber peer-checked:bg-amber peer-checked:text-[#171205] peer-focus-visible:ring-2 peer-focus-visible:ring-amber/30 peer-focus-visible:ring-offset-2 peer-focus-visible:ring-offset-surface group-hover:border-dim"
      >
        <svg
          viewBox="0 0 16 16"
          className="h-3 w-3"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="m3.2 8.4 3.1 3.1 6.5-7" />
        </svg>
      </span>
      <span className="text-[0.8rem] text-dim transition-colors group-hover:text-ink">
        {label}
      </span>
    </label>
  )
}
