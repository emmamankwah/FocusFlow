import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import {
  emailRules,
  passwordRules,
  confirmPasswordRules,
  usernameRules,
} from '@/lib/validation'
import usePageTitle from '@/lib/usePageTitle'
import { signup } from '@/lib/authApi'
import AuthLayout from '@/components/AuthLayout'
import TextField from '@/components/TextField'
import Checkbox from '@/components/Checkbox'
import SubmitButton from '@/components/SubmitButton'
import FormError from '@/components/FormError'
import PasswordChecklist from '@/components/PasswordChecklist'

export default function Register() {
  usePageTitle('Create account — FocusFlow')
  const [apiError, setApiError] = useState(null)
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      firstName: '',
      lastName: '',
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      user_type: '',
      terms: false,
    },
  })

  const password = watch('password')

  const onSubmit = async (data) => {
    setApiError(null)
    try {
      await signup(data)
      navigate('/verify-email')
    } catch (err) {
      setApiError(err.message || 'Could not create your account.')
    }
  }

  return (
    <AuthLayout
      eyebrow="Create account"
      title="Create your account"
      subtitle="It takes a minute. Your first plan is built from your first deadline."
      brandTitle="Start with one deadline"
      brandLead="Tell FocusFlow what you are working on and it builds the week around it."
      footer={
        <>
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-cobalt underline underline-offset-4 hover:text-cobalt/80">
            Log in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <TextField
            id="firstName"
            label="First name"
            placeholder="Ama"
            autoComplete="given-name"
            error={errors.firstName}
            registration={register('firstName', { required: 'Enter your first name.' })}
          />
          <TextField
            id="lastName"
            label="Last name"
            placeholder="Boateng"
            autoComplete="family-name"
            error={errors.lastName}
            registration={register('lastName', { required: 'Enter your last name.' })}
          />
        </div>

        <TextField
          id="username"
          label="Username"
          placeholder="ama_b"
          autoComplete="username"
          error={errors.username}
          registration={register('username', usernameRules)}
        />

        <TextField
          id="email"
          label="Email"
          type="email"
          placeholder="you@school.edu"
          autoComplete="email"
          error={errors.email}
          registration={register('email', emailRules)}
        />

        <fieldset className="space-y-2" aria-describedby={errors.user_type ? 'user-type-error' : undefined}>
          <legend className="text-[0.82rem] font-medium text-inkwell">What best describes you?</legend>
          <div className="grid gap-2 sm:grid-cols-2">
            {[
              ['student', 'Student'],
              ['working_professional', 'Working professional'],
              ['both', 'Both'],
              ['other', 'Other'],
            ].map(([value, label]) => (
              <label
                key={value}
                className="group flex cursor-pointer items-center gap-2.5 rounded-xl border border-inkwell/15 bg-white/60 px-3 py-2.5 transition hover:border-cobalt/50 has-[:checked]:border-cobalt has-[:checked]:bg-cobalt/5"
              >
                <input
                  type="radio"
                  value={value}
                  className="h-4 w-4 accent-cobalt focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cobalt"
                  {...register('user_type', { required: 'Choose the option that best describes you.' })}
                />
                <span className="text-[0.82rem] text-inkwell/80">{label}</span>
              </label>
            ))}
          </div>
          {errors.user_type && (
            <p id="user-type-error" role="alert" className="text-[0.76rem] font-medium text-[#b42318]">
              {errors.user_type.message}
            </p>
          )}
        </fieldset>

        <div>
          <TextField
            id="password"
            label="Password"
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
          label="Confirm password"
          type="password"
          placeholder="Repeat your password"
          autoComplete="new-password"
          error={errors.confirmPassword}
          registration={register('confirmPassword', confirmPasswordRules)}
        />

        <div>
          <Checkbox
            id="terms"
            label="I agree to the Terms and Privacy Policy."
            registration={register('terms', {
              required: 'Agree to the terms to continue.',
            })}
          />
          {errors.terms && (
            <p role="alert" className="mt-1.5 text-[0.76rem] font-medium text-[#b42318]">
              {errors.terms.message}
            </p>
          )}
        </div>

        <FormError message={apiError} />

        <SubmitButton loading={isSubmitting} loadingText="Creating account...">
          Create account
        </SubmitButton>
      </form>
    </AuthLayout>
  )
}
