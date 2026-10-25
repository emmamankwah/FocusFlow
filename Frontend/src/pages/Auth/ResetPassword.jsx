import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { apiPost, setToken } from '@/lib/api'
import { passwordRules, confirmPasswordRules, PASSWORD_HINT } from '@/lib/validation'
import AuthLayout from '@/components/AuthLayout'
import TextField from '@/components/TextField'
import SubmitButton from '@/components/SubmitButton'
import FormError from '@/components/FormError'

export default function ResetPassword() {
  const [apiError, setApiError] = useState(null)
  const navigate = useNavigate()

  const [email] = useState(() => sessionStorage.getItem('pendingOtpEmail') || '')
  const [otp] = useState(() => sessionStorage.getItem('otpCode') || '')
  const [flow] = useState(() => sessionStorage.getItem('otpFlow'))

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm()

  const onSubmit = async (data) => {
    setApiError(null)
    try {
      await apiPost('/auth/reset-password', {
        email,
        otp,
        newPassword: data.password,
      })
      sessionStorage.removeItem('pendingOtpEmail')
      sessionStorage.removeItem('otpCode')
      sessionStorage.removeItem('otpFlow')
      navigate('/login')
    } catch (err) {
      setApiError(err.message || 'Could not reset password')
    }
  }

  if (!email || !otp || flow !== 'reset-password') {
    return <Navigate to="/forgot-password" replace />
  }

  return (
    <AuthLayout
      title="Set new password"
      subtitle="Choose a strong password for your account"
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
        id="password"
        label="New password"
        type="password"
        placeholder="••••••••"
        autoComplete="new-password"
        hint={PASSWORD_HINT}
        error={errors.password}
        registration={register('password', passwordRules)}
      />

      <TextField
        id="confirmPassword"
        label="Confirm new password"
        type="password"
        placeholder="••••••••"
        autoComplete="new-password"
        error={errors.confirmPassword}
        registration={register('confirmPassword', confirmPasswordRules)}
      />

      <FormError message={apiError} />

      <SubmitButton loading={isSubmitting} loadingText="Resetting...">
        Reset password
      </SubmitButton>
    </AuthLayout>
  )
}
