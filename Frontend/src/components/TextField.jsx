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
  describedBy,
  registration,
}) {
  const [show, setShow] = useState(false)
  const isPassword = type === 'password'

  const describedByIds =
    [error ? `${id}-error` : null, hint ? `${id}-hint` : null, describedBy]
      .filter(Boolean)
      .join(' ') || undefined

  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-[0.85rem] font-semibold text-inkwell">
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
          aria-describedby={describedByIds}
          className={`h-12 w-full rounded-xl border bg-white px-3.5 text-[0.95rem] text-inkwell outline-none transition-all duration-200 placeholder:text-inkwell/40 hover:border-inkwell/40 focus:border-cobalt focus:ring-4 focus:ring-cobalt/15 ${
            error ? 'border-[#b42318]' : 'border-inkwell/20'
          } ${isPassword ? 'pr-12' : ''}`}
          {...registration}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShow((state) => !state)}
            aria-label={show ? 'Hide password' : 'Show password'}
            aria-pressed={show}
            title={show ? 'Hide password' : 'Show password'}
            className="absolute top-1/2 right-1.5 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-lg text-inkwell/55 transition-colors hover:bg-cobalt/5 hover:text-inkwell focus-visible:ring-2 focus-visible:ring-cobalt/30"
          >
            {show ? <EyeOffIcon /> : <EyeIcon />}
          </button>
        )}
      </div>
      {hint && !error && (
        <p id={`${id}-hint`} className="mt-1.5 text-[0.76rem] text-inkwell/60">
          {hint}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} role="alert" className="mt-1.5 text-[0.76rem] font-medium text-[#b42318]">
          {error.message}
        </p>
      )}
    </div>
  )
}
