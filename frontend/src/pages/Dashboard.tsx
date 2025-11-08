import React, { useState, useEffect } from 'react';
import { 
  Car, 
  Activity, 
  AlertTriangle, 
  Wrench, 
  TrendingUp, 
  CheckCircle, 
  Clock, 
  Zap, 
  Users, 
  MapPin, 
  Fuel, 
  BarChart3, 
  RefreshCw,
  Bell,
  Settings,
  Shield,
  Target,
  Calendar,
  Filter,
  Wifi,
  WifiOff,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
interface DashboardMetrics {
  totalVehicles: number;
  healthyVehicles: number;
  activeAlerts: number;
  maintenanceDue: number;
  avgFuelEfficiency?: number;
  totalMileage?: number;
  uptime?: number;
}
interface Vehicle {
  id: string;
  vin: string;
  make: string;
  model: string;
  year: number;
  status: string;
  mileage?: number;
  lastUpdate?: string;
  fuelLevel?: number;
  batteryLevel?: number;
}
interface Alert {
  id: string;
  title: string;
  description?: string;
  message?: string;
  severity: string;
  timestamp: string;
  vehicleId?: string;
  resolved?: boolean;
}
interface AIAgentStatus {
  id: string;
  name: string;
  status: string;
  lastActive: string;
  tasksCompleted: number;
  performance: number;
}
interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string[];
    borderColor?: string;
    borderWidth?: number;
  }>;
}
import {
  LineChart,
  AreaChart,
  BarChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  Bar,
  Line,
  PieChart,
  Cell,
  Pie
} from 'recharts';
import apiService from '../services/api';
import config from '../config';
import { useApiWithRetry } from '../hooks/useApiWithRetry';
import useWebSocket from '../hooks/useWebSocket';
import { getAccentGradient, getStatusToken } from '../config/theme';
import { mockFleetMetrics, mockVehicleActivity, mockAgentStatuses } from '../data/mockInsights';
// Sample data for charts
const recentActivityData = [
  { time: '00:00', vehicles: 180, alerts: 2, maintenance: 1 },
  { time: '04:00', vehicles: 165, alerts: 1, maintenance: 2 },
  { time: '08:00', vehicles: 220, alerts: 5, maintenance: 3 },
  { time: '12:00', vehicles: 245, alerts: 8, maintenance: 2 },
  { time: '16:00', vehicles: 235, alerts: 6, maintenance: 4 },
  { time: '20:00', vehicles: 210, alerts: 3, maintenance: 1 }
];
const alertsData = [
  { type: 'Critical', count: 5, color: '#EF4444' },
  { type: 'Warning', count: 12, color: '#F59E0B' },
  { type: 'Info', count: 8, color: '#3B82F6' }
];
const maintenanceStatusData = [
  { day: 'Mon', scheduled: 8, completed: 6, pending: 2 },
  { day: 'Tue', scheduled: 12, completed: 10, pending: 2 },
  { day: 'Wed', scheduled: 6, completed: 5, pending: 1 },
  { day: 'Thu', scheduled: 15, completed: 12, pending: 3 },
  { day: 'Fri', scheduled: 9, completed: 8, pending: 1 },
  { day: 'Sat', scheduled: 4, completed: 4, pending: 0 },
  { day: 'Sun', scheduled: 3, completed: 2, pending: 1 }
];
const Dashboard: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [realTimeData, setRealTimeData] = useState<any>(null);
  
  const { executeWithFallback } = useApiWithRetry();
  
  // WebSocket connection for real-time updates
  const { 
    isConnected: wsConnected, 
    sendMessage
  } = useWebSocket(`${config.wsUrl}/dashboard`, {
    onMessage: (data) => {
      setRealTimeData(data);
      setLastUpdated(new Date());
    },
    onError: () => {
      console.warn('WebSocket connection failed, falling back to polling');
    }
  });
  // Auto-refresh functionality with WebSocket fallback
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const response = await executeWithFallback(
          () => apiService.get('/api/dashboard/metrics'),
          'Failed to fetch dashboard metrics'
        );
        if (response && !wsConnected) {
          setRealTimeData(response.data);
          setLastUpdated(new Date());
        }
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
    
    // Only use polling if WebSocket is not connected
    let interval: NodeJS.Timeout | null = null;
    if (!wsConnected) {
      interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [selectedTimeRange, executeWithFallback, wsConnected]);
  
  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      if (wsConnected) {
        sendMessage({ type: 'refresh_dashboard' });
      } else {
        const response = await executeWithFallback(
          () => apiService.get('/api/dashboard/metrics'),
          'Failed to refresh dashboard metrics'
        );
        if (response) {
          setRealTimeData(response.data);
          setLastUpdated(new Date());
        }
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  const fallbackMetrics = mockFleetMetrics;
  const resolvedMetrics = {
    totalVehicles: realTimeData?.system_metrics?.total_vehicles ?? realTimeData?.totalVehicles ?? fallbackMetrics.totalVehicles,
    healthyVehicles: realTimeData?.system_metrics?.healthy_vehicles ?? realTimeData?.healthyVehicles ?? fallbackMetrics.healthyVehicles,
    activeAlerts: realTimeData?.system_metrics?.active_alerts ?? realTimeData?.activeAlerts ?? fallbackMetrics.activeAlerts,
    maintenanceDue: realTimeData?.system_metrics?.maintenance_scheduled ?? realTimeData?.maintenanceDue ?? fallbackMetrics.maintenanceDue,
    avgFuelEfficiency: realTimeData?.telemetry?.avg_fuel_efficiency ?? fallbackMetrics.avgFuelEfficiency,
    uptime: realTimeData?.system_metrics?.uptime ?? fallbackMetrics.uptime,
  };
  
  const fleetAvailability = resolvedMetrics.totalVehicles
    ? Math.round((resolvedMetrics.healthyVehicles / resolvedMetrics.totalVehicles) * 100)
    : 0;
  
  const primaryMetrics: Array<{
    label: string;
    value: string;
    delta: string;
    icon: React.ElementType;
    trend: 'up' | 'down' | 'flat';
    detail: string;
  }> = [
    {
      label: 'Total Vehicles',
      value: resolvedMetrics.totalVehicles.toLocaleString(),
      delta: '+5 vs last week',
      icon: Car,
      trend: 'up',
      detail: 'Global fleet coverage',
    },
    {
      label: 'Healthy Vehicles',
      value: resolvedMetrics.healthyVehicles.toLocaleString(),
      delta: `${fleetAvailability}% availability`,
      icon: CheckCircle,
      trend: 'up',
      detail: 'Predictive models tracking',
    },
    {
      label: 'Active Alerts',
      value: resolvedMetrics.activeAlerts.toString(),
      delta: '-12% vs 24h',
      icon: AlertTriangle,
      trend: 'down',
      detail: 'Auto-triaged incidents',
    },
    {
      label: 'Maintenance Due',
      value: resolvedMetrics.maintenanceDue.toString(),
      delta: 'Next 7 day window',
      icon: Wrench,
      trend: 'flat',
      detail: 'AI scheduled services',
    },
  ];
  
  const vehicleActivities = realTimeData?.recent_activities ?? mockVehicleActivity;
  const agentPulse = realTimeData?.agent_metrics?.agents ?? mockAgentStatuses;
  
  const systemHealth: Array<{
    label: string;
    status: string;
    detail: string;
    icon: React.ElementType;
  }> = [
    {
      label: 'API Server',
      status: realTimeData?.system_health?.api_status ?? 'healthy',
      detail: 'Latency 118 ms',
      icon: Activity,
    },
    {
      label: 'Database',
      status: realTimeData?.system_health?.database_status ?? 'healthy',
      detail: 'Replica sync 99.99%',
      icon: CheckCircle,
    },
    {
      label: 'Cache Layer',
      status: realTimeData?.system_health?.cache_status ?? 'warning',
      detail: 'Evictions 1.2%',
      icon: Zap,
    },
    {
      label: 'AI Agents',
      status: realTimeData?.agent_metrics?.status ?? 'healthy',
      detail: `${agentPulse.length}+ models online`,
      icon: Users,
    },
  ];

  return (
    <div className="space-y-8 text-slate-100">
      <div className="glass-card relative overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-500/20 hover:border-cyan-400/30">
        <div className="absolute inset-0 opacity-30 blur-3xl pointer-events-none bg-gradient-to-r from-cyan-500 to-blue-500" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-300">Live Fleet Telemetry</p>
            <h1 className="text-3xl font-bold gradient-title flex items-center gap-3 mt-2">
              <BarChart3 className="w-8 h-8 text-cyan-300" />
              Fleet Command Center
            </h1>
            <p className="mt-2 text-slate-300 flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-300" />
              Real-time vehicle health, alerts, and agent automation signals
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="flex items-center gap-2 rounded-full border border-white/15 px-3 py-1.5 text-xs uppercase tracking-wide">
              {wsConnected ? (
                <>
                  <Wifi className="w-4 h-4 text-emerald-300" />
                  <span className="text-emerald-200 font-semibold">Live WebSocket</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-amber-300" />
                  <span className="text-amber-200 font-semibold">Polling Fallback</span>
                </>
              )}
            </div>
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="bg-white/5 border border-white/15 rounded-lg px-4 py-2 text-sm text-white focus:ring-2 focus:ring-cyan-300/50"
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleRefresh}
              className="btn-primary flex items-center gap-2 text-sm"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh Pulse
            </button>
            <button className="btn-ghost flex items-center gap-2 text-sm">
              <Bell className="w-4 h-4" />
              Auto-Alert
            </button>
            <button className="btn-ghost flex items-center gap-2 text-sm">
              <Filter className="w-4 h-4" />
              Filters
            </button>
          </div>
        </div>
        <div className="mt-4 flex items-center gap-4 text-xs text-slate-300">
          <Clock className="w-4 h-4 text-cyan-300" />
          Updated {lastUpdated.toLocaleTimeString()}
          <span className="w-px h-4 bg-white/20" />
          <span className="flex items-center gap-2">
            <Settings className="w-4 h-4 text-cyan-300" />
            Orchestrations synchronized
          </span>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        {primaryMetrics.map((metric, index) => {
          const TrendIcon = metric.trend === 'down' ? ArrowDownRight : ArrowUpRight;
          const trendClass =
            metric.trend === 'down'
              ? 'text-amber-300'
              : metric.trend === 'flat'
              ? 'text-slate-300'
              : 'text-emerald-300';
          return (
            <div key={metric.label} className="glass-card relative overflow-hidden p-5 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/20 hover:border-cyan-400/40 cursor-pointer group">
              <div className={`absolute inset-0 opacity-40 blur-3xl pointer-events-none ${getAccentGradient(index)} group-hover:opacity-60 transition-opacity duration-300`} />
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-300 group-hover:text-cyan-200 transition-colors">{metric.label}</p>
                    <p className="text-3xl font-bold text-white mt-1 group-hover:text-cyan-100 transition-colors">{metric.value}</p>
                  </div>
                  <div className="p-3 rounded-xl bg-white/10 border border-white/20 group-hover:bg-white/20 group-hover:border-cyan-400/50 group-hover:scale-110 transition-all duration-300">
                    <metric.icon className="w-6 h-6 text-white group-hover:text-cyan-300 transition-colors" />
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-300 group-hover:text-slate-200 transition-colors">{metric.detail}</span>
                  <span className={`inline-flex items-center gap-1 ${trendClass} group-hover:scale-110 transition-transform`}>
                    <TrendIcon className="w-4 h-4" />
                    {metric.delta}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="glass-card xl:col-span-2 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10 hover:border-cyan-400/30 hover:scale-[1.01]">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Target className="w-5 h-5 text-cyan-300" />
                Fleet Activity Signal
              </h3>
              <p className="text-sm text-slate-300">Vehicles, alerts and maintenance interactions (UTC)</p>
            </div>
            <div className="flex items-center gap-4 text-sm text-slate-300">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-sky-400" />
                Vehicles
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-rose-400" />
                Alerts
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                Maintenance
              </div>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={recentActivityData}>
                <defs>
                  <linearGradient id="colorVehicles" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorAlerts" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#fb7185" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#fb7185" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorMaintenance" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#34d399" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#34d399" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                <XAxis dataKey="time" stroke="#94a3b8" />
                <YAxis yAxisId="left" stroke="#94a3b8" />
                <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', borderColor: 'rgba(255,255,255,0.1)' }} />
                <Legend />
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="vehicles"
                  stroke="#38bdf8"
                  fillOpacity={1}
                  fill="url(#colorVehicles)"
                  strokeWidth={3}
                />
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey="alerts"
                  stroke="#fb7185"
                  fillOpacity={1}
                  fill="url(#colorAlerts)"
                  strokeWidth={2}
                />
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey="maintenance"
                  stroke="#34d399"
                  fillOpacity={1}
                  fill="url(#colorMaintenance)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="glass-card transition-all duration-300 hover:shadow-2xl hover:shadow-amber-500/10 hover:border-amber-400/30 hover:scale-[1.01]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-300" />
                Alert Composition
              </h3>
              <p className="text-sm text-slate-300">Current open incidents by severity</p>
            </div>
            <button className="btn-ghost text-xs px-3 py-1.5">Details</button>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={alertsData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={120}
                  dataKey="count"
                >
                  {alertsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', borderColor: 'rgba(255,255,255,0.1)' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-3 gap-3 mt-4">
            {alertsData.map((alert) => (
              <div key={alert.type} className="glass-panel rounded-lg p-3 text-center border border-white/10 hover:border-amber-300/40 hover:bg-white/10 hover:scale-105 transition-all duration-200 cursor-pointer">
                <p className="text-xs uppercase tracking-wide text-slate-300">{alert.type}</p>
                <p className="text-2xl font-semibold text-white">{alert.count}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="glass-card xl:col-span-2 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10 hover:border-cyan-400/30 hover:scale-[1.01]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Calendar className="w-5 h-5 text-cyan-300" />
                Maintenance Throughput
              </h3>
              <p className="text-sm text-slate-300">Scheduled vs completed windows this week</p>
            </div>
            <div className="flex gap-2 text-xs">
              <button className="px-3 py-1 rounded-full border border-white/20 text-white">Weekly</button>
              <button className="px-3 py-1 rounded-full border border-transparent text-slate-300 hover:border-white/20">Monthly</button>
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={maintenanceStatusData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                <XAxis dataKey="day" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(15,23,42,0.9)', borderColor: 'rgba(255,255,255,0.1)' }} />
                <Legend />
                <Bar dataKey="scheduled" fill="#a5b4fc" radius={[6, 6, 0, 0]} />
                <Bar dataKey="completed" fill="#34d399" radius={[6, 6, 0, 0]} />
                <Bar dataKey="pending" fill="#fbbf24" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="glass-card transition-all duration-300 hover:shadow-2xl hover:shadow-emerald-500/10 hover:border-emerald-400/30 hover:scale-[1.01]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-300" />
                Operations Snapshot
              </h3>
              <p className="text-sm text-slate-300">AI prioritized objectives</p>
            </div>
            <button className="btn-ghost text-xs px-3 py-1.5">Automations</button>
          </div>
          <div className="space-y-4">
            <div className="glass-panel rounded-xl p-4 border border-white/10 hover:border-emerald-300/40 hover:bg-white/10 hover:scale-[1.02] transition-all duration-200 cursor-pointer">
              <p className="text-sm text-slate-300">Fleet Availability</p>
              <p className="text-3xl font-bold text-white mt-1">{fleetAvailability}%</p>
              <p className="text-xs text-emerald-300 mt-1 flex items-center gap-1">
                <ArrowUpRight className="w-4 h-4" />
                +2.4% vs last week
              </p>
            </div>
            <div className="glass-panel rounded-xl p-4 border border-white/10 hover:border-emerald-300/40 hover:bg-white/10 hover:scale-[1.02] transition-all duration-200 cursor-pointer">
              <p className="text-sm text-slate-300">Uptime Reliability</p>
              <p className="text-3xl font-bold text-white mt-1">{resolvedMetrics.uptime}%</p>
              <p className="text-xs text-slate-300 mt-1">Four 9s SLA holding steady</p>
            </div>
            <div className="glass-panel rounded-xl p-4 border border-white/10 hover:border-emerald-300/40 hover:bg-white/10 hover:scale-[1.02] transition-all duration-200 cursor-pointer">
              <p className="text-sm text-slate-300">Avg Fuel Efficiency</p>
              <p className="text-3xl font-bold text-white mt-1">{resolvedMetrics.avgFuelEfficiency} km/l</p>
              <p className="text-xs text-emerald-300 mt-1 flex items-center gap-1">
                <ArrowUpRight className="w-4 h-4" />
                Optimized via eco-routing
              </p>
            </div>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="glass-card transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-500/10 hover:border-cyan-400/30 hover:scale-[1.01]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Car className="w-5 h-5 text-cyan-300" />
              Recent Vehicle Activity
            </h3>
            <button className="btn-ghost text-xs px-3 py-1.5">View All</button>
          </div>
          <div className="space-y-3">
            {vehicleActivities.map((activity: any) => (
              <div key={activity.id} className="glass-panel rounded-xl border border-white/10 p-4 hover:border-cyan-300/40 hover:bg-white/10 hover:scale-[1.02] transition-all duration-200 cursor-pointer">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm font-semibold text-white">{activity.id}</div>
                  <span className="text-xs text-slate-300">{activity.timestamp}</span>
                </div>
                <p className="text-slate-200 text-sm flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-cyan-300" />
                  {activity.route || activity.detail}
                </p>
                <p className="text-xs text-slate-300 mt-2">{activity.detail}</p>
                <div className="mt-3 flex items-center justify-between text-xs">
                  <span className="inline-flex items-center gap-1 text-emerald-300">
                    <Fuel className="w-3 h-3" />
                    {activity.delta}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-[11px] uppercase tracking-wide ${getStatusToken(activity.status)}`}>
                    {activity.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="glass-card transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/10 hover:border-purple-400/30 hover:scale-[1.01]">
          <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-purple-300" />
            System Health
          </h3>
          <div className="space-y-3">
            {systemHealth.map((system) => (
              <div key={system.label} className="glass-panel rounded-xl border border-white/10 p-4 flex items-center justify-between hover:border-purple-300/40 hover:bg-white/10 transition-all duration-200">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                    <system.icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">{system.label}</p>
                    <p className="text-xs text-slate-300">{system.detail}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-[11px] uppercase tracking-wide ${getStatusToken(system.status)}`}>
                  {system.status}
                </span>
              </div>
            ))}
          </div>
        </div>
        <div className="glass-card transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-500/10 hover:border-cyan-400/30 hover:scale-[1.01]">
          <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
            <Users className="w-5 h-5 text-cyan-300" />
            AI Agent Pulse
          </h3>
          <div className="space-y-3 max-h-[420px] overflow-y-auto custom-scrollbar pr-1">
            {agentPulse.map((agent: any) => (
              <div key={agent.id} className="glass-panel rounded-xl border border-white/10 p-4 hover:border-cyan-300/40 hover:bg-white/10 hover:scale-[1.02] transition-all duration-200 cursor-pointer">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-white">{agent.name}</p>
                    <p className="text-xs text-slate-300">{agent.description}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-[11px] uppercase tracking-wide ${getStatusToken(agent.status)}`}>
                    {agent.status}
                  </span>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-3 text-xs text-slate-300">
                  <div>
                    <p className="text-[11px] uppercase tracking-wide">Tasks</p>
                    <p className="text-sm font-semibold text-white">{agent.tasksProcessed?.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-[11px] uppercase tracking-wide">Latency</p>
                    <p className="text-sm font-semibold text-white">{agent.avgResponseTime ?? agent.latency} ms</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
