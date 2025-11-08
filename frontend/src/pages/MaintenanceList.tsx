import React, { useState, useEffect } from 'react';
import { 
  Wrench, 
  Calendar, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  Search,
  Plus,
  Settings
} from 'lucide-react';
import { apiService } from '../services/api';
import { MaintenanceRecord, PaginatedResponse } from '../types';
import MaintenanceForm from '../components/MaintenanceForm';
import { getBadgeVariant, hoverCardGlow, hoverCardSurface } from '../config/theme';
import type { BadgeVariant } from '../config/theme';

const MaintenanceList: React.FC = () => {
  const [maintenance, setMaintenance] = useState<MaintenanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [showMaintenanceForm, setShowMaintenanceForm] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0
  });

  // Handler for adding new maintenance record
  const handleAddMaintenance = async (maintenanceData: any) => {
    try {
      await apiService.createMaintenanceRecord(maintenanceData);
      setShowMaintenanceForm(false);
      // Refresh the maintenance list
      fetchMaintenance();
    } catch (error) {
      console.error('Failed to add maintenance record:', error);
    }
  };

  const handlePageChange = (newPage: number) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  useEffect(() => {
    fetchMaintenance();
  }, [pagination.page, statusFilter, typeFilter, searchTerm]);

  const fetchMaintenance = async () => {
    try {
      setLoading(true);
      const params: any = {
        page: pagination.page,
        limit: pagination.limit
      };

      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }

      if (typeFilter !== 'all') {
        params.type = typeFilter;
      }

      if (searchTerm) {
        params.search = searchTerm;
      }

      const response: PaginatedResponse<MaintenanceRecord> = await apiService.getMaintenanceRecords(params);
      setMaintenance(response.items || response.data || []);
      setPagination(prev => ({
        ...prev,
        total: response.total || response.pagination?.total || 0,
        totalPages: response.totalPages || response.pagination?.pages || 0
      }));
    } catch (error) {
      console.error('Failed to fetch maintenance records:', error);
    } finally {
      setLoading(false);
    }
  };

  const statusVariantMap: Record<string, BadgeVariant> = {
    completed: 'success',
    in_progress: 'info',
    scheduled: 'warning',
    cancelled: 'danger'
  };

  const statusIconMap: Record<
    string,
    { Icon: React.ElementType; className: string }
  > = {
    completed: { Icon: CheckCircle, className: 'text-emerald-300' },
    in_progress: { Icon: Clock, className: 'text-cyan-300' },
    scheduled: { Icon: Calendar, className: 'text-amber-300' },
    cancelled: { Icon: AlertTriangle, className: 'text-rose-300' },
    default: { Icon: Wrench, className: 'text-slate-300' }
  };

  const getStatusBadge = (status: string) => {
    const key = status?.toLowerCase();
    const variant = statusVariantMap[key] || 'neutral';
    return getBadgeVariant(variant);
  };

  const getStatusIcon = (status: string) => {
    const key = status?.toLowerCase();
    const { Icon, className } = statusIconMap[key] || statusIconMap.default;
    return <Icon className={`w-4 h-4 ${className}`} />;
  };

  const formatStatusLabel = (status?: string) =>
    status ? status.replace(/_/g, ' ') : 'unknown';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Maintenance Records</h1>
        <button
          onClick={() => setShowMaintenanceForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Maintenance
        </button>
      </div>

      {/* Search and Filters */}
      <div className="glass-card p-4 rounded-lg shadow-sm border border-white/10">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search maintenance records..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-10"
              />
            </div>
          </div>
          
          <div className="flex gap-2">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field min-w-[150px]"
            >
              <option value="all">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="input-field min-w-[150px]"
            >
              <option value="all">All Types</option>
              <option value="routine">Routine</option>
              <option value="repair">Repair</option>
              <option value="inspection">Inspection</option>
              <option value="emergency">Emergency</option>
            </select>
          </div>
        </div>
      </div>

      {/* Maintenance Records Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          // Loading skeleton
          Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="glass-card rounded-lg shadow-sm border border-white/10 p-6 animate-pulse">
              <div className="h-4 glass-card/15 rounded w-3/4 mb-4"></div>
              <div className="space-y-2">
                <div className="h-3 glass-card/15 rounded w-1/2"></div>
                <div className="h-3 glass-card/15 rounded w-2/3"></div>
                <div className="h-3 glass-card/15 rounded w-1/3"></div>
              </div>
            </div>
          ))
        ) : maintenance.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <Settings className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No maintenance records found</h3>
            <p className="text-slate-400 mb-4">Get started by adding your first maintenance record.</p>
            <button
              onClick={() => setShowMaintenanceForm(true)}
              className="btn-secondary px-6"
            >
              Add Maintenance Record
            </button>
          </div>
        ) : (
          maintenance.map((record) => (
            <div
              key={record.id || record.vehicle_id}
              className={`${hoverCardSurface} p-6`}
            >
              <div className={hoverCardGlow} />
              <div className="relative space-y-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500/20 via-cyan-500/10 to-transparent border border-white/10 text-cyan-200 shadow-inner shadow-blue-900/30">
                      <Settings className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-widest text-slate-400">
                        Vehicle {record.vehicle_id}
                      </p>
                      <h3 className="text-lg font-semibold text-white">
                        {record.type || record.service_type}
                      </h3>
                    </div>
                  </div>
                  <span className={`status-indicator ${getStatusBadge(record.status)}`}>
                    {formatStatusLabel(record.status)}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm text-slate-300">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center justify-center rounded-xl bg-white/5 border border-white/10 p-2">
                      {getStatusIcon(record.status)}
                    </span>
                    <span className="uppercase tracking-widest text-xs text-slate-400">
                      Status pulse
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">
                    ID #{record.id || record.vehicle_id}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="space-y-1">
                    <p className="text-xs text-slate-400">Scheduled Date</p>
                    <p className="font-medium text-white">
                      {(record.scheduled_date || record.scheduledDate)
                        ? new Date(record.scheduled_date || record.scheduledDate!).toLocaleDateString()
                        : 'N/A'}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-slate-400">Completed Date</p>
                    <p className="font-medium text-white">
                      {record.completed_date
                        ? new Date(record.completed_date).toLocaleDateString()
                        : 'Pending'}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-slate-400">Cost</p>
                    <p className="font-semibold text-emerald-300">
                      ${record.cost ? record.cost.toFixed(2) : '0.00'}
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-slate-400">Status</p>
                    <p className="font-semibold text-white capitalize">
                      {formatStatusLabel(record.status)}
                    </p>
                  </div>
                </div>

                {record.description && (
                  <div className="pt-3 border-t border-white/5">
                    <p className="text-sm text-slate-300">{record.description}</p>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {!loading && maintenance.length > 0 && pagination.totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-slate-200">
            Showing {((pagination.page - 1) * pagination.limit) + 1} to {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total} results
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handlePageChange(pagination.page - 1)}
              disabled={pagination.page === 1}
              className="px-3 py-2 text-sm font-medium text-slate-400 glass-card border border-white/20 rounded-md hover:glass-card/5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(5, pagination.totalPages) }, (_, i) => {
                const pageNum = i + 1;
                return (
                  <button
                    key={pageNum}
                    onClick={() => handlePageChange(pageNum)}
                    className={`px-3 py-2 text-sm font-medium rounded-md ${
                      pagination.page === pageNum
                        ? 'bg-primary-600 text-white'
                        : 'text-slate-400 glass-card border border-white/20 hover:bg-white/5'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
            </div>
            
            <button
              onClick={() => handlePageChange(pagination.page + 1)}
              disabled={pagination.page === pagination.totalPages}
              className="px-3 py-2 text-sm font-medium text-slate-400 glass-card border border-white/20 rounded-md hover:glass-card/5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Maintenance Form Modal */}
      {showMaintenanceForm && (
        <MaintenanceForm
          onSubmit={handleAddMaintenance}
          onCancel={() => setShowMaintenanceForm(false)}
        />
      )}
    </div>
  );
};

export default MaintenanceList;
