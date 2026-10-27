import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { apiPost } from '@/lib/api'
import { emailRules } from '@/lib/validation'
import usePageTitle from '@/lib/usePageTitle'
import AuthLayout from '@/components/AuthLayout'
import TextField from '@/components/TextField'
import SubmitButton from '@/components/SubmitButton'
import FormError from '@/components/FormError'

export default function ForgotPassword() {
  usePageTitle('Forgot password — FocusFlow')
  const [apiError, setApiError] = useState(null)
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm()

  const onSubmit = async (data) => {
    setApiError(null)
    try {
      await apiPost('/auth/forgot-password', { email: data.email })
      sessionStorage.setItem('pendingOtpEmail', data.email)
      sessionStorage.setItem('otpFlow', 'reset-password')
      sessionStorage.removeItem('otpCode')
      navigate('/verify-otp')
    } catch (err) {
      setApiError(err.message || 'Could not send reset code')
    }
  }

  return (
    <AuthLayout
      eyebrow="Account recovery"
      title="Forgot password?"
      subtitle="Enter your email and we'll send you a reset code"
      onSubmit={handleSubmit(onSubmit)}
      footer={
        <>
          Remember your password?{' '}
          <Link to="/login" className="font-medium text-amber hover:text-amber/80">
            Log in
          </Link>
        </>
      }
    >
      <TextField
        id="email"
        label="Email address"
        type="email"
        placeholder="you@example.com"
        autoComplete="email"
        error={errors.email}
        registration={register('email', emailRules)}
      />

      <FormError message={apiError} />

      <SubmitButton loading={isSubmitting} loadingText="Sending code...">
        Send reset code
      </SubmitButton>
    </AuthLayout>
  )
}
