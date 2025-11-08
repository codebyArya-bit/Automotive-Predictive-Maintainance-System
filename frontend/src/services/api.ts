import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  Vehicle, 
  TelemetryData, 
  Agent, 
  MaintenanceRecord, 
  Alert, 
  DashboardMetrics,
  ApiResponse,
  PaginatedResponse 
} from '../types';
import { handleApiError, retryWithBackoff } from '../utils/errorHandler';

// Remove unused interface
// interface DashboardResponse {
//   timestamp: string;
//   agent_metrics: Record<string, any>;
//   system_metrics: Record<string, any>;
//   security_metrics: Record<string, any>;
//   recent_activities: Array<Record<string, any>>;
// }

class ApiService {
  private api: AxiosInstance;

  constructor() {
    // Read API base URL from env and normalize to avoid double "/api/v1"
    const rawApiBase = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL)
      ? import.meta.env.VITE_API_BASE_URL
      : 'http://localhost:8000';

    // Normalize: remove trailing slashes and any existing "/api/v1" suffix
    const apiBase = rawApiBase
      .replace(/\/+$/, '')
      .replace(/\/api\/v1$/, '');

    this.api = axios.create({
      baseURL: `${apiBase}/api/v1`,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Log the raw env and resolved API base URL at runtime for verification
    try {
      // eslint-disable-next-line no-console
      console.info('[ApiService] raw VITE_API_BASE_URL', rawApiBase);
      console.info('[ApiService] normalized apiBase', apiBase);
      console.info('[ApiService] baseURL', `${apiBase}/api/v1`);
    } catch (e) {
      // no-op
    }

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        const appError = handleApiError(error);
        
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        
        return Promise.reject(appError);
      }
    );
  }

  // Dashboard APIs
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    try {
      // Use the real backend dashboard endpoint
      const response = await this.api.get('/dashboard');
      
      // Transform the backend response to match frontend expectations
      const data = response.data;
      
      return {
        total_vehicles: data.system_metrics?.total_vehicles || 0,
        active_vehicles: data.system_metrics?.active_vehicles || 0,
        vehicles_in_maintenance: data.system_metrics?.vehicles_in_maintenance || 0,
        critical_alerts: data.system_metrics?.critical_alerts || 0,
        pending_maintenance: data.system_metrics?.pending_maintenance || 0,
        agent_activity: {
          active_agents: data.agent_metrics?.active_agents || 0,
          total_tasks_today: data.agent_metrics?.total_tasks_today || 0,
          avg_response_time: data.agent_metrics?.avg_response_time || 0
        },
        system_health: {
          api_status: data.system_metrics?.api_status || 'healthy',
          database_status: data.system_metrics?.database_status || 'healthy',
          cache_status: data.system_metrics?.cache_status || 'healthy'
        },
        totalVehicles: data.system_metrics?.total_vehicles || 0,
        healthyVehicles: data.system_metrics?.healthy_vehicles || 0,
        activeAlerts: data.system_metrics?.active_alerts || 0,
        maintenanceDue: data.system_metrics?.maintenance_scheduled || 0
      };
    } catch (error) {
      console.error('Error fetching dashboard metrics:', error);
      // Return mock data for development
      return {
        total_vehicles: 1247,
        active_vehicles: 1124,
        vehicles_in_maintenance: 123,
        critical_alerts: 23,
        pending_maintenance: 156,
        agent_activity: {
          active_agents: 12,
          total_tasks_today: 847,
          avg_response_time: 1.2
        },
        system_health: {
          api_status: 'healthy' as const,
          database_status: 'healthy' as const,
          cache_status: 'healthy' as const
        },
        totalVehicles: 1247,
        healthyVehicles: 1124,
        activeAlerts: 23,
        maintenanceDue: 156
      };
    }
  }

  async getRecentVehicles(limit: number = 5): Promise<Vehicle[]> {
    try {
      // Use the real backend API endpoint
      const response = await fetch(`${this.api.defaults.baseURL}/vehicles?limit=${limit}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      
      // Transform backend data to frontend format
      return data.data.map((vehicle: any) => ({
        id: vehicle.id,
        vin: vehicle.vin,
        make: vehicle.make,
        model: vehicle.model,
        year: vehicle.year,
        license_plate: vehicle.vin, // Using VIN as license plate since not in backend
        status: this.mapVehicleStatus(vehicle.status),
        owner: {
          id: 'unknown',
          name: 'Unknown Owner',
          email: 'unknown@example.com'
        },
        location: {
          latitude: 40.7589,
          longitude: -73.9851,
          address: 'Unknown Location'
        },
        last_telemetry: new Date().toISOString(),
        created_at: vehicle.registration_date || new Date().toISOString(),
        mileage: vehicle.mileage || 0
      }));
    } catch (error) {
      console.error('Error fetching vehicles:', error);
      // Fallback to mock data if API fails
      return [
        {
          id: 'VEH001',
          vin: 'VIN123456789',
          make: 'Toyota',
          model: 'Camry',
          year: 2022,
          license_plate: 'ABC123',
          status: 'active',
          owner: {
            id: 'OWN001',
            name: 'John Doe',
            email: 'john.doe@example.com'
          },
          location: {
            latitude: 40.7589,
            longitude: -73.9851,
            address: 'Downtown'
          },
          last_telemetry: '2024-01-15T10:30:00Z',
          created_at: '2022-01-01T00:00:00Z',
          mileage: 45000
        },
        {
          id: 'VEH002',
          vin: 'VIN987654321',
          make: 'Honda',
          model: 'Civic',
          year: 2023,
          license_plate: 'XYZ789',
          status: 'maintenance',
          owner: {
            id: 'OWN002',
            name: 'Jane Smith',
            email: 'jane.smith@example.com'
          },
          location: {
            latitude: 40.7128,
            longitude: -74.0060,
            address: 'Service Center'
          },
          last_telemetry: '2024-01-20T14:45:00Z',
          created_at: '2023-01-01T00:00:00Z',
          mileage: 12000
        }
      ];
    }
  }

  async getRecentAlerts(_limit: number = 5): Promise<Alert[]> {
    try {
      // Return mock data for development
      return [
        {
          id: 'ALT001',
          vehicleId: 'VEH001',
          vehicle_id: 'VEH001',
          type: 'maintenance',
          severity: 'warning',
          title: 'Brake Pad Wear',
          message: 'Brake pads showing signs of wear, replacement recommended',
          description: 'Brake pads showing signs of wear, replacement recommended',
          timestamp: '2024-01-20T10:30:00Z',
          acknowledged: false,
          resolved: false,
          status: 'open'
        },
        {
          id: 'ALT002',
          vehicleId: 'VEH003',
          vehicle_id: 'VEH003',
          type: 'system',
          severity: 'critical',
          title: 'Engine Temperature High',
          message: 'Engine temperature exceeding normal operating range',
          description: 'Engine temperature exceeding normal operating range',
          timestamp: '2024-01-20T09:15:00Z',
          acknowledged: true,
          resolved: false,
          status: 'acknowledged'
        }
      ];
    } catch (error) {
      console.error('Error fetching recent alerts:', error);
      return [];
    }
  }

  async getDashboardData(): Promise<any> {
    const response = await this.api.get('/dashboard');
    return response.data;
  }

  async getAIAgentStatus(): Promise<any[]> {
    try {
      // Return mock data for development - in production this would call /api/v1/agents/status
      return [
        {
          id: 'agent-001',
          name: 'Data Analysis Agent',
          status: 'active',
          lastActivity: '2024-01-20T11:45:00Z',
          tasksCompleted: 156,
          currentTask: 'Processing vehicle telemetry data'
        },
        {
          id: 'agent-002',
          name: 'Diagnosis Agent',
          status: 'active',
          lastActivity: '2024-01-20T11:42:00Z',
          tasksCompleted: 89,
          currentTask: 'Analyzing brake system diagnostics'
        },
        {
          id: 'agent-003',
          name: 'Manufacturing Insights Agent',
          status: 'idle',
          lastActivity: '2024-01-20T11:30:00Z',
          tasksCompleted: 234,
          currentTask: null
        }
      ];
    } catch (error) {
      console.error('Error fetching AI agent status:', error);
      return [];
    }
  }

  // Vehicle APIs
  async getVehicles(params?: {
    make?: string;
    model?: string;
    status?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<Vehicle>> {
    const response: AxiosResponse<PaginatedResponse<any>> = await this.api.get('/vehicles', { params });
    
    // Transform backend data to frontend format
    const transformedData = response.data.data.map((vehicle: any) => ({
      id: vehicle.id,
      vin: vehicle.vin,
      make: vehicle.make,
      model: vehicle.model,
      year: vehicle.year,
      license_plate: vehicle.vin, // Using VIN as license plate since not in backend
      status: this.mapVehicleStatus(vehicle.status),
      owner: {
        id: 'unknown',
        name: 'Unknown Owner',
        email: 'unknown@example.com'
      },
      location: {
        latitude: 40.7589,
        longitude: -73.9851,
        address: 'Unknown Location'
      },
      last_telemetry: new Date().toISOString(),
      created_at: vehicle.registration_date || new Date().toISOString(),
      mileage: vehicle.mileage || 0
    }));

    return {
      data: transformedData,
      pagination: response.data.pagination,
      items: transformedData,
      total: response.data.pagination.total,
      totalPages: response.data.pagination.pages
    };
  }

  async getVehicle(id: string): Promise<Vehicle> {
    const response: AxiosResponse<any> = await this.api.get(`/vehicles/${id}`);
    // Backend returns data directly, not wrapped in { data: {...} }
    const vehicle = response.data;

    // Transform backend data to frontend format
    return {
      id: vehicle.id,
      vin: vehicle.vin,
      make: vehicle.make,
      model: vehicle.model,
      year: vehicle.year,
      licensePlate: vehicle.vin, // Use camelCase for consistency
      license_plate: vehicle.vin, // Keep snake_case for compatibility
      lastUpdated: vehicle.last_service_date || new Date().toISOString(), // Use lastUpdated
      status: this.mapVehicleStatus(vehicle.status), // Map backend status to frontend status
      owner: {
        id: 'unknown',
        name: 'Unknown Owner',
        email: 'unknown@example.com'
      },
      location: {
        latitude: 40.7589,
        longitude: -73.9851,
        address: 'Unknown Location'
      },
      last_telemetry: new Date().toISOString(),
      created_at: vehicle.registration_date || new Date().toISOString(),
      mileage: vehicle.mileage || 0
    };
  }

  // Helper method to map backend vehicle status to a strict frontend union
  private mapVehicleStatus(backendStatus: string): Vehicle['status'] {
    const statusMap: Record<string, Vehicle['status']> = {
      'Active': 'active',
      'active': 'active',
      'Maintenance': 'maintenance',
      'maintenance': 'maintenance',
      'Critical': 'critical',
      'critical': 'critical',
      'Inactive': 'inactive',
      'inactive': 'inactive',
      'Warning': 'warning',
      'warning': 'warning',
      'Offline': 'offline',
      'offline': 'offline'
    };
    const mapped = statusMap[backendStatus];
    if (mapped) return mapped;
    const lower = (backendStatus || '').toLowerCase();
    const allowed: Vehicle['status'][] = ['active','inactive','maintenance','critical','healthy','warning','offline'];
    return (allowed.includes(lower as Vehicle['status']) ? (lower as Vehicle['status']) : 'inactive');
  }

  async createVehicle(vehicle: Partial<Vehicle>): Promise<Vehicle> {
    // Transform frontend format to backend format
    const backendVehicle = {
      make: vehicle.make,
      model: vehicle.model,
      year: vehicle.year,
      engine_type: 'Unknown',
      transmission_type: 'Unknown',
      mileage: vehicle.mileage || 0,
      is_active: vehicle.status === 'active'
    };

    const response: AxiosResponse<ApiResponse<any>> = await this.api.post('/vehicles', backendVehicle);
    const createdVehicle = response.data.data;
    
    // Transform backend response to frontend format
    return {
      id: createdVehicle.id,
      vin: createdVehicle.vin,
      make: createdVehicle.make,
      model: createdVehicle.model,
      year: createdVehicle.year,
      license_plate: createdVehicle.vin,
      status: this.mapVehicleStatus(createdVehicle.status),
      owner: {
        id: 'unknown',
        name: 'Unknown Owner',
        email: 'unknown@example.com'
      },
      location: {
        latitude: 40.7589,
        longitude: -73.9851,
        address: 'Unknown Location'
      },
      last_telemetry: new Date().toISOString(),
      created_at: createdVehicle.registration_date || new Date().toISOString(),
      mileage: createdVehicle.mileage || 0
    };
  }

  async updateVehicle(id: string, vehicle: Partial<Vehicle>): Promise<Vehicle> {
    // Transform frontend format to backend format
    const backendVehicle = {
      make: vehicle.make,
      model: vehicle.model,
      year: vehicle.year,
      mileage: vehicle.mileage,
      is_active: vehicle.status === 'active'
    };

    const response: AxiosResponse<ApiResponse<any>> = await this.api.put(`/vehicles/${id}`, backendVehicle);
    const updatedVehicle = response.data.data;
    
    // Transform backend response to frontend format
    return {
      id: updatedVehicle.id,
      vin: updatedVehicle.vin,
      make: updatedVehicle.make,
      model: updatedVehicle.model,
      year: updatedVehicle.year,
      license_plate: updatedVehicle.vin,
      status: this.mapVehicleStatus(updatedVehicle.status),
      owner: {
        id: 'unknown',
        name: 'Unknown Owner',
        email: 'unknown@example.com'
      },
      location: {
        latitude: 40.7589,
        longitude: -73.9851,
        address: 'Unknown Location'
      },
      last_telemetry: new Date().toISOString(),
      created_at: updatedVehicle.registration_date || new Date().toISOString(),
      mileage: updatedVehicle.mileage || 0
    };
  }

  async deleteVehicle(id: string): Promise<void> {
    await this.api.delete(`/vehicles/${id}`);
  }

  async deleteMaintenanceRecord(id: string): Promise<void> {
    await this.api.delete(`/maintenance/${id}`);
  }

  // Telemetry APIs
  async getVehicleTelemetry(vehicleId: string, params?: {
    start_date?: string;
    end_date?: string;
    limit?: number;
  }): Promise<TelemetryData[]> {
    const response: AxiosResponse<PaginatedResponse<any>> = await this.api.get(
      `/vehicles/${vehicleId}/telemetry`, 
      { params }
    );
    
    // Transform backend response to frontend format
    return response.data.data.map((item: any) => ({
      vehicle_id: item.vehicle_id,
      engine_temperature: item.engine_temp,
      oil_pressure: item.oil_pressure,
      coolant_level: item.coolant_temp,
      engine_rpm: item.engine_rpm,
      vehicle_speed: item.speed,
      fuel_level: item.fuel_level,
      battery_voltage: item.battery_voltage,
      error_codes: [],
      mileage: item.odometer || 0,
      last_service: '',
      timestamp: item.timestamp,
      // Keep both formats for compatibility
      engineRpm: item.engine_rpm,
      speed: item.speed,
      engineTemp: item.engine_temp,
      oilPressure: item.oil_pressure,
      coolantLevel: item.coolant_temp,
      fuelLevel: item.fuel_level,
      batteryVoltage: item.battery_voltage,
      errorCodes: []
    }));
  }

  async submitTelemetryData(vehicleId: string, data: Partial<TelemetryData>): Promise<TelemetryData> {
    const response: AxiosResponse<ApiResponse<TelemetryData>> = await this.api.post(
      `/vehicles/${vehicleId}/telemetry`, 
      data
    );
    return response.data.data;
  }

  // Agent APIs
  async getAgents(): Promise<Agent[]> {
    const response: AxiosResponse<ApiResponse<Agent[]>> = await this.api.get('/agents');
    return response.data.data;
  }

  async getAgentStatus(agentId: string): Promise<Agent> {
    const response: AxiosResponse<ApiResponse<Agent>> = await this.api.get(`/agents/${agentId}/status`);
    return response.data.data;
  }

  async triggerAgent(agentId: string, payload?: any): Promise<any> {
    const response = await this.api.post(`/agents/${agentId}/trigger`, payload);
    return response.data;
  }

  // Maintenance APIs
  async getMaintenanceRecords(params?: {
    vehicle_id?: string;
    status?: string;
    priority?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<MaintenanceRecord>> {
    const response: AxiosResponse<PaginatedResponse<any>> = await this.api.get('/maintenance', { params });
    
    // Transform backend response to frontend format
    const transformedData = response.data.data.map((item: any) => ({
      id: item.id,
      vehicle_id: item.vehicle_id,
      type: item.service_type,
      description: item.description,
      scheduled_date: item.start_date,
      completed_date: item.end_date,
      cost: item.cost,
      technician: item.technician,
      status: item.status,
      priority: item.priority,
      notes: item.notes,
      created_at: item.start_date
    }));

    return {
      data: transformedData,
      pagination: response.data.pagination,
      items: transformedData,
      total: response.data.pagination.total,
      totalPages: response.data.pagination.pages
    };
  }

  async createMaintenanceRecord(record: Partial<MaintenanceRecord>): Promise<MaintenanceRecord> {
    // Transform frontend format to backend format
    const backendRecord = {
      vehicle_id: record.vehicle_id,
      service_type: record.type,
      description: record.description,
      start_date: record.scheduled_date,
      end_date: record.completed_date,
      cost: record.cost,
      technician: record.technician,
      status: record.status,
      priority: record.priority,
      notes: record.notes
    };

    const response: AxiosResponse<ApiResponse<any>> = await this.api.post('/maintenance', backendRecord);
    
    // Transform backend response to frontend format
    const item = response.data.data;
    return {
      id: item.id,
      vehicle_id: item.vehicle_id,
      type: item.service_type,
      description: item.description,
      scheduled_date: item.start_date,
      completed_date: item.end_date,
      cost: item.cost,
      technician: item.technician,
      status: item.status,
      priority: item.priority,
      notes: item.notes
    };
  }

  async updateMaintenanceRecord(id: string, record: Partial<MaintenanceRecord>): Promise<MaintenanceRecord> {
    const response: AxiosResponse<ApiResponse<MaintenanceRecord>> = await this.api.put(`/maintenance/${id}`, record);
    return response.data.data;
  }

  // Alert APIs
  async getAlerts(params?: {
    vehicle_id?: string;
    severity?: string;
    acknowledged?: boolean;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<Alert>> {
    const response: AxiosResponse<PaginatedResponse<Alert>> = await this.api.get('/alerts', { params });
    return response.data;
  }

  async acknowledgeAlert(id: string): Promise<Alert> {
    const response: AxiosResponse<ApiResponse<Alert>> = await this.api.post(`/alerts/${id}/acknowledge`);
    return response.data.data;
  }

  async resolveAlert(id: string): Promise<Alert> {
    const response: AxiosResponse<ApiResponse<Alert>> = await this.api.post(`/alerts/${id}/resolve`);
    return response.data.data;
  }

  // Demo APIs
  async runDemo(scenario: string): Promise<any> {
    const response = await this.api.post('/demo/run', { scenario });
    return response.data;
  }

  async getDemoScenarios(): Promise<string[]> {
    const response = await this.api.get('/demo/scenarios');
    return response.data.scenarios;
  }

  // Analytics APIs
  async getAnalytics(params?: {
    metric?: string;
    start_date?: string;
    end_date?: string;
    vehicle_id?: string;
  }): Promise<any> {
    const response = await this.api.get('/analytics', { params });
    return response.data;
  }

  // Health Check
  async healthCheck(): Promise<any> {
    const response = await this.api.get('/health');
    return response.data;
  }

  // Missing methods for components
  async getMaintenance(_params?: {
    vehicle_id?: string;
    status?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<MaintenanceRecord>> {
    // Mock data for now since backend doesn't have this endpoint
    return {
      data: [],
      pagination: { page: 1, limit: 10, total: 0, pages: 0 },
      items: [],
      total: 0,
      totalPages: 0
    };
  }

  async getVehicleMaintenance(_vehicleId: string): Promise<MaintenanceRecord[]> {
    // Mock data for now
    return [];
  }

  async getVehicleAlerts(_vehicleId: string): Promise<Alert[]> {
    // Mock data for now
    return [];
  }

  // Generic API methods with retry logic
  async get<T = any>(url: string, config?: any): Promise<T> {
    return retryWithBackoff(
      () => this.api.get(url, config).then(response => response.data),
      3,
      1000,
      `GET ${url}`
    );
  }

  async post<T = any>(url: string, data?: any, config?: any): Promise<T> {
    return retryWithBackoff(
      () => this.api.post(url, data, config).then(response => response.data),
      2, // Fewer retries for POST requests
      1000,
      `POST ${url}`
    );
  }

  async put<T = any>(url: string, data?: any, config?: any): Promise<T> {
    return retryWithBackoff(
      () => this.api.put(url, data, config).then(response => response.data),
      2,
      1000,
      `PUT ${url}`
    );
  }

  async delete<T = any>(url: string, config?: any): Promise<T> {
    return retryWithBackoff(
      () => this.api.delete(url, config).then(response => response.data),
      2,
      1000,
      `DELETE ${url}`
    );
  }

  // ========================================================================
  // NEW ENHANCED FEATURES - Authentication, Forecasting, RCA/CAPA, Voice Agent
  // ========================================================================

  // Authentication APIs
  async login(email: string, password: string): Promise<{ token: string; user: any }> {
    const response = await this.api.post('/auth/login', { email, password });
    const { token, user } = response.data;

    // Store token
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify(user));

    return { token, user };
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/auth/logout');
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
    }
  }

  async getCurrentUser(): Promise<any> {
    const response = await this.api.get('/auth/me');
    return response.data;
  }

  // Service Demand Forecasting APIs
  async getDemandForecast(days: number = 30): Promise<any> {
    const response = await this.api.get('/demand-forecast', { params: { days } });
    const data = response.data || {};
    const rawForecast = data.forecast || {};

    // Normalize backend shape to match UI expectations
    const daily: any[] = Array.isArray(rawForecast.daily_forecast) ? rawForecast.daily_forecast : [];
    const periodDays: number = Number(rawForecast.forecast_period_days || daily.length || days) || days;

    const start = new Date();
    const end = new Date(start);
    end.setDate(start.getDate() + periodDays - 1);

    const daily_forecast = daily.map((value, idx) => {
      const demand = typeof value === 'number' ? value : Number(value) || 0;
      const date = new Date(start.getTime() + idx * 24 * 60 * 60 * 1000).toISOString();
      return {
        date,
        predicted_demand: demand,
        confidence: 0.9,
      };
    });

    const total = daily.reduce((acc, v) => acc + (typeof v === 'number' ? v : Number(v) || 0), 0);
    const avg = daily.length ? total / daily.length : 0;
    const peak = daily.length ? Math.max(...daily.map(v => (typeof v === 'number' ? v : Number(v) || 0))) : 0;
    const peakIndex = daily.indexOf(peak);
    const peakDate = new Date(start.getTime() + (peakIndex >= 0 ? peakIndex : 0) * 24 * 60 * 60 * 1000).toISOString();

    const forecast_period = {
      start_date: start.toISOString(),
      end_date: end.toISOString(),
      total_days: periodDays,
    };

    const summary = {
      average_daily_demand: Number(avg.toFixed(1)),
      peak_demand: Number(peak),
      peak_date: peakDate,
      total_predicted_demand: Number(total.toFixed(1)),
    };

    const normalizedForecast = {
      forecast_period,
      daily_forecast,
      summary,
    };

    return {
      status: data.status,
      forecast: normalizedForecast,
      generated_at: data.generated_at,
    };
  }

  async getDemandSummary(): Promise<any> {
    const response = await this.api.get('/demand-forecast/summary');
    return response.data;
  }

  async getServiceCenterCapacity(): Promise<any> {
    const response = await this.api.get('/service-centers/capacity');
    const data = response.data || {};
    const analysis = data.capacity_analysis || {};
    const centers = analysis.center_analysis || {};

    const service_centers = Object.entries(centers).map(([name, info]: [string, any], idx) => {
      const capacity = Number(info?.capacity || 0);
      const forecastedDemand = Number(info?.forecasted_demand || 0);
      const utilizationPct = Number(info?.forecasted_utilization || 0);
      const availableSlots = Math.max(0, capacity - Math.round(forecastedDemand));
      const centerId = `center_${idx + 1}`;
      const location = name.replace(/^[^_]*_/,'').replace('_',' ');

      return {
        center_id: centerId,
        name,
        location,
        capacity: {
          daily_capacity: capacity,
          current_utilization: Number(utilizationPct.toFixed(1)),
          available_slots: availableSlots,
        },
        staffing: {
          current_staff: Math.max(1, Math.ceil(capacity / 5)),
          recommended_staff: Math.max(1, Math.ceil(forecastedDemand / 5)),
          utilization_rate: Number(utilizationPct.toFixed(1)),
        },
      };
    });

    const staffing_recommendations = (analysis.capacity_warnings || []).map((w: any) => ({
      recommendation: w.recommendation || 'Monitor and adjust staffing',
      priority: (w.severity || 'medium').toUpperCase(),
      impact: 'Improves throughput and reduces wait times',
    }));

    const optimization_opportunities = (analysis.capacity_warnings || []).map((w: any) => ({
      opportunity: w.message || 'Optimize scheduling around peak demand',
      potential_savings: '$5,000/month',
      implementation_complexity: (w.severity || 'medium'),
    }));

    return {
      status: data.status,
      capacity: {
        service_centers,
        staffing_recommendations,
        optimization_opportunities,
      },
      timestamp: data.timestamp,
    };
  }

  // RCA/CAPA APIs
  async getRCAReports(): Promise<any> {
    const response = await this.api.get('/rca-reports');
    return response.data;
  }

  async getRCAReportById(defectId: string): Promise<any> {
    const response = await this.api.get(`/rca-reports/${defectId}`);
    return response.data;
  }

  async getRecurringDefects(): Promise<any> {
    const response = await this.api.get('/recurring-defects');
    return response.data;
  }

  async getManufacturingFeedback(): Promise<any> {
    const response = await this.api.get('/manufacturing-feedback');
    return response.data;
  }

  // Edge Case Scenarios APIs
  async getEdgeCaseScenarios(): Promise<any> {
    const response = await this.api.get('/edge-cases/scenarios');
    return response.data;
  }

  async runEdgeCaseScenario(scenarioName: string): Promise<any> {
    const response = await this.api.post(`/edge-cases/run/${scenarioName}`);
    return response.data;
  }

  // Voice Agent APIs
  async initiateVoiceCall(vehicleId: string, customerId: string, priority: string): Promise<any> {
    const response = await this.api.post('/voice-agent/initiate-call', {
      vehicle_id: vehicleId,
      customer_id: customerId,
      priority
    });
    const data = response.data || {};
    const call = data.call || {};
    let conversationScript = call.conversation_script;

    // Normalize backend shape: backend returns an array of messages, while
    // the frontend expects an object with a `conversation` array.
    if (Array.isArray(conversationScript)) {
      const urgency = (priority === 'P0' || priority === 'P1') ? 'high' : 'normal';
      conversationScript = {
        priority: priority,
        urgency_level: urgency,
        conversation: conversationScript,
        key_points: [],
        expected_outcome: urgency === 'high' ? 'emergency_handled' : 'appointment_booked'
      };
    }

    return {
      ...data,
      call: {
        ...call,
        conversation_script: conversationScript
      }
    };
  }

  async getCallHistory(customerId?: string): Promise<any> {
    const params = customerId ? { customer_id: customerId } : {};
    const response = await this.api.get('/voice-agent/call-history', { params });
    return response.data;
  }

  // Role-Based Dashboard APIs
  async getCustomerDashboard(): Promise<any> {
    const response = await this.api.get('/dashboard/customer');
    return response.data;
  }

  async getServiceStaffDashboard(): Promise<any> {
    const response = await this.api.get('/dashboard/service-staff');
    return response.data;
  }

  async getManufacturingDashboard(): Promise<any> {
    const response = await this.api.get('/dashboard/manufacturing');
    return response.data;
  }

  async getAdminDashboard(): Promise<any> {
    const response = await this.api.get('/dashboard/admin');
    return response.data;
  }

  // Logs APIs
  async getLogs(params: {
    level?: string;
    source?: string;
    type?: string;
    q?: string;
    limit?: number;
    from?: string;
    to?: string;
    since_minutes?: number;
  } = {}): Promise<any> {
    const response = await this.api.get('/logs', { params });
    return response.data;
  }

  async getLogStats(windowMinutes: number = 60): Promise<any> {
    const response = await this.api.get('/logs/stats', { params: { window_minutes: windowMinutes } });
    return response.data;
  }

  async getLogSuggestions(recentN: number = 100): Promise<any> {
    const response = await this.api.get('/logs/suggestions', { params: { recent_n: recentN } });
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;