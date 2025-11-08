import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  Search,
  Filter,
  Clock,
  Shield,
  Settings,
  RefreshCw,
  AlertCircle,
  Bell,
  Eye
} from 'lucide-react';
import { apiService } from '../services/api';
import { Alert, PaginatedResponse } from '../types';

const AlertsList: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  });

  useEffect(() => {
    fetchAlerts();
  }, [pagination.page, severityFilter, statusFilter, searchTerm]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const params: any = {
        page: pagination.page,
        limit: pagination.limit
      };

      if (severityFilter !== 'all') {
        params.severity = severityFilter;
      }

      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }

      if (searchTerm) {
        params.search = searchTerm;
      }

      const response: PaginatedResponse<Alert> = await apiService.getAlerts(params);
      setAlerts(response.items || response.data || []);
      setPagination(prev => ({
        ...prev,
        total: response.total || response.pagination?.total || 0,
        totalPages: response.totalPages || response.pagination?.pages || 0
      }));
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
      case 'critical':
        return 'text-danger-600 bg-danger-50 border-danger-200';
      case 'medium':
      case 'warning':
        return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'low':
      case 'info':
        return 'text-primary-600 bg-primary-50 border-primary-200';
      default:
        return 'text-slate-300 bg-white/5 border-white/10';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
      case 'critical':
        return <AlertCircle className="w-5 h-5 text-danger-500" />;
      case 'medium':
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-warning-500" />;
      case 'low':
      case 'info':
        return <Info className="w-5 h-5 text-primary-500" />;
      default:
        return <Bell className="w-5 h-5 text-slate-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'resolved':
        return 'text-success-600 bg-success-50';
      case 'acknowledged':
        return 'text-warning-600 bg-warning-50';
      case 'open':
        return 'text-danger-600 bg-danger-50';
      default:
        return 'text-slate-300 bg-white/5';
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      await apiService.acknowledgeAlert(alertId);
      fetchAlerts(); // Refresh the list
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await apiService.resolveAlert(alertId);
      fetchAlerts(); // Refresh the list
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
  };

  const handlePageChange = (newPage: number) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white flex items-center">
            <Shield className="w-6 h-6 sm:w-8 sm:h-8 mr-2 text-primary-600" />
            System Alerts
          </h1>
          <p className="mt-1 text-sm sm:text-base text-slate-300 flex items-center">
            <AlertTriangle className="w-4 h-4 mr-1 text-slate-400" />
            Monitor and manage fleet alerts and notifications
          </p>
        </div>
        <div className="flex items-center space-x-3 mt-4 sm:mt-0">
          <button 
            onClick={() => window.location.reload()} 
            className="flex items-center px-3 py-2 text-sm text-slate-300 hover:text-white hover:glass-card/10 rounded-lg transition-colors"
            title="Refresh Alerts"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            <span className="hidden sm:inline">Refresh</span>
          </button>
          <div className="flex items-center text-xs sm:text-sm text-slate-400">
            <Clock className="w-4 h-4 mr-1 text-success-500" />
            <span className="hidden sm:inline">Last updated: </span>
            <span className="sm:hidden">Updated: </span>
            {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search alerts by title, description, or vehicle..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-white/20 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="pl-10 pr-8 py-2 border border-white/20 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none glass-card"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="error">Error</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
            </select>
          </div>
          <div className="relative">
            <Settings className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="pl-10 pr-8 py-2 border border-white/20 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none glass-card"
            >
              <option value="">All Status</option>
              <option value="open">Open</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={`card border-l-4 ${getSeverityColor(alert.severity)} hover:shadow-md transition-shadow duration-200`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4 flex-1">
                <div className="flex-shrink-0 mt-1">
                  {getSeverityIcon(alert.severity)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-medium text-white truncate">
                      {alert.title}
                    </h3>
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(alert.status || 'open')}`}>
                        {alert.status}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-slate-300 mb-3">{alert.description}</p>
                  
                  <div className="flex items-center justify-between text-sm text-slate-400">
                    <div className="flex items-center space-x-4">
                      {alert.vehicleId && (
                        <Link
                          to={`/vehicles/${alert.vehicleId}`}
                          className="text-primary-600 hover:text-primary-700 font-medium"
                        >
                          Vehicle #{alert.vehicleId}
                        </Link>
                      )}
                      <span>Created: {alert.createdAt ? new Date(alert.createdAt).toLocaleString() : 'N/A'}</span>
                      {alert.resolvedAt && (
                        <span>Resolved: {new Date(alert.resolvedAt).toLocaleString()}</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Actions */}
              <div className="flex items-center space-x-2 ml-4">
                {alert.status === 'open' && (
                  <>
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="p-2 text-warning-600 hover:text-warning-700 hover:bg-warning-50 rounded-lg transition-colors duration-200"
                      title="Acknowledge"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleResolve(alert.id)}
                      className="p-2 text-success-600 hover:text-success-700 hover:bg-success-50 rounded-lg transition-colors duration-200"
                      title="Resolve"
                    >
                      <CheckCircle className="w-4 h-4" />
                    </button>
                  </>
                )}
                {alert.status === 'acknowledged' && (
                  <button
                    onClick={() => handleResolve(alert.id)}
                    className="p-2 text-success-600 hover:text-success-700 hover:bg-success-50 rounded-lg transition-colors duration-200"
                    title="Resolve"
                  >
                    <CheckCircle className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {pagination.totalPages > 1 && (
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
            
            {Array.from({ length: Math.min(5, pagination.totalPages) }, (_, i) => {
              const page = i + 1;
              return (
                <button
                  key={page}
                  onClick={() => handlePageChange(page)}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    page === pagination.page
                      ? 'text-primary-600 bg-primary-50 border border-primary-300'
                      : 'text-slate-400 glass-card border border-white/20 hover:bg-white/5'
                  }`}
                >
                  {page}
                </button>
              );
            })}

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
    </div>
  );
};

export default AlertsList;