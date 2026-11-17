import { useEffect, useRef, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import usePageTitle from '@/lib/usePageTitle'
import { getPendingEmail, resendVerification, verifyEmail } from '@/lib/mockAuth'
import AuthLayout from '@/components/AuthLayout'
import SubmitButton from '@/components/SubmitButton'
import FormError from '@/components/FormError'

const COOLDOWN_SECONDS = 30

export default function VerifyEmail() {
  usePageTitle('Verify your email — FocusFlow')
  const navigate = useNavigate()
  // Read once: verifying clears the pending email, and re-reading would trip
  // the guard below mid-navigation.
  const [email] = useState(() => getPendingEmail())

  const [apiError, setApiError] = useState(null)
  const [notice, setNotice] = useState(null)
  const [verifying, setVerifying] = useState(false)
  const [resending, setResending] = useState(false)
  const [cooldown, setCooldown] = useState(COOLDOWN_SECONDS)
  const [resentAt, setResentAt] = useState(0)
  const timer = useRef(null)

  useEffect(() => {
    if (cooldown <= 0) return undefined
    timer.current = setTimeout(() => setCooldown((value) => value - 1), 1000)
    return () => clearTimeout(timer.current)
  }, [cooldown, resentAt])

  if (!email) return <Navigate to="/signup" replace />

  const handleVerify = async () => {
    setApiError(null)
    setVerifying(true)
    try {
      await verifyEmail(email)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setApiError(err.message || 'Could not verify this email.')
      setVerifying(false)
    }
  }

  const handleResend = async () => {
    setApiError(null)
    setNotice(null)
    setResending(true)
    try {
      await resendVerification()
      setNotice(`New verification link sent to ${email}.`)
      setCooldown(COOLDOWN_SECONDS)
      setResentAt((value) => value + 1)
    } catch (err) {
      setApiError(err.message || 'Could not resend the email.')
    } finally {
      setResending(false)
    }
  }

  return (
    <AuthLayout
      eyebrow="One more step"
      title="Verify your email"
      subtitle={`We sent a verification link to ${email}.`}
      brandTitle="Almost there"
      brandLead="Verify your address and FocusFlow will start building your first week."
      footer={
        <>
          Wrong address?{' '}
          <Link to="/signup" className="font-semibold text-cobalt underline underline-offset-4 hover:text-cobalt/80">
            Use a different email
          </Link>
        </>
      }
    >
      <div className="space-y-4">
        <div className="rounded-xl border border-cobalt/15 bg-cobalt/5 px-4 py-3.5 text-[0.84rem] leading-relaxed text-inkwell/75">
          <p className="font-semibold text-inkwell">{email}</p>
          <p className="mt-1">
            Open the link in that email to finish setting up. In this preview, no email is
            sent — verify instantly below.
          </p>
        </div>

        <FormError message={apiError} />

        {notice && (
          <p role="status" className="rounded-xl border border-[#2fa86a]/25 bg-[#2fa86a]/10 px-3.5 py-2.5 text-[0.8rem] font-medium text-[#1d7a4c]">
            {notice}
          </p>
        )}

        <form
          onSubmit={(event) => {
            event.preventDefault()
            handleVerify()
          }}
        >
          <SubmitButton loading={verifying} loadingText="Verifying...">
            Verify and continue
          </SubmitButton>
        </form>

        <button
          type="button"
          onClick={handleResend}
          disabled={resending || cooldown > 0}
          className="h-11 w-full rounded-xl border border-inkwell/20 bg-white text-[0.88rem] font-semibold text-inkwell transition-colors hover:border-inkwell/40 hover:bg-paper disabled:cursor-not-allowed disabled:opacity-55"
        >
          {resending
            ? 'Sending...'
            : cooldown > 0
              ? `Resend email in ${cooldown}s`
              : 'Resend email'}
        </button>
      </div>
    </AuthLayout>
  )
}
