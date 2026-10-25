import { useState } from 'react'

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
          className={`w-full rounded-[3px] border border-line bg-deck px-3.5 py-2.5 text-[0.9rem] text-ink outline-none transition-colors placeholder:text-dim/60 focus:border-amber/60 focus:ring-2 focus:ring-amber/20 ${
            error ? 'border-coral/60' : ''
          } ${isPassword ? 'pr-14' : ''}`}
          {...registration}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShow((s) => !s)}
            aria-label={show ? 'Hide password' : 'Show password'}
            aria-pressed={show}
            className="absolute top-1/2 right-3 -translate-y-1/2 rounded-[3px] px-1.5 py-1 font-mono text-[0.7rem] text-dim uppercase transition-colors hover:text-ink"
          >
            {show ? 'Hide' : 'Show'}
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
