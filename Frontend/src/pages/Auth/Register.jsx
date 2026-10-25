import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { apiPost } from '@/lib/api'
import {
  emailRules,
  passwordRules,
  confirmPasswordRules,
  usernameRules,
  PASSWORD_HINT,
} from '@/lib/validation'
import AuthLayout from '@/components/AuthLayout'
import TextField from '@/components/TextField'
import SubmitButton from '@/components/SubmitButton'
import FormError from '@/components/FormError'

export default function Register() {
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
      await apiPost('/auth/register', {
        firstName: data.firstName,
        lastName: data.lastName,
        username: data.username,
        email: data.email,
        password: data.password,
        confirmPassword: data.confirmPassword,
      })
      sessionStorage.removeItem('otpFlow')
      sessionStorage.removeItem('otpCode')
      sessionStorage.setItem('pendingOtpEmail', data.email)
      navigate('/verify-otp')
    } catch (err) {
      setApiError(err.message || 'Registration failed')
    }
  }

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start planning smarter today"
      onSubmit={handleSubmit(onSubmit)}
      footer={
        <>
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-amber hover:text-amber/80">
            Log in
          </Link>
        </>
      }
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <TextField
          id="firstName"
          label="First name"
          placeholder="John"
          autoComplete="given-name"
          error={errors.firstName}
          registration={register('firstName', { required: 'First name is required' })}
        />
        <TextField
          id="lastName"
          label="Last name"
          placeholder="Doe"
          autoComplete="family-name"
          error={errors.lastName}
          registration={register('lastName', { required: 'Last name is required' })}
        />
      </div>

      <TextField
        id="username"
        label="Username"
        placeholder="john_doe"
        autoComplete="username"
        error={errors.username}
        registration={register('username', usernameRules)}
      />

      <TextField
        id="email"
        label="Email address"
        type="email"
        placeholder="you@example.com"
        autoComplete="email"
        error={errors.email}
        registration={register('email', emailRules)}
      />

      <TextField
        id="password"
        label="Password"
        type="password"
        placeholder="••••••••"
        autoComplete="new-password"
        hint={PASSWORD_HINT}
        error={errors.password}
        registration={register('password', passwordRules)}
      />

      <TextField
        id="confirmPassword"
        label="Confirm password"
        type="password"
        placeholder="••••••••"
        autoComplete="new-password"
        error={errors.confirmPassword}
        registration={register('confirmPassword', confirmPasswordRules)}
      />

      <FormError message={apiError} />

      <SubmitButton loading={isSubmitting} loadingText="Creating account...">
        Create account
      </SubmitButton>
    </AuthLayout>
  )
}
