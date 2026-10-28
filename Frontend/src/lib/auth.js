import { apiGet, getToken } from '@/lib/api'

// Fail closed: a missing token, a 401, an HTTP error, or an unreachable
// backend all count as "not signed in". Nothing is cached, so every guarded
// route mount checks the API again.
export function validateSession() {
  if (!getToken()) return Promise.resolve(false)

  return apiGet('/auth/profile')
    .then(() => true)
    .catch(() => false)
}
