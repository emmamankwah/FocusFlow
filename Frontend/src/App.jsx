import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import ScrollToTop from './components/ScrollToTop.jsx'

const Landing = lazy(() => import('./pages/Landing/Landing.jsx'))
const Register = lazy(() => import('./pages/Auth/Register.jsx'))
const Login = lazy(() => import('./pages/Auth/Login.jsx'))
const VerifyOtp = lazy(() => import('./pages/Auth/VerifyOtp.jsx'))
const ForgotPassword = lazy(() => import('./pages/Auth/ForgotPassword.jsx'))
const ResetPassword = lazy(() => import('./pages/Auth/ResetPassword.jsx'))
const Dashboard = lazy(() => import('./pages/Dashboard/Dashboard.jsx'))
const NotFound = lazy(() => import('./pages/NotFound.jsx'))

function PageLoader() {
  return (
    <div className="grid min-h-screen place-items-center bg-canvas">
      <span className="h-9 w-9 animate-spin rounded-full border-2 border-line border-t-amber" />
    </div>
  )
}

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/signup" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/verify-otp" element={<VerifyOtp />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  )
}
