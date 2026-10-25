import { useEffect, useRef, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { apiPost, setToken } from '@/lib/api'
import FormError from '@/components/FormError'

const LENGTH = 6

export default function VerifyOtp() {
  const [otp, setOtp] = useState(Array(LENGTH).fill(''))
  const [apiError, setApiError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [resending, setResending] = useState(false)
  const [resendMsg, setResendMsg] = useState(null)
  const [cooldown, setCooldown] = useState(0)
  const inputs = useRef([])
  const navigate = useNavigate()

  const [email] = useState(() => sessionStorage.getItem('pendingOtpEmail') || '')
  const [flow] = useState(() => sessionStorage.getItem('otpFlow'))

  useEffect(() => {
    if (cooldown <= 0) return
    const timer = setTimeout(() => setCooldown((c) => c - 1), 1000)
    return () => clearTimeout(timer)
  }, [cooldown])

  if (!email) {
    return (
      <Navigate to={flow === 'reset-password' ? '/forgot-password' : '/signup'} replace />
    )
  }

  const handleChange = (index, value) => {
    if (!/^\d*$/.test(value)) return

    const next = [...otp]
    next[index] = value.slice(-1)
    setOtp(next)

    if (value && index < LENGTH - 1) {
      inputs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputs.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e) => {
    e.preventDefault()
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, LENGTH)
    if (!pasted) return

    const next = [...otp]
    for (let i = 0; i < pasted.length; i++) next[i] = pasted[i]
    setOtp(next)
    inputs.current[Math.min(pasted.length, LENGTH - 1)]?.focus()
  }

  const handleResend = async () => {
    setResending(true)
    setResendMsg(null)
    try {
      await apiPost('/auth/resend-otp', { email })
      setResendMsg({ type: 'success', text: 'A new code is on its way.' })
      setCooldown(30)
    } catch (err) {
      setResendMsg({ type: 'error', text: err.message || 'Could not resend code' })
    } finally {
      setResending(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const code = otp.join('')
    setApiError(null)

    if (flow === 'reset-password') {
      sessionStorage.setItem('otpCode', code)
      navigate('/reset-password')
      return
    }

    setIsSubmitting(true)
    try {
      const res = await apiPost('/auth/verify-otp', { email, otp: code })
      const token = res?.token || res?.access_token
      sessionStorage.removeItem('pendingOtpEmail')
      sessionStorage.removeItem('otpFlow')

      if (token) {
        setToken(token)
        navigate('/')
      } else {
        navigate('/login', { state: { verified: true } })
      }
    } catch (err) {
      setApiError(err.message || 'Verification failed')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="relative grid min-h-screen place-items-center overflow-hidden bg-canvas px-6 py-16 font-grotesk text-ink">
      <div aria-hidden className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -left-32 h-[480px] w-[480px] rounded-full bg-amber/10 blur-3xl" />
        <div className="absolute right-[-160px] bottom-[-160px] h-[460px] w-[460px] rounded-full bg-coral/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md text-center">
        <div className="mb-8">
          <h1 className="text-[1.75rem] font-bold tracking-[-0.01em]">Verify your email</h1>
          <p className="mt-2.5 text-[0.9rem] text-dim">
            We&apos;ve sent a 6-digit code to <span className="text-ink">{email}</span>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="flex justify-center gap-3" onPaste={handlePaste}>
            {otp.map((digit, i) => (
              <input
                key={i}
                ref={(el) => (inputs.current[i] = el)}
                type="text"
                inputMode="numeric"
                autoComplete={i === 0 ? 'one-time-code' : 'off'}
                maxLength={1}
                value={digit}
                autoFocus={i === 0}
                onChange={(e) => handleChange(i, e.target.value)}
                onKeyDown={(e) => handleKeyDown(i, e)}
                aria-label={`Digit ${i + 1}`}
                aria-invalid={apiError ? true : undefined}
                className="h-14 w-12 rounded-[3px] border border-line bg-deck text-center font-mono text-lg text-ink outline-none transition-colors focus:border-amber/60 focus:ring-2 focus:ring-amber/20 sm:h-16 sm:w-14"
              />
            ))}
          </div>

          <FormError message={apiError} />

          {resendMsg && (
            <p
              role="status"
              className={`rounded-[3px] border px-3.5 py-2.5 text-[0.8rem] ${
                resendMsg.type === 'success'
                  ? 'border-cyan/30 bg-cyan/10 text-cyan'
                  : 'border-coral/30 bg-coral/10 text-coral'
              }`}
            >
              {resendMsg.text}
            </p>
          )}

          <button
            type="submit"
            className="btn btn-primary w-full justify-center disabled:cursor-not-allowed disabled:opacity-50"
            disabled={otp.some((d) => !d) || isSubmitting}
          >
            {isSubmitting ? 'Verifying...' : 'Verify'}
          </button>
        </form>

        <p className="mt-6 text-[0.86rem] text-dim">
          Didn&apos;t receive a code?{' '}
          <button
            type="button"
            onClick={handleResend}
            disabled={resending || cooldown > 0}
            className="font-medium text-amber transition-colors hover:text-amber/80 disabled:cursor-not-allowed disabled:text-dim/50"
          >
            {resending ? 'Sending...' : cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend'}
          </button>
        </p>

        <button
          type="button"
          onClick={() => navigate(-1)}
          className="mt-4 font-mono text-[0.72rem] text-dim uppercase transition-colors hover:text-ink"
        >
          ← Back
        </button>
      </div>
    </main>
  )
}
