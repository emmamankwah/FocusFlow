import { useEffect, useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { getToken, onUnauthorized } from '@/lib/api'
import { validateSession } from '@/lib/auth'
import PageLoader from './PageLoader'

export default function ProtectedRoute({ children }) {
  const location = useLocation()
  const [status, setStatus] = useState(() =>
    getToken() ? 'checking' : 'anonymous',
  )

  // Any API call that comes back 401 drops the session and sends the user to
  // the login page instead of leaving them on a half-working screen.
  useEffect(() => onUnauthorized(() => setStatus('anonymous')), [])

  useEffect(() => {
    if (status !== 'checking') return undefined

    let active = true
    validateSession().then((ok) => {
      if (active) setStatus(ok ? 'authenticated' : 'anonymous')
    })
    return () => {
      active = false
    }
  }, [status])

  if (status === 'anonymous') {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location.pathname + location.search }}
      />
    )
  }

  if (status === 'checking') return <PageLoader />

  return children
}
