import { apiGet, apiPost, getToken, setToken } from '@/lib/api'

const SESSION_USER_KEY = 'focusflow-session-user'
const PENDING_EMAIL_KEY = 'focusflow-pending-email'
const RESET_EMAIL_KEY = 'focusflow-reset-email'

function saveUser(user) {
  localStorage.setItem(SESSION_USER_KEY, JSON.stringify(user))
  return user
}

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
  return {
    email: sessionStorage.getItem(RESET_EMAIL_KEY) || '',
  }
}

export async function signup(values) {
  await apiPost('/auth/register', {
    firstName: values.firstName,
    lastName: values.lastName,
    username: values.username,
    email: values.email,
    password: values.password,
    confirmPassword: values.confirmPassword,
  })
  sessionStorage.setItem(PENDING_EMAIL_KEY, values.email.trim())
}

export async function verifyEmail(email, otp) {
  const result = await apiPost('/auth/verify-otp', { email, otp })
  sessionStorage.removeItem(PENDING_EMAIL_KEY)
  return result
}

export function resendVerification(email = getPendingEmail()) {
  return apiPost('/auth/resend-otp', { email })
}

export async function login({ email, password, remember = true }) {
  const result = await apiPost('/auth/login', { email, password })
  if (!result?.access_token) throw new Error('The server did not return an access token.')
  setToken(result.access_token, remember !== false)
  try {
    const profile = await apiGet('/auth/profile')
    return saveUser(profile)
  } catch (error) {
    setToken(null)
    throw error
  }
}

export function logout() {
  setToken(null)
  localStorage.removeItem(SESSION_USER_KEY)
}

export async function requestPasswordReset(email) {
  await apiPost('/auth/forgot-password', { email })
  const normalizedEmail = email.trim()
  sessionStorage.setItem(RESET_EMAIL_KEY, normalizedEmail)
  return { email: normalizedEmail }
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

export async function validateSession() {
  if (!getToken()) return false
  try {
    saveUser(await apiGet('/auth/profile'))
    return true
  } catch {
    logout()
    return false
  }
}
