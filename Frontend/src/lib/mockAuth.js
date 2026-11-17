// Frontend-only authentication for the design demo.
//
// Accounts live in localStorage and passwords are stored as SHA-256 digests.
// Nothing here is a replacement for the real API: when the backend is
// connected, swap these functions for the calls in `lib/api.js` and keep the
// same return shapes so the screens do not change.

import { setToken } from '@/lib/api'

const USERS_KEY = 'focusflow-users'
const SESSION_USER_KEY = 'focusflow-session-user'
const PENDING_EMAIL_KEY = 'focusflow-pending-email'
const RESET_EMAIL_KEY = 'focusflow-reset-email'
const RESET_TOKEN_KEY = 'focusflow-reset-token'

const wait = (ms = 500) => new Promise((resolve) => setTimeout(resolve, ms))

function readUsers() {
  try {
    const parsed = JSON.parse(localStorage.getItem(USERS_KEY))
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function writeUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users))
}

async function sha256(text) {
  const buffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text))
  return [...new Uint8Array(buffer)]
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('')
}

const normalize = (value = '') => value.trim().toLowerCase()

function publicUser({ passwordHash, ...user }) {
  return user
}

function startSession(user, persist = true) {
  setToken(crypto.randomUUID(), persist)
  localStorage.setItem(SESSION_USER_KEY, JSON.stringify(user))
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

export function setPendingEmail(email) {
  sessionStorage.setItem(PENDING_EMAIL_KEY, normalize(email))
}

export function getResetContext() {
  return {
    email: sessionStorage.getItem(RESET_EMAIL_KEY) || '',
    token: sessionStorage.getItem(RESET_TOKEN_KEY) || '',
  }
}

export async function signup(values) {
  await wait(650)

  const users = readUsers()
  const email = normalize(values.email)
  const username = values.username.trim()

  if (users.some((user) => user.email === email)) {
    throw new Error('An account with this email already exists. Log in instead.')
  }
  if (users.some((user) => user.username.toLowerCase() === username.toLowerCase())) {
    throw new Error('That username is taken. Try another.')
  }

  const record = {
    id: crypto.randomUUID(),
    firstName: values.firstName.trim(),
    lastName: values.lastName.trim(),
    username,
    email,
    persona: values.persona || 'Student',
    peakTime: values.peakTime || 'morning',
    verified: false,
    createdAt: new Date().toISOString(),
    passwordHash: await sha256(values.password),
  }

  writeUsers([...users, record])
  setPendingEmail(email)
  return publicUser(record)
}

export async function resendVerification() {
  await wait(450)
  return true
}

export async function verifyEmail(email) {
  await wait(600)

  const target = normalize(email || getPendingEmail())
  const users = readUsers()
  const index = users.findIndex((user) => user.email === target)
  if (index === -1) throw new Error('We could not find that account. Create it again.')

  users[index] = { ...users[index], verified: true }
  writeUsers(users)
  sessionStorage.removeItem(PENDING_EMAIL_KEY)

  const user = publicUser(users[index])
  startSession(user, true)
  return user
}

export async function login({ email, password, remember = true }) {
  await wait(600)

  const user = readUsers().find((item) => item.email === normalize(email))
  if (!user || user.passwordHash !== (await sha256(password))) {
    throw new Error('Email or password is incorrect. Check both and try again.')
  }

  if (!user.verified) {
    const error = new Error('Verify your email address to finish setting up your account.')
    error.code = 'unverified'
    error.email = user.email
    throw error
  }

  const sessionUser = publicUser(user)
  startSession(sessionUser, remember !== false)
  return sessionUser
}

export function logout() {
  setToken(null)
  localStorage.removeItem(SESSION_USER_KEY)
}

export async function requestPasswordReset(email) {
  await wait(600)

  const target = normalize(email)
  sessionStorage.setItem(RESET_EMAIL_KEY, target)
  sessionStorage.setItem(RESET_TOKEN_KEY, crypto.randomUUID())
  return { email: target }
}

export async function resetPassword({ email, password }) {
  await wait(650)

  const context = getResetContext()
  const target = normalize(email || context.email)
  if (!context.token || target !== context.email) {
    throw new Error('This reset link has expired. Request a new one.')
  }

  const users = readUsers()
  const index = users.findIndex((user) => user.email === target)
  if (index === -1) throw new Error('No account was found for this email.')

  users[index] = {
    ...users[index],
    verified: true,
    passwordHash: await sha256(password),
  }
  writeUsers(users)

  sessionStorage.removeItem(RESET_EMAIL_KEY)
  sessionStorage.removeItem(RESET_TOKEN_KEY)
  return publicUser(users[index])
}
