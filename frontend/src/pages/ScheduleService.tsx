import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

interface Vehicle {
  vehicle_id: string;
  make: string;
  model: string;
  year: number;
}

const ScheduleService: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    vehicle_id: '',
    service_type: 'regular_maintenance',
    scheduled_date: '',
    preferred_time: 'morning',
    notes: '',
  });

  useEffect(() => {
    loadVehicles();
  }, []);

  const loadVehicles = async () => {
    try {
      setLoading(true);
      const response = await apiService.getCustomerDashboard();
      setVehicles(response.dashboard?.vehicles || []);
    } catch (error) {
      console.error('Failed to load vehicles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Simulated API call - replace with actual API endpoint when available
      await new Promise(resolve => setTimeout(resolve, 1000));
      alert('Service appointment scheduled successfully!');
      navigate('/customer-dashboard');
    } catch (error) {
      console.error('Failed to schedule service:', error);
      alert('Failed to schedule service. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Top Navigation */}
      <nav className="glass-card border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/customer-dashboard')} className="text-cyan-300 hover:text-cyan-200 transition-colors">
                ← Back
              </button>
              <h1 className="text-2xl font-bold text-white">🔧 Schedule Service</h1>
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
                className="bg-gradient-to-r from-rose-500 to-red-500 text-white px-4 py-2 rounded-xl hover:from-rose-600 hover:to-red-600 transition-all duration-200 text-sm font-medium shadow-lg shadow-rose-500/30"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto p-6">
        <div className="glass-card border border-white/20 rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Book Your Service Appointment</h2>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mx-auto"></div>
              <p className="text-slate-300 mt-4">Loading...</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Select Vehicle */}
              <div>
                <label htmlFor="vehicle" className="block text-sm font-medium text-slate-200 mb-2">
                  Select Vehicle *
                </label>
                <select
                  id="vehicle"
                  required
                  value={formData.vehicle_id}
                  onChange={(e) => setFormData({ ...formData, vehicle_id: e.target.value })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                >
                  <option value="" className="bg-slate-800 text-white">Choose a vehicle...</option>
                  {vehicles.map((vehicle) => (
                    <option key={vehicle.vehicle_id} value={vehicle.vehicle_id} className="bg-slate-800 text-white">
                      {vehicle.year} {vehicle.make} {vehicle.model} - {vehicle.vehicle_id}
                    </option>
                  ))}
                </select>
              </div>

              {/* Service Type */}
              <div>
                <label htmlFor="service_type" className="block text-sm font-medium text-slate-200 mb-2">
                  Service Type *
                </label>
                <select
                  id="service_type"
                  required
                  value={formData.service_type}
                  onChange={(e) => setFormData({ ...formData, service_type: e.target.value })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                >
                  <option value="regular_maintenance" className="bg-slate-800 text-white">Regular Maintenance</option>
                  <option value="oil_change" className="bg-slate-800 text-white">Oil Change</option>
                  <option value="tire_rotation" className="bg-slate-800 text-white">Tire Rotation</option>
                  <option value="brake_service" className="bg-slate-800 text-white">Brake Service</option>
                  <option value="engine_diagnostic" className="bg-slate-800 text-white">Engine Diagnostic</option>
                  <option value="battery_check" className="bg-slate-800 text-white">Battery Check</option>
                  <option value="other" className="bg-slate-800 text-white">Other</option>
                </select>
              </div>

              {/* Date */}
              <div>
                <label htmlFor="scheduled_date" className="block text-sm font-medium text-slate-200 mb-2">
                  Preferred Date *
                </label>
                <input
                  type="date"
                  id="scheduled_date"
                  required
                  value={formData.scheduled_date}
                  onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                />
              </div>

              {/* Time */}
              <div>
                <label htmlFor="preferred_time" className="block text-sm font-medium text-slate-200 mb-2">
                  Preferred Time *
                </label>
                <select
                  id="preferred_time"
                  required
                  value={formData.preferred_time}
                  onChange={(e) => setFormData({ ...formData, preferred_time: e.target.value })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                >
                  <option value="morning" className="bg-slate-800 text-white">Morning (8:00 AM - 12:00 PM)</option>
                  <option value="afternoon" className="bg-slate-800 text-white">Afternoon (12:00 PM - 5:00 PM)</option>
                  <option value="evening" className="bg-slate-800 text-white">Evening (5:00 PM - 8:00 PM)</option>
                </select>
              </div>

              {/* Notes */}
              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-slate-200 mb-2">
                  Additional Notes
                </label>
                <textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={4}
                  placeholder="Any specific concerns or requests?"
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                />
              </div>

              {/* Submit Button */}
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => navigate('/customer-dashboard')}
                  className="flex-1 py-3 px-6 border border-white/20 rounded-xl font-medium text-slate-300 hover:bg-white/10 hover:border-white/30 transition-all duration-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-3 px-6 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-xl font-medium hover:from-cyan-600 hover:to-blue-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-cyan-500/30"
                >
                  {submitting ? 'Scheduling...' : 'Schedule Appointment'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScheduleService;
