import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { getToken } from '@/lib/api'
import { validateSession } from '@/lib/auth'
import PageLoader from './PageLoader'

// Auth pages stay public, but a signed-in visitor is sent to the dashboard.
export default function GuestRoute({ children }) {
  const [status, setStatus] = useState(() =>
    getToken() ? 'checking' : 'anonymous',
  )

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

  if (status === 'checking') return <PageLoader />
  if (status === 'authenticated') return <Navigate to="/dashboard" replace />

  return children
}
