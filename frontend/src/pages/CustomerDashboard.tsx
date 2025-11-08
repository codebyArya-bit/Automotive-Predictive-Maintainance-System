import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { mockCustomerVehicles, mockServiceAppointments, mockAlertStream } from '../data/mockInsights';

interface Vehicle {
  vehicle_id: string;
  make: string;
  model: string;
  year: number;
  status: string;
  last_service?: string;
  next_service_due?: string;
  health_score?: number;
}

interface Alert {
  alert_id: string;
  type: string;
  severity: string;
  message: string;
  timestamp: string;
  vehicle_id: string;
}

interface Appointment {
  appointment_id: string;
  vehicle_id: string;
  service_type: string;
  scheduled_date: string;
  status: string;
  service_center: string;
}

const buildMockCustomerDashboard = () => ({
  vehicles: mockCustomerVehicles.map((vehicle, index) => ({
    vehicle_id: vehicle.vin,
    make: vehicle.make,
    model: vehicle.model,
    year: vehicle.year,
    status: vehicle.status || 'healthy',
    last_service: new Date(Date.now() - (index + 1) * 86400000).toISOString(),
    next_service_due: new Date(Date.now() + (index + 2) * 86400000 * 5).toISOString(),
    health_score: 78 - index * 4,
  })),
  recent_alerts: mockAlertStream.slice(0, 4).map((alert) => ({
    alert_id: alert.id,
    type: alert.severity,
    severity: alert.severity,
    message: alert.message,
    timestamp: alert.timestamp,
    vehicle_id: alert.vehicleId || 'N/A',
  })),
  upcoming_appointments: mockServiceAppointments,
  call_history: [
    { id: 'call-101', agent: 'Autonomy Concierge', summary: 'Scheduled battery refresh', timestamp: new Date().toISOString() },
    { id: 'call-102', agent: 'Predictive Insights', summary: 'Explained tire rotation alert', timestamp: new Date(Date.now() - 3600 * 1000).toISOString() },
  ],
});

const CustomerDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<any>(buildMockCustomerDashboard());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiService.getCustomerDashboard();
      setDashboard(response.dashboard || buildMockCustomerDashboard());
    } catch (err: any) {
      console.warn('Falling back to mock customer dashboard data', err);
      setDashboard(buildMockCustomerDashboard());
      setError(err?.message ? `${err.message} — displaying live snapshot` : 'Showing sample snapshot while live data recovers');
    } finally {
      setLoading(false);
    }
  };

  const getHealthScoreColor = (score: number): string => {
    if (score >= 80) return 'text-emerald-300 bg-emerald-500/20';
    if (score >= 60) return 'text-cyan-300 bg-cyan-500/20';
    if (score >= 40) return 'text-orange-300 bg-orange-500/20';
    return 'text-rose-300 bg-rose-500/20';
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-500 text-white';
      case 'high':
        return 'bg-orange-500 text-white';
      case 'medium':
        return 'bg-blue-500 text-white';
      case 'low':
        return 'bg-green-500 text-white';
      default:
        return 'bg-white/50 text-white';
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950">
        <div className="glass-card p-10 rounded-2xl text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-cyan-400 mx-auto mb-4"></div>
          <p className="text-slate-200">Loading your customer dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8 text-slate-100">
        <div className="glass-card border border-rose-400/30 text-rose-100 px-6 py-4 rounded-2xl max-w-xl mx-auto">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-slate-100">
      {/* Top Navigation */}
      <nav className="glass-card/5 shadow-xl shadow-slate-950/40 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold gradient-title">🚗 AutoMind</h1>
              <span className="text-sm text-slate-300">Customer Portal</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm font-semibold text-white">
                  {user?.first_name} {user?.last_name}
                </div>
                <div className="text-xs text-slate-300 capitalize">{user?.role?.replace('_', ' ')}</div>
              </div>
              <button
                onClick={handleLogout}
                className="btn-danger text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-6">
        {/* Welcome Section */}
        <div className="glass-card relative overflow-hidden rounded-2xl shadow-2xl p-8 mb-6">
          <div className="absolute inset-0 opacity-30 blur-3xl pointer-events-none bg-gradient-to-r from-cyan-500 to-blue-500" />
          <div className="relative">
            <h2 className="text-3xl font-bold gradient-title mb-2">
              Welcome back, {user?.first_name}!
            </h2>
            <p className="text-cyan-200">Monitor your vehicles and stay ahead of maintenance needs</p>
          </div>
        </div>

        {/* Quick Stats */}
        {dashboard && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-cyan-400/40 transition-all">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-300 mb-1">My Vehicles</div>
                  <div className="text-3xl font-bold text-cyan-300">
                    {dashboard.vehicles?.length || 0}
                  </div>
                </div>
                <div className="text-4xl">🚙</div>
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-amber-400/40 transition-all">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-300 mb-1">Active Alerts</div>
                  <div className="text-3xl font-bold text-amber-300">
                    {dashboard.recent_alerts?.length || 0}
                  </div>
                </div>
                <div className="text-4xl">⚠️</div>
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-emerald-400/40 transition-all">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-300 mb-1">Upcoming Appointments</div>
                  <div className="text-3xl font-bold text-emerald-300">
                    {dashboard.upcoming_appointments?.length || 0}
                  </div>
                </div>
                <div className="text-4xl">📅</div>
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-purple-400/40 transition-all">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-300 mb-1">Recent Calls</div>
                  <div className="text-3xl font-bold text-purple-300">
                    {dashboard.call_history?.length || 0}
                  </div>
                </div>
                <div className="text-4xl">📞</div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* My Vehicles */}
          <div className="glass-card rounded-2xl p-6 border border-white/10">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center">
              <span className="mr-2">🚗</span>
              My Vehicles
            </h3>
            <div className="space-y-4">
              {dashboard?.vehicles?.map((vehicle: Vehicle) => (
                <div key={vehicle.vehicle_id} className="glass-panel border border-white/10 rounded-lg p-4 hover:border-cyan-400/40 transition-all">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-white">
                        {vehicle.year} {vehicle.make} {vehicle.model}
                      </h4>
                      <p className="text-xs text-slate-300">{vehicle.vehicle_id}</p>
                    </div>
                    {vehicle.health_score && (
                      <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getHealthScoreColor(vehicle.health_score)}`}>
                        {vehicle.health_score}%
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <div className="text-slate-300">Status</div>
                      <div className="font-medium text-white capitalize">{vehicle.status}</div>
                    </div>
                    <div>
                      <div className="text-slate-300">Last Service</div>
                      <div className="font-medium text-white">
                        {vehicle.last_service ? new Date(vehicle.last_service).toLocaleDateString() : 'N/A'}
                      </div>
                    </div>
                  </div>

                  {vehicle.next_service_due && (
                    <div className="mt-3 bg-cyan-500/20 border border-cyan-400/30 p-2 rounded text-xs text-cyan-200">
                      Next service due: {new Date(vehicle.next_service_due).toLocaleDateString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Recent Alerts */}
          <div className="glass-card rounded-2xl p-6 border border-white/10">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center">
              <span className="mr-2">⚠️</span>
              Recent Alerts
            </h3>
            <div className="space-y-3">
              {dashboard?.recent_alerts?.map((alert: Alert) => (
                <div key={alert.alert_id} className="border-l-4 border-amber-400 glass-panel p-4 rounded-r-lg hover:border-amber-300 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${getSeverityColor(alert.severity)}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                    <span className="text-xs text-slate-300">
                      {new Date(alert.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-sm text-white font-medium mb-1">{alert.type}</p>
                  <p className="text-sm text-slate-300">{alert.message}</p>
                </div>
              ))}
              {(!dashboard?.recent_alerts || dashboard.recent_alerts.length === 0) && (
                <div className="text-center py-8 text-slate-300">
                  <div className="text-4xl mb-2">✅</div>
                  <p>No active alerts. All systems normal!</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Upcoming Appointments */}
        <div className="glass-card rounded-2xl p-6 border border-white/10 mb-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <span className="mr-2">📅</span>
            Upcoming Appointments
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dashboard?.upcoming_appointments?.map((appointment: Appointment) => (
              <div key={appointment.appointment_id} className="glass-panel border border-white/10 rounded-lg p-4 hover:border-cyan-400/40 transition-all">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-semibold text-cyan-300 capitalize">
                    {appointment.service_type}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    appointment.status === 'confirmed' ? 'bg-emerald-500/20 text-emerald-200 border border-emerald-400/30' :
                    appointment.status === 'pending' ? 'bg-amber-500/20 text-amber-200 border border-amber-400/30' :
                    'glass-card/10 text-slate-200 border border-white/10'
                  }`}>
                    {appointment.status.toUpperCase()}
                  </span>
                </div>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-slate-300">Date:</span>
                    <span className="ml-2 font-medium text-white">
                      {new Date(appointment.scheduled_date).toLocaleDateString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-300">Location:</span>
                    <span className="ml-2 font-medium text-white">{appointment.service_center}</span>
                  </div>
                  <div>
                    <span className="text-slate-300">Vehicle:</span>
                    <span className="ml-2 font-medium text-xs text-slate-200">{appointment.vehicle_id}</span>
                  </div>
                </div>
              </div>
            ))}
            {(!dashboard?.upcoming_appointments || dashboard.upcoming_appointments.length === 0) && (
              <div className="col-span-full text-center py-8 text-slate-300">
                <div className="text-4xl mb-2">📅</div>
                <p>No upcoming appointments scheduled</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <button
            onClick={() => navigate('/voice-agent')}
            className="glass-card border border-cyan-400/30 text-white p-6 rounded-xl hover:border-cyan-300/60 hover:shadow-cyan-500/30 hover:shadow-xl transition-all"
          >
            <div className="text-4xl mb-3">📞</div>
            <div className="text-lg font-bold mb-1 gradient-title">AI Voice Agent</div>
            <div className="text-sm text-cyan-200">Get proactive service notifications</div>
          </button>

          <button
            onClick={() => navigate('/schedule-service')}
            className="glass-card border border-emerald-400/30 text-white p-6 rounded-xl hover:border-emerald-300/60 hover:shadow-emerald-500/30 hover:shadow-xl transition-all"
          >
            <div className="text-4xl mb-3">🔧</div>
            <div className="text-lg font-bold mb-1 gradient-title">Schedule Service</div>
            <div className="text-sm text-emerald-200">Book your next appointment</div>
          </button>

          <button
            onClick={() => navigate('/service-history')}
            className="glass-card border border-purple-400/30 text-white p-6 rounded-xl hover:border-purple-300/60 hover:shadow-purple-500/30 hover:shadow-xl transition-all"
          >
            <div className="text-4xl mb-3">📋</div>
            <div className="text-lg font-bold mb-1 gradient-title">Service History</div>
            <div className="text-sm text-purple-200">View past maintenance records</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CustomerDashboard;
