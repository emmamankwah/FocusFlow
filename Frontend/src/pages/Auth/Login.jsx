import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { apiPost, setToken } from '@/lib/api'
import { emailRules } from '@/lib/validation'
import AuthLayout from '@/components/AuthLayout'
import TextField from '@/components/TextField'
import Checkbox from '@/components/Checkbox'
import SubmitButton from '@/components/SubmitButton'
import FormError from '@/components/FormError'

export default function Login() {
  const [apiError, setApiError] = useState(null)
  const navigate = useNavigate()
  const { state } = useLocation()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ defaultValues: { remember: false } })

  const onSubmit = async (data) => {
    setApiError(null)
    try {
      const res = await apiPost('/auth/login', {
        email: data.email,
        password: data.password,
      })
      const token = res?.token || res?.access_token
      if (token) setToken(token, data.remember)
      navigate('/')
    } catch (err) {
      setApiError(err.message || 'Login failed')
    }
  }

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Log in to your account"
      onSubmit={handleSubmit(onSubmit)}
      footer={
        <>
          Don&apos;t have an account?{' '}
          <Link to="/signup" className="font-medium text-amber hover:text-amber/80">
            Sign up
          </Link>
        </>
      }
    >
      {state?.verified && (
        <p
          role="status"
          className="rounded-[3px] border border-cyan/30 bg-cyan/10 px-3.5 py-2.5 text-[0.8rem] text-cyan"
        >
          Email verified — log in to continue.
        </p>
      )}

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
        autoComplete="current-password"
        error={errors.password}
        registration={register('password', {
          required: 'Password is required',
        })}
      />

      <FormError message={apiError} />

      <div className="flex items-center justify-between gap-4">
        <Checkbox id="remember" label="Remember me" registration={register('remember')} />
        <Link to="/forgot-password" className="font-medium text-amber hover:text-amber/80">
          Forgot password?
        </Link>
      </div>

      <SubmitButton loading={isSubmitting} loadingText="Logging in...">
        Log in
      </SubmitButton>
    </AuthLayout>
  )
}
