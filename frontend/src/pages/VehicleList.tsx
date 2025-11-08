import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Car, 
  Search, 
  Filter, 
  Eye, 
  AlertTriangle,
  CheckCircle,
  Clock,
  MapPin,
  Settings,
  Users,
  Plus
} from 'lucide-react';
import { apiService } from '../services/api';
import { Vehicle, PaginatedResponse } from '../types';
import VehicleForm from '../components/VehicleForm';

const VehicleList: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [makeFilter, setMakeFilter] = useState('');
  const [showVehicleForm, setShowVehicleForm] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0
  });

  // Get unique makes from vehicles for filter dropdown
  const uniqueMakes = [...new Set(vehicles.map(v => v.make).filter(Boolean))];

  // Handler for adding new vehicle
  const handleAddVehicle = async (vehicleData: any) => {
    try {
      await apiService.createVehicle(vehicleData);
      setShowVehicleForm(false);
      // Refresh the vehicle list
      fetchVehicles();
    } catch (error) {
      console.error('Failed to add vehicle:', error);
    }
  };

  useEffect(() => {
    fetchVehicles();
  }, [pagination.page, statusFilter, searchTerm]);

  const fetchVehicles = async () => {
    try {
      setLoading(true);
      const params: any = {
        page: pagination.page,
        limit: pagination.limit
      };

      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }

      if (searchTerm) {
        params.search = searchTerm;
      }

      const response: PaginatedResponse<Vehicle> = await apiService.getVehicles(params);
      setVehicles(response.items || response.data || []);
      setPagination(prev => ({
        ...prev,
        total: response.total || response.pagination?.total || 0,
        totalPages: response.totalPages || response.pagination?.pages || 0
      }));
    } catch (error) {
      console.error('Failed to fetch vehicles:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'operational':
        return <CheckCircle className="w-5 h-5 text-success-500" />;
      case 'warning':
      case 'maintenance_due':
        return <Clock className="w-5 h-5 text-warning-500" />;
      case 'critical':
      case 'breakdown':
        return <AlertTriangle className="w-5 h-5 text-danger-500" />;
      default:
        return <Car className="w-5 h-5 text-slate-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'operational':
        return 'text-emerald-300 bg-emerald-500/20';
      case 'warning':
      case 'maintenance_due':
        return 'text-amber-300 bg-amber-500/20';
      case 'critical':
      case 'breakdown':
        return 'text-rose-300 bg-rose-500/20';
      default:
        return 'text-slate-300 bg-white/5';
    }
  };

  const handlePageChange = (newPage: number) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white flex items-center">
            <Car className="w-6 h-6 sm:w-8 sm:h-8 mr-2 text-cyan-300" />
            Vehicle Fleet
          </h1>
          <p className="mt-1 text-sm sm:text-base text-slate-300 flex items-center">
            <Users className="w-4 h-4 mr-1 text-slate-400" />
            Manage and monitor your entire vehicle fleet
          </p>
        </div>
        <div className="flex items-center space-x-3 mt-4 sm:mt-0">
          <button 
            onClick={() => setShowVehicleForm(true)}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Vehicle
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search vehicles by VIN, make, model..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-white/20 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="pl-10 pr-8 py-2 border border-white/20 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none bg-white/10 backdrop-blur-xl"
            >
              <option value="">All Status</option>
              <option value="healthy">Healthy</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
              <option value="maintenance_due">Maintenance Due</option>
            </select>
          </div>
          <div className="relative">
            <Settings className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <select
              value={makeFilter}
              onChange={(e) => setMakeFilter(e.target.value)}
              className="pl-10 pr-8 py-2 border border-white/20 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none bg-white/10 backdrop-blur-xl"
            >
              <option value="">All Makes</option>
              {uniqueMakes.map(make => (
                <option key={make} value={make}>{make}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Vehicle Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {vehicles.map((vehicle) => (
            <div
              key={vehicle.id}
              className="group relative bg-white/10 backdrop-blur-xl rounded-xl border border-white/10 overflow-hidden transition-all duration-300 hover:shadow-2xl hover:-translate-y-2 hover:border-cyan-400/40"
            >
              {/* Animated gradient overlay on hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/0 via-blue-500/0 to-purple-500/0 group-hover:from-cyan-500/20 group-hover:via-blue-500/10 group-hover:to-purple-500/20 transition-all duration-500 pointer-events-none"></div>

              {/* Glowing border effect on hover */}
              <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-400 via-blue-400 to-purple-400 blur-sm"></div>
              </div>

              {/* Card content */}
              <div className="relative p-6">
                {/* Header with icon and status */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <div className="w-14 h-14 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-xl flex items-center justify-center mr-3 transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-md group-hover:shadow-lg">
                      <Car className="w-7 h-7 text-cyan-300 group-hover:text-cyan-200 transition-colors" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white group-hover:text-cyan-200 transition-colors text-lg">
                        {vehicle.make} {vehicle.model}
                      </h3>
                      <p className="text-sm text-slate-400 font-medium">{vehicle.year}</p>
                    </div>
                  </div>
                  <div className="flex items-center transform group-hover:scale-110 transition-transform duration-300">
                    {getStatusIcon(vehicle.status)}
                  </div>
                </div>

                {/* Vehicle details with enhanced styling */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between py-2 border-b border-white/5 group-hover:border-cyan-400/20 transition-colors">
                    <span className="text-sm font-medium text-slate-300">VIN</span>
                    <span className="text-sm font-mono font-semibold text-white bg-white/5 px-2 py-1 rounded group-hover:bg-cyan-500/20 group-hover:text-cyan-200 transition-all">
                      {vehicle.vin.slice(-8)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-2 border-b border-white/5 group-hover:border-cyan-400/20 transition-colors">
                    <span className="text-sm font-medium text-slate-300">License Plate</span>
                    <span className="text-sm font-bold text-white bg-gradient-to-r from-gray-50 to-gray-100 px-3 py-1 rounded-lg group-hover:from-primary-50 group-hover:to-blue-50 group-hover:text-cyan-200 transition-all">
                      {vehicle.licensePlate}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-2 border-b border-white/5 group-hover:border-cyan-400/20 transition-colors">
                    <span className="text-sm font-medium text-slate-300">Mileage</span>
                    <span className="text-sm font-semibold text-white group-hover:text-cyan-200 transition-colors">
                      {vehicle.mileage ? vehicle.mileage.toLocaleString() : '0'} mi
                    </span>
                  </div>

                  {vehicle.location && (
                    <div className="flex items-center justify-between py-2 border-b border-white/5 group-hover:border-cyan-400/20 transition-colors">
                      <span className="text-sm font-medium text-slate-300">Location</span>
                      <div className="flex items-center text-sm font-semibold text-white group-hover:text-cyan-200 transition-colors">
                        <MapPin className="w-4 h-4 mr-1 group-hover:animate-bounce" />
                        {vehicle.location.address.split(',')[0]}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between py-2">
                    <span className="text-sm font-medium text-slate-300">Status</span>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold shadow-sm transform group-hover:scale-105 transition-transform ${getStatusColor(vehicle.status)}`}>
                      {vehicle.status}
                    </span>
                  </div>
                </div>

                {/* Last updated info */}
                <div className="mb-4 p-3 bg-white/5 rounded-lg group-hover:bg-gradient-to-r group-hover:from-primary-50 group-hover:to-blue-50 transition-all">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-slate-400 group-hover:text-cyan-300 transition-colors">
                      Last Updated
                    </span>
                    <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-200 transition-colors">
                      {vehicle.lastUpdated ? new Date(vehicle.lastUpdated).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      }) : new Date().toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </span>
                  </div>
                </div>

                {/* Enhanced action button */}
                <Link
                  to={`/vehicles/${vehicle.id}`}
                  className="w-full flex items-center justify-center px-4 py-3 bg-gradient-to-r from-primary-600 to-blue-600 text-white rounded-lg font-semibold shadow-md hover:shadow-xl hover:from-primary-700 hover:to-blue-700 transform hover:scale-105 transition-all duration-300 group-hover:animate-pulse"
                >
                  <Eye className="w-5 h-5 mr-2 group-hover:animate-pulse" />
                  View Details
                </Link>
              </div>

              {/* Corner accent decoration */}
              <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-primary-400/10 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="absolute bottom-0 left-0 w-16 h-16 bg-gradient-to-tr from-blue-400/10 to-transparent rounded-tr-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            </div>
          ))}
        </div>
      )}

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
              className="px-3 py-2 text-sm font-medium text-slate-400 bg-white/10 backdrop-blur-xl border border-white/20 rounded-md hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed"
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
                      ? 'text-cyan-300 bg-primary-50 border border-primary-300'
                      : 'text-slate-400 bg-white/10 backdrop-blur-xl border border-white/20 hover:bg-white/5'
                  }`}
                >
                  {page}
                </button>
              );
            })}

            <button
              onClick={() => handlePageChange(pagination.page + 1)}
              disabled={pagination.page === pagination.totalPages}
              className="px-3 py-2 text-sm font-medium text-slate-400 bg-white/10 backdrop-blur-xl border border-white/20 rounded-md hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Vehicle Form Modal */}
      {showVehicleForm && (
        <VehicleForm
          onSubmit={handleAddVehicle}
          onCancel={() => setShowVehicleForm(false)}
        />
      )}
    </div>
  );
};

export default VehicleList;