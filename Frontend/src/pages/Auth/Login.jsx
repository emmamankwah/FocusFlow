import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { emailRules } from '@/lib/validation'
import usePageTitle from '@/lib/usePageTitle'
import { login, setPendingEmail } from '@/lib/mockAuth'
import AuthLayout from '@/components/AuthLayout'
import TextField from '@/components/TextField'
import Checkbox from '@/components/Checkbox'
import SubmitButton from '@/components/SubmitButton'
import FormError from '@/components/FormError'
import Divider from '@/components/Divider'
import GoogleButton from '@/components/GoogleButton'

export default function Login() {
  usePageTitle('Log in — FocusFlow')
  const [apiError, setApiError] = useState(null)
  const [notice, setNotice] = useState(null)
  const navigate = useNavigate()
  const { state } = useLocation()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ defaultValues: { email: '', password: '', remember: true } })

  const onSubmit = async (data) => {
    setApiError(null)
    setNotice(null)

    try {
      await login(data)
      navigate(state?.from || '/dashboard', { replace: true })
    } catch (err) {
      if (err.code === 'unverified') {
        setPendingEmail(err.email)
        navigate('/verify-email', { replace: true })
        return
      }
      setApiError(err.message || 'Login failed')
    }
  }

  return (
    <AuthLayout
      eyebrow="Account access"
      title="Welcome back"
      subtitle="Pick up where you left off."
      brandTitle="Your plan is waiting"
      brandLead="Log in to see what is due, what moved, and what to do next."
      footer={
        <>
          New here?{' '}
          <Link to="/signup" className="font-semibold text-cobalt underline underline-offset-4 hover:text-cobalt/80">
            Create an account
          </Link>
        </>
      }
    >
      {state?.reset && (
        <p
          role="status"
          className="rounded-xl border border-[#2fa86a]/25 bg-[#2fa86a]/10 px-3.5 py-2.5 text-[0.82rem] font-medium text-[#1d7a4c]"
        >
          Password updated. Log in with your new password.
        </p>
      )}

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

        <TextField
          id="password"
          label="Password"
          type="password"
          placeholder="Your password"
          autoComplete="current-password"
          error={errors.password}
          registration={register('password', { required: 'Enter your password.' })}
        />

        <div className="flex flex-wrap items-center justify-between gap-3">
          <Checkbox id="remember" label="Keep me signed in" registration={register('remember')} />
          <Link
            to="/forgot-password"
            className="text-[0.84rem] font-semibold text-cobalt underline underline-offset-4 hover:text-cobalt/80"
          >
            Forgot password?
          </Link>
        </div>

        <FormError message={apiError} />

        {notice && (
          <p role="status" className="rounded-xl border border-cobalt/15 bg-cobalt/5 px-3.5 py-2.5 text-[0.8rem] text-inkwell/75">
            {notice}
          </p>
        )}

        <SubmitButton loading={isSubmitting} loadingText="Logging in...">
          Log in
        </SubmitButton>
      </form>

      <div className="my-5">
        <Divider>or</Divider>
      </div>

      <GoogleButton
        onClick={() =>
          setNotice('Google sign-in is not connected in this preview. Use your email and password.')
        }
      >
        Continue with Google
      </GoogleButton>
    </AuthLayout>
  )
}
