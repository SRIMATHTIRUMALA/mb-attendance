import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AppLayout from './components/layout/AppLayout';
import Login from './pages/Login';
import EmployeeDashboard from './pages/EmployeeDashboard';
import DailyWork from './pages/DailyWork';
import AttendanceHistory from './pages/AttendanceHistory';
import WeeklySchedule from './pages/WeeklySchedule';
import Requests from './pages/Requests';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import Employees from './pages/admin/Employees';
import EmployeeDetails from './pages/admin/EmployeeDetails';
import AttendanceReview from './pages/admin/AttendanceReview';
import WorkReports from './pages/admin/WorkReports';
import Settings from './pages/admin/Settings';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-slate-500">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          {/* Protected Routes inside AppLayout */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            {/* Employee Views */}
            <Route index element={<EmployeeDashboard />} />
            <Route path="work" element={<DailyWork />} />
            <Route path="attendance-history" element={<AttendanceHistory />} />
            <Route path="schedule" element={<WeeklySchedule />} />
            <Route path="requests" element={<Requests />} />

            {/* Admin Views */}
            <Route
              path="admin"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="admin/employees"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <Employees />
                </ProtectedRoute>
              }
            />
            <Route
              path="admin/employees/:id"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <EmployeeDetails />
                </ProtectedRoute>
              }
            />
            <Route
              path="admin/attendance"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <AttendanceReview />
                </ProtectedRoute>
              }
            />
            <Route
              path="admin/reports"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <WorkReports />
                </ProtectedRoute>
              }
            />
            <Route
              path="admin/settings"
              element={
                <ProtectedRoute requireAdmin={true}>
                  <Settings />
                </ProtectedRoute>
              }
            />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
