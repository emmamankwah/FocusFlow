import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { emailRules } from '@/lib/validation'
import usePageTitle from '@/lib/usePageTitle'
import { requestPasswordReset } from '@/lib/mockAuth'
import AuthLayout from '@/components/AuthLayout'
import TextField from '@/components/TextField'
import SubmitButton from '@/components/SubmitButton'
import FormError from '@/components/FormError'

export default function ForgotPassword() {
  usePageTitle('Forgot password — FocusFlow')
  const [apiError, setApiError] = useState(null)
  const [sentTo, setSentTo] = useState('')
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ defaultValues: { email: '' } })

  const onSubmit = async (data) => {
    setApiError(null)
    try {
      const { email } = await requestPasswordReset(data.email)
      setSentTo(email)
    } catch (err) {
      setApiError(err.message || 'Could not send the reset link.')
    }
  }

  if (sentTo) {
    return (
      <AuthLayout
        eyebrow="Check your inbox"
        title="Check your inbox"
        subtitle={`If an account exists for ${sentTo}, a reset link is on its way.`}
        brandTitle="Back in a minute"
        brandLead="The link works for 30 minutes. If nothing arrives, check your spam folder."
        footer={
          <>
            Remember your password?{' '}
            <Link to="/login" className="font-semibold text-cobalt underline underline-offset-4 hover:text-cobalt/80">
              Back to log in
            </Link>
          </>
        }
      >
        <div className="space-y-4">
          <div className="rounded-xl border border-cobalt/15 bg-cobalt/5 px-4 py-3.5 text-[0.84rem] leading-relaxed text-inkwell/75">
            <p>
              This is a preview, so no email is sent. Open the reset link below to set a new
              password.
            </p>
          </div>

          <button
            type="button"
            onClick={() => navigate('/reset-password')}
            className="group inline-flex h-12 w-full items-center justify-center gap-2.5 rounded-xl bg-cobalt px-5 text-[0.95rem] font-semibold text-white shadow-[0_18px_36px_-20px_rgba(47,69,255,0.85)] transition-all duration-200 hover:-translate-y-px hover:bg-[#2438e6]"
          >
            Open reset link
            <svg
              viewBox="0 0 16 16"
              className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M2.5 8h11M9 3.5 13.5 8 9 12.5" />
            </svg>
          </button>

          <button
            type="button"
            onClick={() => setSentTo('')}
            className="h-11 w-full rounded-xl border border-inkwell/20 bg-white text-[0.88rem] font-semibold text-inkwell transition-colors hover:border-inkwell/40 hover:bg-paper"
          >
            Use a different email
          </button>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      eyebrow="Account recovery"
      title="Forgot password?"
      subtitle="Enter your email and we'll send you a reset link."
      brandTitle="Locked out?"
      brandLead="A reset link gets you back to your plan in under a minute."
      footer={
        <>
          Remember your password?{' '}
          <Link to="/login" className="font-semibold text-cobalt underline underline-offset-4 hover:text-cobalt/80">
            Back to log in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        <TextField
          id="email"
          label="Email"
          type="email"
          placeholder="you@school.edu"
          autoComplete="email"
          error={errors.email}
          registration={register('email', emailRules)}
        />

        <FormError message={apiError} />

        <SubmitButton loading={isSubmitting} loadingText="Sending link...">
          Send reset link
        </SubmitButton>
      </form>
    </AuthLayout>
  )
}
