import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import ScrollToTop from './components/ScrollToTop.jsx'
import PageLoader from './components/PageLoader.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import GuestRoute from './components/GuestRoute.jsx'

const Landing = lazy(() => import('./pages/Landing/Landing.jsx'))
const Register = lazy(() => import('./pages/Auth/Register.jsx'))
const Login = lazy(() => import('./pages/Auth/Login.jsx'))
const VerifyOtp = lazy(() => import('./pages/Auth/VerifyOtp.jsx'))
const ForgotPassword = lazy(() => import('./pages/Auth/ForgotPassword.jsx'))
const ResetPassword = lazy(() => import('./pages/Auth/ResetPassword.jsx'))
const Dashboard = lazy(() => import('./pages/Dashboard/Dashboard.jsx'))
const AiPlanner = lazy(() => import('./pages/Dashboard/AiPlanner.jsx'))
const NotFound = lazy(() => import('./pages/NotFound.jsx'))

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<Landing />} />

        <Route
          path="/signup"
          element={
            <GuestRoute>
              <Register />
            </GuestRoute>
          }
        />
        <Route
          path="/login"
          element={
            <GuestRoute>
              <Login />
            </GuestRoute>
          }
        />
        <Route
          path="/verify-otp"
          element={
            <GuestRoute>
              <VerifyOtp />
            </GuestRoute>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <GuestRoute>
              <ForgotPassword />
            </GuestRoute>
          }
        />
        <Route
          path="/reset-password"
          element={
            <GuestRoute>
              <ResetPassword />
            </GuestRoute>
          }
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-planner"
          element={
            <ProtectedRoute>
              <AiPlanner />
            </ProtectedRoute>
          }
        />
        <Route
          path="/planner"
          element={
            <ProtectedRoute>
              <AiPlanner />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  )
}
