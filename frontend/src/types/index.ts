// Vehicle Types
export interface Vehicle {
  id: string;
  vin: string;
  make: string;
  model: string;
  year: number;
  license_plate: string;
  licensePlate?: string; // camelCase version
  status: 'active' | 'inactive' | 'maintenance' | 'critical' | 'healthy' | 'warning' | 'offline';
  owner: {
    id: string;
    name: string;
    email: string;
  };
  location?: {
    latitude: number;
    longitude: number;
    address: string;
  };
  last_telemetry: string;
  created_at: string;
  mileage?: number;
  lastUpdated?: string; // ISO date string
}

// Telemetry Data Types
export interface TelemetryData {
  vehicle_id: string;
  engine_temperature: number;
  oil_pressure: number;
  coolant_level: number;
  engine_rpm: number;
  vehicle_speed: number;
  fuel_level: number;
  battery_voltage: number;
  error_codes: string[];
  mileage: number;
  last_service: string;
  timestamp: string;
  engineRpm?: number;
  speed?: number;
  engineTemp?: number;
  oilPressure?: number;
  coolantLevel?: number;
  fuelLevel?: number;
  batteryVoltage?: number;
  errorCodes?: string[];
}

// Agent Types
export interface Agent {
  id: string;
  name: string;
  type: 'diagnosis' | 'data_analysis' | 'customer_engagement' | 'scheduling' | 'feedback' | 'manufacturing' | 'ueba';
  status: 'active' | 'idle' | 'processing' | 'error';
  last_activity: string;
  tasks_completed: number;
  current_task?: string;
  tasksProcessed?: number;
  avgResponseTime?: number;
  uptime?: string;
  description?: string;
  version?: string;
  createdAt?: string;
  lastUpdated?: string;
}

// Maintenance Types
export interface MaintenanceRecord {
  id: string;
  vehicle_id: string;
  type: 'scheduled' | 'predictive' | 'emergency';
  priority: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  scheduled_date?: string;
  completed_date?: string;
  cost?: number;
  technician?: string;
  parts_required?: string[];
  parts_used?: string[];
  notes?: string;
  vehicleId?: string;
  vehicleInfo?: any;
  scheduledDate?: string;
  service_type?: string;
}

// Alert Types
export interface Alert {
  id: string;
  vehicle_id: string;
  type: 'maintenance' | 'safety' | 'performance' | 'system';
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
  resolved: boolean;
  status?: 'open' | 'acknowledged' | 'resolved' | 'closed';
  description?: string;
  vehicleId?: string;
  createdAt?: string;
  resolvedAt?: string;
}

// Dashboard Metrics
export interface DashboardMetrics {
  total_vehicles: number;
  active_vehicles: number;
  vehicles_in_maintenance: number;
  critical_alerts: number;
  pending_maintenance: number;
  agent_activity: {
    active_agents: number;
    total_tasks_today: number;
    avg_response_time: number;
  };
  system_health: {
    api_status: 'healthy' | 'degraded' | 'down';
    database_status: 'healthy' | 'degraded' | 'down';
    cache_status: 'healthy' | 'degraded' | 'down';
  };
  totalVehicles?: number;
  healthyVehicles?: number;
  activeAlerts?: number;
  maintenanceDue?: number;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
  items?: T[];
  total?: number;
  totalPages?: number;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: 'vehicle_update' | 'alert' | 'agent_activity' | 'maintenance_update';
  payload: any;
  timestamp: string;
}

// Chart Data Types
export interface ChartDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface MetricTrend {
  current: number;
  previous: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
  value?: number;
  direction?: 'up' | 'down' | 'stable';
}