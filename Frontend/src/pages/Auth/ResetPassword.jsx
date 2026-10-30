import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { confirmPasswordRules, passwordRules } from '@/lib/validation'
import usePageTitle from '@/lib/usePageTitle'
import { getResetContext, resetPassword } from '@/lib/mockAuth'
import AuthLayout from '@/components/AuthLayout'
import TextField from '@/components/TextField'
import SubmitButton from '@/components/SubmitButton'
import FormError from '@/components/FormError'
import PasswordChecklist from '@/components/PasswordChecklist'

export default function ResetPassword() {
  usePageTitle('Set a new password — FocusFlow')
  const [apiError, setApiError] = useState(null)
  const navigate = useNavigate()
  // Read once: a successful reset clears this context, and re-reading on the
  // next render would trip the guard and bounce back to /forgot-password.
  const [context] = useState(() => getResetContext())

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm({ defaultValues: { password: '', confirmPassword: '' } })

  const password = watch('password')

  if (!context.email || !context.token) {
    return <Navigate to="/forgot-password" replace />
  }

  const onSubmit = async (data) => {
    setApiError(null)
    try {
      await resetPassword({ email: context.email, password: data.password })
      navigate('/login', { replace: true, state: { reset: true } })
    } catch (err) {
      setApiError(err.message || 'Could not reset your password.')
    }
  }

  return (
    <AuthLayout
      eyebrow="Account recovery"
      title="Set a new password"
      subtitle={`Choose a new password for ${context.email}.`}
      brandTitle="Fresh start"
      brandLead="Pick something strong — your plan is right where you left it."
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
        <div>
          <TextField
            id="password"
            label="New password"
            type="password"
            placeholder="Create a password"
            autoComplete="new-password"
            error={errors.password}
            describedBy="password-rules"
            registration={register('password', passwordRules)}
          />
          <PasswordChecklist value={password} />
        </div>

        <TextField
          id="confirmPassword"
          label="Confirm new password"
          type="password"
          placeholder="Repeat your password"
          autoComplete="new-password"
          error={errors.confirmPassword}
          registration={register('confirmPassword', confirmPasswordRules)}
        />

        <FormError message={apiError} />

        <SubmitButton loading={isSubmitting} loadingText="Updating...">
          Update password
        </SubmitButton>
      </form>
    </AuthLayout>
  )
}
