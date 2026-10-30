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
import { signup } from '@/lib/mockAuth'
import AuthLayout from '@/components/AuthLayout'
import TextField from '@/components/TextField'
import Checkbox from '@/components/Checkbox'
import Choice from '@/components/Choice'
import SubmitButton from '@/components/SubmitButton'
import FormError from '@/components/FormError'
import PasswordChecklist from '@/components/PasswordChecklist'

const PERSONAS = [
  { value: 'Student', label: 'Student', hint: 'Coursework + exams' },
  { value: 'Creator', label: 'Creator', hint: 'Projects + clients' },
  { value: 'Professional', label: 'Professional', hint: 'Work + side gigs' },
]

const PEAK_TIMES = [
  { value: 'morning', label: 'Morning', hint: 'Before noon' },
  { value: 'afternoon', label: 'Afternoon', hint: '12–5pm' },
  { value: 'evening', label: 'Evening', hint: 'After 5pm' },
]

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
      persona: 'Student',
      peakTime: 'morning',
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

        <Choice
          legend="What are you planning for?"
          name="persona"
          options={PERSONAS}
          register={register}
        />

        <Choice
          legend="When do you focus best?"
          name="peakTime"
          options={PEAK_TIMES}
          register={register}
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
