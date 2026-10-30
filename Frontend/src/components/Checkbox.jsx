export default function Checkbox({ id, label, registration }) {
  return (
    <label
      htmlFor={id}
      className="group inline-flex cursor-pointer items-center gap-2.5 select-none"
    >
      <input id={id} type="checkbox" className="peer sr-only" {...registration} />
      <span
        aria-hidden
        className="grid h-[20px] w-[20px] shrink-0 place-items-center rounded-md border-[1.5px] border-inkwell/30 bg-white text-transparent transition-colors peer-checked:border-cobalt peer-checked:bg-cobalt peer-checked:text-white peer-focus-visible:ring-2 peer-focus-visible:ring-cobalt/30 peer-focus-visible:ring-offset-2 group-hover:border-inkwell/50"
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
      <span className="text-[0.84rem] text-inkwell/70 transition-colors group-hover:text-inkwell">
        {label}
      </span>
    </label>
  )
}
