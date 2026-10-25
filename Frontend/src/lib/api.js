const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '')

function getToken() {
  return localStorage.getItem('token') || sessionStorage.getItem('token')
}

export function setToken(token, persist = true) {
  localStorage.removeItem('token')
  sessionStorage.removeItem('token')
  if (!token) return
  if (persist) localStorage.setItem('token', token)
  else sessionStorage.setItem('token', token)
}

function firstMessage(value) {
  return typeof value === 'string' && value.trim() ? value : null
}

// The backend answers with `{"error": "..."}`, FastAPI validation failures with
// `{"detail": [...]}`, and plain HTTP errors with a status code. Reduce all of
// them to one readable sentence.
function errorMessage(data, status) {
  if (data && typeof data === 'object') {
    if (Array.isArray(data.detail)) {
      const messages = data.detail
        .map((item) => firstMessage(item?.msg) || firstMessage(item?.message))
        .filter(Boolean)
      if (messages.length) return messages.join(' ')
    }

    return (
      firstMessage(data.detail) ||
      firstMessage(data.error) ||
      firstMessage(data.message) ||
      `Request failed with status ${status}`
    )
  }

  return firstMessage(data) || `Request failed with status ${status}`
}

export async function api(path, { method = 'GET', body, headers = {}, signal } = {}) {
  const config = {
    method,
    signal,
    headers: {
      Accept: 'application/json',
      ...headers,
    },
  }

  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`

  if (body !== undefined) {
    config.headers['Content-Type'] = 'application/json'
    config.body = JSON.stringify(body)
  }

  const res = await fetch(`${BASE_URL}${path}`, config)

  if (res.status === 204) return null

  const text = await res.text()
  let data = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }

  // Some endpoints report failures in the body while still returning 200.
  const bodyError =
    data && typeof data === 'object' && !Array.isArray(data)
      ? firstMessage(data.error)
      : null

  if (!res.ok || bodyError) {
    if (res.status === 401 && getToken()) setToken(null)

    const error = new Error(errorMessage(data, res.status))
    error.status = res.status
    error.data = data
    throw error
  }

  return data
}

export const apiGet = (path, options) => api(path, { ...options, method: 'GET' })
export const apiPost = (path, body, options) => api(path, { ...options, method: 'POST', body })
export const apiPut = (path, body, options) => api(path, { ...options, method: 'PUT', body })
export const apiPatch = (path, body, options) => api(path, { ...options, method: 'PATCH', body })
export const apiDelete = (path, options) => api(path, { ...options, method: 'DELETE' })
