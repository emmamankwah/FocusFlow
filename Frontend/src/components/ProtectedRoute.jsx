import { useEffect, useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { getToken, onUnauthorized } from '@/lib/api'
import { logout, validateSession } from '@/lib/auth'
import PageLoader from './PageLoader'

export default function ProtectedRoute({ children }) {
  const location = useLocation()
  const navigate = useNavigate()
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

  return (
    <>
      {children}
      <button
        type="button"
        onClick={() => {
          logout()
          navigate('/login', { replace: true })
        }}
        className="fixed top-4 right-4 z-[100] rounded-lg border border-line bg-surface px-3 py-2 font-mono text-[0.65rem] tracking-[0.12em] text-ink uppercase shadow-lg transition-colors hover:border-amber hover:text-amber focus-visible:ring-2 focus-visible:ring-amber/50 focus-visible:outline-none"
      >
        Log out
      </button>
    </>
  )
}
