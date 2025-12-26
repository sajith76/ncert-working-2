import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import useUserStore from "./stores/userStore";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import TeacherPlaceholder from "./pages/TeacherPlaceholder";
import OnboardingLayout from "./pages/onboarding/OnboardingLayout";
import Dashboard from "./pages/Dashboard";
import BookToBot from "./pages/BookToBot";
import Settings from "./pages/Settings";
import "./App.css";

/**
 * Main App Component - Entry Point with Routing
 *
 * Routes:
 * - / → Login (with role selection)
 * - /signup → Student signup
 * - /teacher → Teacher placeholder
 * - /onboarding → Student onboarding flow
 * - /dashboard → Main dashboard hub
 * - /book-to-bot → PDF viewer interface
 * - /test → Test page (placeholder)
 * - /report-card → Report card (placeholder)
 * - /about-you → Customize onboarding
 *
 * TODO: Backend Integration
 * - Add token refresh on app mount
 * - Verify auth state with backend
 * - Add global error boundary
 */

// Protected Route wrapper
function ProtectedRoute({ children }) {
  const { isAuthenticated, user } = useUserStore();

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  if (!user.isOnboarded) {
    return <Navigate to="/onboarding" replace />;
  }

  return children;
}

// Onboarding Route wrapper
function OnboardingRoute({ children }) {
  const { isAuthenticated, user } = useUserStore();

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  if (user.isOnboarded) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

// Public Route wrapper
function PublicRoute({ children }) {
  const { isAuthenticated, user } = useUserStore();

  if (isAuthenticated) {
    if (user.isOnboarded) {
      return <Navigate to="/dashboard" replace />;
    } else {
      return <Navigate to="/onboarding" replace />;
    }
  }

  return children;
}

// Placeholder components for new routes
function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Test Center</h1>
        <p className="text-gray-500">Coming soon! Take tests to track your progress.</p>
        {/* TODO: Backend Integration - Fetch available tests */}
      </div>
    </div>
  );
}

function ReportCardPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Report Card</h1>
        <p className="text-gray-500">Coming soon! View your detailed performance reports.</p>
        {/* TODO: Backend Integration - Fetch user's test results and analytics */}
      </div>
    </div>
  );
}

// Settings page is now imported from ./pages/Settings

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/signup"
          element={
            <PublicRoute>
              <Signup />
            </PublicRoute>
          }
        />
        <Route path="/teacher" element={<TeacherPlaceholder />} />

        {/* Onboarding Route */}
        <Route
          path="/onboarding"
          element={
            <OnboardingRoute>
              <OnboardingLayout />
            </OnboardingRoute>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/book-to-bot"
          element={
            <ProtectedRoute>
              <BookToBot />
            </ProtectedRoute>
          }
        />
        <Route
          path="/test"
          element={
            <ProtectedRoute>
              <TestPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/report-card"
          element={
            <ProtectedRoute>
              <ReportCardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/about-you"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
