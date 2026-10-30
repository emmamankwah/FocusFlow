// Shared react-hook-form rules. Password policy mirrors the live checklist in
// `components/PasswordChecklist.jsx`: 8+ characters, an uppercase letter, a
// number and a symbol.

export const emailRules = {
  required: 'Enter your email address.',
  pattern: {
    value: /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i,
    message: 'Enter a valid email address.',
  },
}

export const usernameRules = {
  required: 'Choose a username.',
  minLength: { value: 3, message: 'Use at least 3 characters.' },
  maxLength: { value: 30, message: 'Use at most 30 characters.' },
  pattern: {
    value: /^[A-Za-z0-9._-]+$/,
    message: 'Use letters, numbers, dots, dashes or underscores.',
  },
}

export const passwordRules = {
  required: 'Choose a password.',
  minLength: { value: 8, message: 'Use at least 8 characters.' },
  maxLength: { value: 128, message: 'Use at most 128 characters.' },
  validate: (value) => {
    if (!value) return true
    const missing = []
    if (!/[A-Z]/.test(value)) missing.push('an uppercase letter')
    if (!/\d/.test(value)) missing.push('a number')
    if (!/[^A-Za-z0-9]/.test(value)) missing.push('a symbol')
    if (!missing.length) return true

    const list =
      missing.length === 1
        ? missing[0]
        : `${missing.slice(0, -1).join(', ')} and ${missing[missing.length - 1]}`
    return `Add ${list}.`
  },
}

export const confirmPasswordRules = {
  required: 'Confirm your password.',
  validate: (value, values) =>
    value === values.password || 'Passwords do not match.',
}

export const PASSWORD_HINT = '8+ characters with an uppercase letter, a number and a symbol.'
