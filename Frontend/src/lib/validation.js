// Shared react-hook-form rules so every password field enforces the same
// policy as the backend `PasswordValidation` model.

export const emailRules = {
  required: 'Email is required',
  pattern: { value: /^\S+@\S+$/i, message: 'Invalid email address' },
}

export const usernameRules = {
  required: 'Username is required',
  minLength: { value: 3, message: 'Must be at least 3 characters' },
  maxLength: { value: 30, message: 'Must be at most 30 characters' },
  pattern: {
    value: /^[A-Za-z0-9._-]+$/,
    message: 'Use letters, numbers, dots, dashes or underscores',
  },
}

export const passwordRules = {
  required: 'Password is required',
  minLength: { value: 8, message: 'Must be at least 8 characters' },
  maxLength: { value: 128, message: 'Must be at most 128 characters' },
  validate: (value) => {
    if (!value) return true
    const missing = []
    if (!/[A-Z]/.test(value)) missing.push('an uppercase letter')
    if (!/[a-z]/.test(value)) missing.push('a lowercase letter')
    if (!/\d/.test(value)) missing.push('a number')
    if (!/[^A-Za-z0-9]/.test(value)) missing.push('a special character')
    if (!missing.length) return true

    const list =
      missing.length === 1
        ? missing[0]
        : `${missing.slice(0, -1).join(', ')} and ${missing[missing.length - 1]}`
    return `Add ${list}`
  },
}

export const confirmPasswordRules = {
  required: 'Please confirm your password',
  validate: (value, values) =>
    value === values.password || 'Passwords do not match',
}

export const PASSWORD_HINT = '8+ characters with upper, lower, number & symbol.'
