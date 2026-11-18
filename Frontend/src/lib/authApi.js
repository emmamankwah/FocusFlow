import { apiGet, apiPost, getToken, setToken } from '@/lib/api'

const SESSION_USER_KEY = 'focusflow-session-user'
const PENDING_EMAIL_KEY = 'focusflow-pending-email'
const RESET_EMAIL_KEY = 'focusflow-reset-email'

const normalizeEmail = (email = '') => email.trim()

export function getSessionUser() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_USER_KEY))
  } catch {
    return null
  }
}

export function getPendingEmail() {
  return sessionStorage.getItem(PENDING_EMAIL_KEY) || ''
}

export function getResetContext() {
  return { email: sessionStorage.getItem(RESET_EMAIL_KEY) || '' }
}

export async function signup(values) {
  const result = await apiPost('/auth/register', {
    firstName: values.firstName,
    lastName: values.lastName,
    username: values.username,
    email: normalizeEmail(values.email),
    password: values.password,
    confirmPassword: values.confirmPassword,
  })
  sessionStorage.setItem(PENDING_EMAIL_KEY, normalizeEmail(values.email))
  return result
}

export async function login({ email, password, remember = true }) {
  const result = await apiPost('/auth/login', {
    email: normalizeEmail(email),
    password,
  })
  setToken(result.access_token, remember !== false)

  try {
    const user = await apiGet('/auth/profile')
    localStorage.setItem(SESSION_USER_KEY, JSON.stringify(user))
    return user
  } catch (error) {
    logout()
    throw error
  }
}

export async function verifyEmail(email, otp) {
  const result = await apiPost('/auth/verify-otp', { email, otp })
  sessionStorage.removeItem(PENDING_EMAIL_KEY)
  return result
}

export function resendVerification() {
  return apiPost('/auth/resend-otp', { email: getPendingEmail() })
}

export async function requestPasswordReset(email) {
  const normalizedEmail = normalizeEmail(email)
  const result = await apiPost('/auth/forgot-password', { email: normalizedEmail })
  sessionStorage.setItem(RESET_EMAIL_KEY, normalizedEmail)
  return { ...result, email: normalizedEmail }
}

export async function resetPassword({ email, otp, password }) {
  const result = await apiPost('/auth/reset-password', {
    email,
    otp,
    newPassword: password,
  })
  sessionStorage.removeItem(RESET_EMAIL_KEY)
  return result
}

export function logout() {
  setToken(null)
  localStorage.removeItem(SESSION_USER_KEY)
}

export async function validateSession() {
  if (!getToken()) return false
  try {
    const user = await apiGet('/auth/profile')
    localStorage.setItem(SESSION_USER_KEY, JSON.stringify(user))
    return true
  } catch {
    logout()
    return false
  }
}
