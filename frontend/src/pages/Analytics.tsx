import React, { useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  Car, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Zap, 
  Gauge, 
  Filter, 
  Download, 
  RefreshCw, 
  PieChart, 
  LineChart, 
  Target, 
  Fuel,
  MapPin,
  Settings,
  Calendar,
  Users,
  Shield,
  Cpu
} from 'lucide-react';
import {
  LineChart as RechartsLineChart,
  AreaChart,
  BarChart as RechartsBarChart,
  PieChart as RechartsPieChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  Bar,
  Line,
  Cell,
  Pie,
  RadialBarChart,
  RadialBar
} from 'recharts';
import { darkChartTheme } from '../config/theme';

// Sample data for charts
const performanceData = [
  { name: 'Mon', vehicles: 240, alerts: 12, maintenance: 8, efficiency: 95 },
  { name: 'Tue', vehicles: 245, alerts: 15, maintenance: 6, efficiency: 92 },
  { name: 'Wed', vehicles: 238, alerts: 8, maintenance: 12, efficiency: 97 },
  { name: 'Thu', vehicles: 252, alerts: 18, maintenance: 4, efficiency: 89 },
  { name: 'Fri', vehicles: 247, alerts: 10, maintenance: 9, efficiency: 94 },
  { name: 'Sat', vehicles: 235, alerts: 6, maintenance: 15, efficiency: 98 },
  { name: 'Sun', vehicles: 228, alerts: 4, maintenance: 11, efficiency: 96 }
];

const statusDistribution = [
  { name: 'Active', value: 185, color: '#10B981' },
  { name: 'Maintenance', value: 23, color: '#F59E0B' },
  { name: 'Offline', value: 15, color: '#EF4444' },
  { name: 'Idle', value: 24, color: '#6B7280' }
];

const geographicData = [
  { region: 'North', vehicles: 85, alerts: 12, efficiency: 94 },
  { region: 'South', vehicles: 72, alerts: 8, efficiency: 96 },
  { region: 'East', vehicles: 68, alerts: 15, efficiency: 91 },
  { region: 'West', vehicles: 62, alerts: 6, efficiency: 98 },
  { region: 'Central', vehicles: 58, alerts: 9, efficiency: 93 }
];

const fuelEfficiencyData = [
  { month: 'Jan', efficiency: 28.5, cost: 4200 },
  { month: 'Feb', efficiency: 29.2, cost: 3950 },
  { month: 'Mar', efficiency: 27.8, cost: 4350 },
  { month: 'Apr', efficiency: 30.1, cost: 3800 },
  { month: 'May', efficiency: 31.2, cost: 3650 },
  { month: 'Jun', efficiency: 29.8, cost: 3900 }
];

const maintenanceData = [
  { type: 'Preventive', count: 45, percentage: 65 },
  { type: 'Corrective', count: 18, percentage: 26 },
  { type: 'Emergency', count: 6, percentage: 9 }
];

const sharedTooltipProps = {
  contentStyle: {
    backgroundColor: darkChartTheme.tooltipBg,
    border: `1px solid ${darkChartTheme.tooltipBorder}`,
    borderRadius: '16px',
    boxShadow: '0 20px 45px rgba(15, 23, 42, 0.6)',
    color: darkChartTheme.tooltipText
  },
  labelStyle: { color: darkChartTheme.tooltipText }
};

const axisTickStyle = { fill: darkChartTheme.axis, fontSize: 12 };

