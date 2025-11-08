import React, { useState, useEffect } from 'react';
import { ArrowLeft, CalendarDays } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { getBadgeVariant } from '../config/theme';
import type { BadgeVariant } from '../config/theme';

interface ServiceRecord {
  service_id: string;
  vehicle_id: string;
  vehicle_name: string;
  service_type: string;
  service_date: string;
  mileage: number;
  cost: number;
  service_center: string;
  technician: string;
  notes: string;
  status: string;
}

const ServiceHistory: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [serviceRecords, setServiceRecords] = useState<ServiceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadServiceHistory();
  }, []);

  const loadServiceHistory = async () => {
    try {
      setLoading(true);
      // Simulated data - replace with actual API call when available
      const mockData: ServiceRecord[] = [
        {
          service_id: 'SRV-001',
          vehicle_id: 'VEH-2024-001',
          vehicle_name: '2024 Toyota Camry',
          service_type: 'Oil Change',
          service_date: '2025-10-15',
          mileage: 15000,
          cost: 49.99,
          service_center: 'AutoMind Service Center - Downtown',
          technician: 'John Smith',
          notes: 'Synthetic oil used. Next service due at 20,000 miles.',
          status: 'completed'
        },
        {
          service_id: 'SRV-002',
          vehicle_id: 'VEH-2024-001',
          vehicle_name: '2024 Toyota Camry',
          service_type: 'Tire Rotation',
          service_date: '2025-09-20',
          mileage: 12000,
          cost: 35.00,
          service_center: 'AutoMind Service Center - North',
          technician: 'Sarah Johnson',
          notes: 'All tires rotated. Tire pressure checked and adjusted.',
          status: 'completed'
        },
        {
          service_id: 'SRV-003',
          vehicle_id: 'VEH-2024-001',
          vehicle_name: '2024 Toyota Camry',
          service_type: 'Regular Maintenance',
          service_date: '2025-08-10',
          mileage: 10000,
          cost: 129.99,
          service_center: 'AutoMind Service Center - Downtown',
          technician: 'Mike Brown',
          notes: 'Comprehensive inspection. All systems operating normally.',
          status: 'completed'
        },
      ];
      setServiceRecords(mockData);
    } catch (error) {
      console.error('Failed to load service history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const filteredRecords = filter === 'all'
    ? serviceRecords
    : serviceRecords.filter(record => record.service_type.toLowerCase().includes(filter.toLowerCase()));

  const statusVariantMap: Record<string, BadgeVariant> = {
    completed: 'success',
    pending: 'warning',
    cancelled: 'danger'
  };

  const getStatusBadge = (status: string) => {
    const variant = statusVariantMap[status?.toLowerCase()] || 'neutral';
    return getBadgeVariant(variant);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-slate-100">
      {/* Top Navigation */}
      <nav className="glass-card shadow-md border border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/customer-dashboard')}
                className="btn-ghost flex items-center gap-2 text-sm text-slate-200"
              >
                <ArrowLeft className="w-4 h-4" />
                Back
              </button>
              <h1 className="text-2xl font-bold text-white">Service History</h1>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm font-semibold text-white">
                  {user?.first_name} {user?.last_name}
                </div>
                <div className="text-xs text-slate-400 capitalize">{user?.role?.replace('_', ' ')}</div>
              </div>
              <button
                onClick={handleLogout}
                className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-6">
        {/* Header Section */}
        <div className="relative overflow-hidden glass-card rounded-2xl border border-white/10 p-8 mb-6">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/40 via-cyan-500/30 to-emerald-400/30 opacity-60 blur-3xl" />
          <div className="relative">
            <div className="flex items-center gap-3 text-cyan-200 mb-3">
              <CalendarDays className="w-6 h-6" />
              <span className="text-sm uppercase tracking-widest">Maintenance timeline</span>
            </div>
            <h2 className="text-3xl font-bold text-white mb-2">Your Service History</h2>
            <p className="text-slate-200">
              Track every appointment, technician note, and cost detail in one cohesive timeline.
            </p>
          </div>
        </div>

        {/* Filter Section */}
        <div className="glass-card rounded-xl shadow-md p-4 mb-6">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-slate-200">Filter by:</span>
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${
                  filter === 'all'
                    ? 'border-cyan-400/60 bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-cyan-900/30'
                    : 'text-slate-200 border-white/10 hover:border-cyan-400/40 hover:bg-white/10'
                }`}
              >
                All Services
              </button>
              <button
                onClick={() => setFilter('oil')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${
                  filter === 'oil'
                    ? 'border-cyan-400/60 bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-cyan-900/30'
                    : 'text-slate-200 border-white/10 hover:border-cyan-400/40 hover:bg-white/10'
                }`}
              >
                Oil Changes
              </button>
              <button
                onClick={() => setFilter('tire')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${
                  filter === 'tire'
                    ? 'border-cyan-400/60 bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-cyan-900/30'
                    : 'text-slate-200 border-white/10 hover:border-cyan-400/40 hover:bg-white/10'
                }`}
              >
                Tire Services
              </button>
              <button
                onClick={() => setFilter('maintenance')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${
                  filter === 'maintenance'
                    ? 'border-cyan-400/60 bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-cyan-900/30'
                    : 'text-slate-200 border-white/10 hover:border-cyan-400/40 hover:bg-white/10'
                }`}
              >
                Maintenance
              </button>
            </div>
          </div>
        </div>

        {/* Service Records */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
            <p className="text-slate-300">Loading service history...</p>
          </div>
        ) : filteredRecords.length === 0 ? (
          <div className="glass-card rounded-xl shadow-md p-12 text-center">
            <div className="flex items-center justify-center mb-4">
              <CalendarDays className="w-12 h-12 text-cyan-300" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">No Service Records Found</h3>
            <p className="text-slate-300 mb-6">You don't have any service history yet.</p>
            <button
              onClick={() => navigate('/schedule-service')}
              className="btn-primary"
            >
              Schedule Your First Service
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredRecords.map((record) => (
              <div key={record.service_id} className="glass-card rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-white">{record.service_type}</h3>
                    <p className="text-sm text-slate-300">{record.vehicle_name}</p>
                  </div>
                  <span className={`status-indicator ${getStatusBadge(record.status)}`}>
                    {record.status.replace(/_/g, ' ').toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <div className="text-xs text-slate-400 mb-1">Service Date</div>
                    <div className="font-medium">{new Date(record.service_date).toLocaleDateString()}</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 mb-1">Mileage</div>
                    <div className="font-medium">{record.mileage.toLocaleString()} miles</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 mb-1">Cost</div>
                    <div className="font-medium text-emerald-300">${record.cost.toFixed(2)}</div>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-xs text-slate-400 mb-1">Service Center</div>
                      <div className="text-slate-200">{record.service_center}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-400 mb-1">Technician</div>
                      <div className="text-slate-200">{record.technician}</div>
                    </div>
                  </div>
                  {record.notes && (
                    <div className="mt-3">
                      <div className="text-xs text-slate-400 mb-1">Notes</div>
                      <div className="text-sm text-slate-200 bg-white/5 p-3 rounded-lg">{record.notes}</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Quick Action */}
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate('/schedule-service')}
            className="btn-primary"
          >
            Schedule New Service
          </button>
        </div>
      </div>
    </div>
  );
};

export default ServiceHistory;
