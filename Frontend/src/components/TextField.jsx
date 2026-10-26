import { useState } from 'react'

function EyeIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-[18px] w-[18px]"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M2.1 12.35a1 1 0 0 1 0-.7C3.66 7.6 7.53 4.5 12 4.5s8.34 3.1 9.9 7.15a1 1 0 0 1 0 .7C20.34 16.4 16.47 19.5 12 19.5S3.66 16.4 2.1 12.35Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

function EyeOffIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-[18px] w-[18px]"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="m3 3 18 18" />
      <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
      <path d="M9.9 5.2A10.9 10.9 0 0 1 12 5c4.47 0 8.34 3.1 9.9 7.15a11.8 11.8 0 0 1-2.2 3.3" />
      <path d="M6.2 6.2A11.8 11.8 0 0 0 2.1 11.65a1 1 0 0 0 0 .7C3.66 16.4 7.53 19.5 12 19.5c1.4 0 2.7-.3 3.9-.8" />
    </svg>
  )
}

export default function TextField({
  id,
  label,
  type = 'text',
  placeholder,
  autoComplete,
  autoFocus,
  error,
  hint,
  registration,
}) {
  const [show, setShow] = useState(false)
  const isPassword = type === 'password'

  const describedBy =
    (error ? `${id}-error` : hint ? `${id}-hint` : null) || undefined

  return (
    <div>
      <label
        htmlFor={id}
        className="mb-1.5 block font-mono text-[0.7rem] tracking-[0.14em] text-dim uppercase"
      >
        {label}
      </label>
      <div className={isPassword ? 'relative' : undefined}>
        <input
          id={id}
          type={isPassword && show ? 'text' : type}
          placeholder={placeholder}
          autoComplete={autoComplete}
          autoFocus={autoFocus}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          className={`w-full rounded-xl border border-line bg-deck/80 px-3.5 py-2.5 text-[0.9rem] text-ink outline-none transition-all duration-200 placeholder:text-dim/60 hover:border-dim/70 focus:border-amber/60 focus:bg-deck focus:ring-4 focus:ring-amber/10 ${
            error ? 'border-coral/60' : ''
          } ${isPassword ? 'pr-11' : ''}`}
          {...registration}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShow((s) => !s)}
            aria-label={show ? 'Hide password' : 'Show password'}
            aria-pressed={show}
            title={show ? 'Hide password' : 'Show password'}
            className="absolute top-1/2 right-1.5 grid h-8 w-8 -translate-y-1/2 place-items-center rounded-lg text-dim transition-colors hover:bg-line/40 hover:text-ink focus-visible:ring-2 focus-visible:ring-amber/30"
          >
            {show ? <EyeOffIcon /> : <EyeIcon />}
          </button>
        )}
      </div>
      {hint && !error && (
        <p id={`${id}-hint`} className="mt-1.5 text-[0.72rem] text-dim">
          {hint}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} className="mt-1.5 text-[0.75rem] text-coral">
          {error.message}
        </p>
      )}
    </div>
  )
}
