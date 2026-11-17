import { getToken } from '@/lib/api'
import { getSessionUser } from '@/lib/mockAuth'

// Frontend-only session check. A token without a stored account (or a stale
// token from the old backend sessions) counts as signed out, so guarded routes
// fail closed instead of rendering against missing data.
export function validateSession() {
  if (!getToken()) return Promise.resolve(false)
  return Promise.resolve(Boolean(getSessionUser()))
}