const Analytics: React.FC = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('all');
  const [isLoading, setIsLoading] = useState(false);

  const handleRefresh = async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  const handleExport = () => {
    // Export functionality
    const dataStr = JSON.stringify({
      performance: performanceData,
      status: statusDistribution,
      geographic: geographicData,
      fuelEfficiency: fuelEfficiencyData,
      maintenance: maintenanceData
    }, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analytics-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white flex items-center">
            <BarChart3 className="w-6 h-6 sm:w-8 sm:h-8 mr-2 text-cyan-300" />
            Fleet Analytics
          </h1>
          <p className="mt-1 text-sm sm:text-base text-slate-300 flex items-center">
            <Activity className="w-4 h-4 mr-1 text-slate-400" />
            Comprehensive insights and performance metrics
          </p>
        </div>
        <div className="flex items-center space-x-3 mt-4 sm:mt-0">
          <select 
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="input-field w-40"
          >
            <option value="1d">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          <button 
            onClick={handleRefresh}
            disabled={isLoading}
            className="btn-ghost px-4 py-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
          <button 
            onClick={handleExport}
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <Download className="w-4 h-4 mr-1" />
            <span className="hidden sm:inline">Export</span>
          </button>
          <div className="flex items-center text-xs sm:text-sm text-slate-400">
            <Clock className="w-4 h-4 mr-1 text-emerald-300" />
            <span className="hidden sm:inline">Last updated: </span>
            <span className="sm:hidden">Updated: </span>
            {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="metric-card group hover:shadow-lg transition-all duration-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-300 flex items-center">
                <Car className="w-4 h-4 mr-1 text-slate-400" />
                Total Vehicles
              </p>
              <p className="text-2xl font-bold text-white">247</p>
              <p className="text-xs text-emerald-300 flex items-center mt-1">
                <TrendingUp className="w-3 h-3 mr-1" />
                +12% from last month
              </p>
            </div>
            <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-cyan-200 group-hover:border-cyan-400/40 transition-colors">
              <Car className="w-6 h-6 text-cyan-300" />
            </div>
          </div>
        </div>

        <div className="metric-card group hover:shadow-lg transition-all duration-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-300 flex items-center">
                <Activity className="w-4 h-4 mr-1 text-slate-400" />
                Active Vehicles
              </p>
              <p className="text-2xl font-bold text-white">185</p>
              <p className="text-xs text-emerald-300 flex items-center mt-1">
                <CheckCircle className="w-3 h-3 mr-1" />
                75% operational
              </p>
            </div>
            <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-emerald-200 group-hover:border-emerald-400/40 transition-colors">
              <Activity className="w-6 h-6 text-emerald-300" />
            </div>
          </div>
        </div>

        <div className="metric-card group hover:shadow-lg transition-all duration-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-300 flex items-center">
                <Gauge className="w-4 h-4 mr-1 text-slate-400" />
                Avg Efficiency
              </p>
              <p className="text-2xl font-bold text-white">94.2%</p>
              <p className="text-xs text-cyan-300 flex items-center mt-1">
                <TrendingUp className="w-3 h-3 mr-1" />
                +3.2% improvement
              </p>
            </div>
            <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-blue-200 group-hover:border-cyan-400/40 transition-colors">
              <Gauge className="w-6 h-6 text-cyan-300" />
            </div>
          </div>
        </div>

        <div className="metric-card group hover:shadow-lg transition-all duration-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-300 flex items-center">
                <AlertTriangle className="w-4 h-4 mr-1 text-slate-400" />
                Active Alerts
              </p>
              <p className="text-2xl font-bold text-white">23</p>
              <p className="text-xs text-rose-300 flex items-center mt-1">
                <Zap className="w-3 h-3 mr-1" />
                5 critical issues
              </p>
            </div>
            <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-rose-200 group-hover:border-rose-400/40 transition-colors">
              <AlertTriangle className="w-6 h-6 text-rose-300" />
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fleet Performance Trends */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <LineChart className="w-5 h-5 mr-2 text-cyan-300" />
              Fleet Performance Trends
            </h3>
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select 
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value)}
                className="input-field w-40"
              >
                <option value="all">All Metrics</option>
                <option value="vehicles">Vehicles Only</option>
                <option value="alerts">Alerts Only</option>
                <option value="efficiency">Efficiency Only</option>
              </select>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke={darkChartTheme.grid} />
                <XAxis 
                  dataKey="name" 
                  stroke={darkChartTheme.axis}
                  tick={axisTickStyle}
                />
                <YAxis 
                  stroke={darkChartTheme.axis}
                  tick={axisTickStyle}
                />
                <Tooltip {...sharedTooltipProps} />
                <Legend wrapperStyle={{ color: darkChartTheme.legendText }} />
                {(selectedMetric === 'all' || selectedMetric === 'vehicles') && (
                  <Area
                    type="monotone"
                    dataKey="vehicles"
                    stackId="1"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.6}
                    name="Active Vehicles"
                  />
                )}
                {(selectedMetric === 'all' || selectedMetric === 'alerts') && (
                  <Area
                    type="monotone"
                    dataKey="alerts"
                    stackId="2"
                    stroke="#ef4444"
                    fill="#ef4444"
                    fillOpacity={0.6}
                    name="Alerts"
                  />
                )}
                {(selectedMetric === 'all' || selectedMetric === 'efficiency') && (
                  <Line
                    type="monotone"
                    dataKey="efficiency"
                    stroke="#10b981"
                    strokeWidth={3}
                    dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                    name="Efficiency %"
                  />
                )}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Vehicle Status Distribution */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white flex items-center">
          <PieChart className="w-5 h-5 mr-2 text-emerald-300" />
              Vehicle Status Distribution
            </h3>
            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4 text-slate-400" />
              <span className="text-sm text-slate-300">Real-time</span>
            </div>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={statusDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip {...sharedTooltipProps} />
                <Legend wrapperStyle={{ color: darkChartTheme.legendText }} />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Additional Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Geographic Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center">
            <MapPin className="w-5 h-5 mr-2 text-cyan-300" />
            Geographic Distribution
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsBarChart data={geographicData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" stroke={darkChartTheme.grid} />
                <XAxis type="number" stroke={darkChartTheme.axis} tick={axisTickStyle} />
                <YAxis 
                  type="category" 
                  dataKey="region" 
                  stroke={darkChartTheme.axis} 
                  tick={axisTickStyle}
                  width={60}
                />
                <Tooltip {...sharedTooltipProps} />
                <Bar dataKey="vehicles" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </RechartsBarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fuel Efficiency Trends */}
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center">
            <Fuel className="w-5 h-5 mr-2 text-emerald-300" />
            Fuel Efficiency
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsLineChart data={fuelEfficiencyData}>
                <CartesianGrid strokeDasharray="3 3" stroke={darkChartTheme.grid} />
                <XAxis 
                  dataKey="month" 
                  stroke={darkChartTheme.axis}
                  tick={axisTickStyle}
                />
                <YAxis 
                  stroke={darkChartTheme.axis}
                  tick={axisTickStyle}
                />
                <Tooltip {...sharedTooltipProps} />
                <Line
                  type="monotone"
                  dataKey="efficiency"
                  stroke="#10b981"
                  strokeWidth={3}
                  dot={{ fill: '#10b981', strokeWidth: 2, r: 5 }}
                  name="MPG"
                />
              </RechartsLineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Maintenance Analytics */}
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center">
            <Settings className="w-5 h-5 mr-2 text-amber-300" />
            Maintenance Breakdown
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart 
                cx="50%" 
                cy="50%" 
                innerRadius="20%" 
                outerRadius="80%" 
                data={maintenanceData}
              >
                <RadialBar
                  dataKey="percentage"
                  cornerRadius={10}
                  fill="#8884d8"
                />
                <Tooltip {...sharedTooltipProps} />
                <Legend wrapperStyle={{ color: darkChartTheme.legendText }} />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* System Health Status */}
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-6 flex items-center">
          <Shield className="w-5 h-5 mr-2 text-purple-300" />
          System Health Status
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass-panel rounded-xl p-4 border border-white/10 flex items-center justify-between">
            <span className="text-sm text-slate-300 flex items-center">
              <Cpu className="w-4 h-4 mr-2 text-emerald-300" />
              API Server
            </span>
            <span className="text-sm font-medium text-emerald-300">Online</span>
          </div>
          <div className="glass-panel rounded-xl p-4 border border-white/10 flex items-center justify-between">
            <span className="text-sm text-slate-300 flex items-center">
              <CheckCircle className="w-4 h-4 mr-2 text-emerald-300" />
              Database
            </span>
            <span className="text-sm font-medium text-emerald-300">Online</span>
          </div>
          <div className="glass-panel rounded-xl p-4 border border-white/10 flex items-center justify-between">
            <span className="text-sm text-slate-300 flex items-center">
              <AlertTriangle className="w-4 h-4 mr-2 text-amber-300" />
              Cache
            </span>
            <span className="text-sm font-medium text-amber-300">Warning</span>
          </div>
          <div className="glass-panel rounded-xl p-4 border border-white/10 flex items-center justify-between">
            <span className="text-sm text-slate-300 flex items-center">
              <Activity className="w-4 h-4 mr-2 text-cyan-300" />
              AI Agents
            </span>
            <span className="text-sm font-medium text-cyan-300">Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
