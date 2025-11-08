import { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, ProtectedRoute } from './contexts/AuthContext';
import Layout from './components/Layout';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorBoundary from './components/ErrorBoundary';
import Dashboard from './pages/Dashboard';
import { agentMonitorPalette } from './config/theme';

// Authentication
import Login from './pages/Login';

// New feature pages
import CustomerDashboard from './pages/CustomerDashboard';
import ManufacturingDashboard from './pages/ManufacturingDashboard';
import ScheduleService from './pages/ScheduleService';
import ServiceHistory from './pages/ServiceHistory';
import RecurringDefects from './pages/RecurringDefects';
import QualityMetrics from './pages/QualityMetrics';
import EdgeCaseDemo from './pages/EdgeCaseDemo';
import VoiceAgentSimulator from './components/VoiceAgentSimulator';
import DemandForecastDashboard from './components/DemandForecastDashboard';
import RCACAPAReport from './components/RCACAPAReport';

// Lazy load existing components for better performance
const VehicleList = lazy(() => import('./pages/VehicleList'));
const VehicleDetail = lazy(() => import('./pages/VehicleDetail'));
const AgentMonitor = lazy(() => import('./pages/AgentMonitor'));
const MaintenanceList = lazy(() => import('./pages/MaintenanceList'));
const AlertsList = lazy(() => import('./pages/AlertsList'));
const DemoInterface = lazy(() => import('./pages/DemoInterface'));
const Analytics = lazy(() => import('./pages/Analytics'));
const DemoAnalytics = lazy(() => import('./pages/DemoAnalytics'));
const LogMonitor = lazy(() => import('./pages/LogMonitor'));

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <AuthProvider>
          <div className={`min-h-screen ${agentMonitorPalette.page}`}>
            <Suspense fallback={<LoadingSpinner />}>
              <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Navigate to="/login" replace />} />

                {/* Role-Based Dashboard Routes */}
                <Route
                  path="/customer-dashboard"
                  element={
                    <ProtectedRoute allowedRoles={['customer']}>
                      <CustomerDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/manufacturing-dashboard"
                  element={
                    <ProtectedRoute allowedRoles={['manufacturing_engineer', 'system_admin']}>
                      <ManufacturingDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Customer Feature Routes */}
                <Route
                  path="/schedule-service"
                  element={
                    <ProtectedRoute allowedRoles={['customer']}>
                      <ScheduleService />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/service-history"
                  element={
                    <ProtectedRoute allowedRoles={['customer']}>
                      <ServiceHistory />
                    </ProtectedRoute>
                  }
                />

                {/* Manufacturing Feature Routes */}
                <Route
                  path="/recurring-defects"
                  element={
                    <ProtectedRoute allowedRoles={['manufacturing_engineer', 'system_admin']}>
                      <RecurringDefects />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/quality-metrics"
                  element={
                    <ProtectedRoute allowedRoles={['manufacturing_engineer', 'system_admin']}>
                      <QualityMetrics />
                    </ProtectedRoute>
                  }
                />

                {/* Feature Routes - Available to authenticated users */}
                <Route
                  path="/voice-agent"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <VoiceAgentSimulator />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/demand-forecast"
                  element={
                    <ProtectedRoute allowedRoles={['service_staff', 'system_admin', 'fleet_manager']}>
                      <Layout>
                        <DemandForecastDashboard />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/rca-reports"
                  element={
                    <ProtectedRoute allowedRoles={['manufacturing_engineer', 'system_admin']}>
                      <Layout>
                        <RCACAPAReport />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/edge-cases"
                  element={
                    <ProtectedRoute>
                      <EdgeCaseDemo />
                    </ProtectedRoute>
                  }
                />

                {/* Existing Dashboard Routes - Protected */}
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <Dashboard />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/vehicles"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <VehicleList />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/vehicles/:id"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <VehicleDetail />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/agents"
                  element={
                    <ProtectedRoute allowedRoles={['system_admin']}>
                      <Layout>
                        <AgentMonitor />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/logs"
                  element={
                    <ProtectedRoute allowedRoles={['system_admin', 'manufacturing_engineer']}>
                      <Layout>
                        <LogMonitor />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/maintenance"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <MaintenanceList />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/alerts"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <AlertsList />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/demo"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <DemoInterface />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/demo-analytics"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <DemoAnalytics />
                      </Layout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/analytics"
                  element={
                    <ProtectedRoute allowedRoles={['system_admin', 'fleet_manager']}>
                      <Layout>
                        <Analytics />
                      </Layout>
                    </ProtectedRoute>
                  }
                />

                {/* Catch-all - redirect to login */}
                <Route path="*" element={<Navigate to="/login" replace />} />
              </Routes>
            </Suspense>

            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#10b981',
                    secondary: '#fff',
                  },
                },
                error: {
                  duration: 5000,
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </div>
        </AuthProvider>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
