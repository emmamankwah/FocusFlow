const RULES = [
  { key: 'length', label: '8+ characters', test: (value) => value.length >= 8 },
  { key: 'upper', label: 'An uppercase letter', test: (value) => /[A-Z]/.test(value) },
  { key: 'number', label: 'A number', test: (value) => /\d/.test(value) },
  { key: 'symbol', label: 'A symbol', test: (value) => /[^A-Za-z0-9]/.test(value) },
]

const COLORS = ['bg-rose', 'bg-blush', 'bg-lilac', 'bg-[#2fa86a]']

export default function PasswordChecklist({ value = '', id = 'password-rules' }) {
  const score = RULES.filter((rule) => rule.test(value)).length

  return (
    <div id={id} className="mt-2.5">
      <div className="flex gap-1.5" aria-hidden="true">
        {RULES.map((rule, index) => (
          <span
            key={rule.key}
            className={`h-1.5 flex-1 rounded-full transition-colors ${
              value && index < score ? COLORS[score - 1] : 'bg-inkwell/10'
            }`}
          />
        ))}
      </div>

      <ul className="mt-2.5 grid grid-cols-2 gap-x-4 gap-y-1">
        {RULES.map((rule) => {
          const ok = rule.test(value)
          return (
            <li
              key={rule.key}
              className={`flex items-center gap-1.5 text-[0.74rem] ${
                ok ? 'text-inkwell' : 'text-inkwell/50'
              }`}
            >
              <span
                aria-hidden="true"
                className={`grid h-3.5 w-3.5 shrink-0 place-items-center rounded-full border transition-colors ${
                  ok ? 'border-[#2fa86a] bg-[#2fa86a] text-white' : 'border-inkwell/30'
                }`}
              >
                {ok && (
                  <svg viewBox="0 0 12 12" className="h-2 w-2" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="m2 6.2 2.4 2.4L10 3.2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </span>
              {rule.label}
            </li>
          )
        })}
      </ul>

      <p className="sr-only" aria-live="polite">
        {value ? `${score} of 4 password requirements met.` : ''}
      </p>
    </div>
  )
}
