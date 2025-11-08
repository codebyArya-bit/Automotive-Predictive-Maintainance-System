import React, { useState, useEffect } from 'react';
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadialBarChart, RadialBar, ComposedChart
} from 'recharts';
import {
  Activity, AlertTriangle, CheckCircle, Clock, TrendingUp, TrendingDown,
  Car, Users, MapPin, Zap, Shield, Gauge, Target, Award, Battery,
  Thermometer, Droplets, Settings, RefreshCw, Download, Maximize2,
  Play, Pause, SkipForward, Calendar, Filter
} from 'lucide-react';

interface DemoMetrics {
  totalVehicles: number;
  activeVehicles: number;
  criticalAlerts: number;
  maintenanceScheduled: number;
  avgResponseTime: number;
  systemEfficiency: number;
  customerSatisfaction: number;
  costSavings: number;
}

interface ScenarioResult {
  id: string;
  name: string;
  status: 'completed' | 'in_progress' | 'failed';
  responseTime: number;
  accuracy: number;
  customerSatisfaction: number;
  costImpact: number;
}

const DemoAnalytics: React.FC = () => {
  const [metrics, setMetrics] = useState<DemoMetrics>({
    totalVehicles: 1247,
    activeVehicles: 1189,
    criticalAlerts: 3,
    maintenanceScheduled: 47,
    avgResponseTime: 2.3,
    systemEfficiency: 97.8,
    customerSatisfaction: 9.2,
    costSavings: 284500
  });

  const [scenarioResults, setScenarioResults] = useState<ScenarioResult[]>([
    {
      id: '1',
      name: 'Critical Engine Failure',
      status: 'completed',
      responseTime: 1.8,
      accuracy: 98.5,
      customerSatisfaction: 9.7,
      costImpact: -3500
    },
    {
      id: '2',
      name: 'Brake Maintenance Warning',
      status: 'completed',
      responseTime: 2.1,
      accuracy: 96.2,
      customerSatisfaction: 9.4,
      costImpact: -850
    },
    {
      id: '3',
      name: 'Routine Maintenance',
      status: 'completed',
      responseTime: 1.9,
      accuracy: 94.8,
      customerSatisfaction: 8.9,
      costImpact: 85
    },
    {
      id: '4',
      name: 'Healthy Vehicle Monitoring',
      status: 'completed',
      responseTime: 0.8,
      accuracy: 99.1,
      customerSatisfaction: 9.8,
      costImpact: 420
    },
    {
      id: '5',
      name: 'Winter Weather Emergency',
      status: 'in_progress',
      responseTime: 1.2,
      accuracy: 97.3,
      customerSatisfaction: 9.6,
      costImpact: -2800
    },
    {
      id: '6',
      name: 'Electric Vehicle Optimization',
      status: 'completed',
      responseTime: 2.4,
      accuracy: 95.7,
      customerSatisfaction: 9.1,
      costImpact: 340
    }
  ]);

  const [isLiveMode, setIsLiveMode] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Real-time performance data
  const performanceData = [
    { time: '00:00', responseTime: 2.1, accuracy: 96.5, efficiency: 94.2 },
    { time: '00:05', responseTime: 1.9, accuracy: 97.1, efficiency: 95.8 },
    { time: '00:10', responseTime: 2.3, accuracy: 95.8, efficiency: 93.4 },
    { time: '00:15', responseTime: 1.7, accuracy: 98.2, efficiency: 97.1 },
    { time: '00:20', responseTime: 2.0, accuracy: 96.9, efficiency: 95.6 },
    { time: '00:25', responseTime: 1.8, accuracy: 97.8, efficiency: 96.9 }
  ];

  // AI Agent performance breakdown
  const agentPerformance = [
    { name: 'Diagnostic Agent', accuracy: 98.5, responseTime: 1.2, utilization: 87 },
    { name: 'Predictive Agent', accuracy: 96.8, responseTime: 2.1, utilization: 92 },
    { name: 'Customer Agent', accuracy: 94.2, responseTime: 0.8, utilization: 78 },
    { name: 'Scheduling Agent', accuracy: 97.1, responseTime: 1.5, utilization: 85 },
    { name: 'Emergency Agent', accuracy: 99.2, responseTime: 0.6, utilization: 45 },
    { name: 'Optimization Agent', accuracy: 95.7, responseTime: 2.8, utilization: 91 }
  ];

  // Vehicle health distribution
  const vehicleHealthData = [
    { name: 'Excellent', value: 756, color: '#10B981' },
    { name: 'Good', value: 312, color: '#3B82F6' },
    { name: 'Fair', value: 134, color: '#F59E0B' },
    { name: 'Poor', value: 31, color: '#EF4444' },
    { name: 'Critical', value: 14, color: '#DC2626' }
  ];

  // Cost impact analysis
  const costImpactData = [
    { category: 'Preventive Maintenance', savings: 125000, color: '#10B981' },
    { category: 'Emergency Response', savings: 89000, color: '#3B82F6' },
    { category: 'Fuel Optimization', savings: 45000, color: '#8B5CF6' },
    { category: 'Route Efficiency', savings: 25500, color: '#F59E0B' }
  ];

  // Predictive insights
  const predictiveInsights = [
    { metric: 'Maintenance Predictions', current: 94.2, target: 96.0, trend: 'up' },
    { metric: 'Failure Prevention', current: 87.8, target: 90.0, trend: 'up' },
    { metric: 'Cost Optimization', current: 92.1, target: 95.0, trend: 'up' },
    { metric: 'Customer Satisfaction', current: 96.4, target: 97.0, trend: 'stable' }
  ];

  useEffect(() => {
    if (isLiveMode) {
      const interval = setInterval(() => {
        // Simulate real-time updates
        setMetrics(prev => ({
          ...prev,
          activeVehicles: prev.activeVehicles + Math.floor(Math.random() * 3) - 1,
          avgResponseTime: Math.max(0.5, prev.avgResponseTime + (Math.random() - 0.5) * 0.2),
          systemEfficiency: Math.min(100, Math.max(90, prev.systemEfficiency + (Math.random() - 0.5) * 2))
        }));
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [isLiveMode]);

  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    trend?: 'up' | 'down' | 'stable';
    color: string;
    subtitle?: string;
  }> = ({ title, value, icon, trend, color, subtitle }) => (
    <div
      className="glass-card rounded-xl shadow-lg p-6 border border-white/10 border-l-4"
      style={{ borderLeftColor: color }}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-300">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>
        <div className="flex items-center space-x-2">
          <div
            className="p-3 rounded-xl border border-white/10"
            style={{ backgroundColor: `${color}15` }}
          >
            {icon}
          </div>
          {trend && (
            <div className="flex items-center">
              {trend === 'up' && <TrendingUp className="w-4 h-4 text-emerald-300" />}
              {trend === 'down' && <TrendingDown className="w-4 h-4 text-rose-300" />}
              {trend === 'stable' && <div className="w-4 h-4 bg-slate-500 rounded-full" />}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className={`min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-slate-100 ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
      {/* Header */}
      <div className="glass-card shadow-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-white">Demo Analytics Dashboard</h1>
              <p className="text-sm text-slate-300">Real-time system performance and scenario results</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isLiveMode ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`} />
                <span className="text-sm text-slate-300">{isLiveMode ? 'Live' : 'Paused'}</span>
              </div>
              <button
                onClick={() => setIsLiveMode(!isLiveMode)}
                className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg"
              >
                {isLiveMode ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
              </button>
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg"
              >
                <Maximize2 className="w-5 h-5" />
              </button>
              <button className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg">
                <Download className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Vehicles"
            value={metrics.totalVehicles.toLocaleString()}
            icon={<Car className="w-6 h-6 text-cyan-300" />}
            color="#3B82F6"
            trend="stable"
          />
          <MetricCard
            title="Active Vehicles"
            value={metrics.activeVehicles.toLocaleString()}
            icon={<Activity className="w-6 h-6 text-emerald-300" />}
            color="#10B981"
            trend="up"
            subtitle={`${((metrics.activeVehicles / metrics.totalVehicles) * 100).toFixed(1)}% utilization`}
          />
          <MetricCard
            title="Avg Response Time"
            value={`${metrics.avgResponseTime.toFixed(1)}s`}
            icon={<Clock className="w-6 h-6 text-purple-300" />}
            color="#8B5CF6"
            trend="down"
            subtitle="Target: <2.5s"
          />
          <MetricCard
            title="System Efficiency"
            value={`${metrics.systemEfficiency.toFixed(1)}%`}
            icon={<Gauge className="w-6 h-6 text-amber-300" />}
            color="#F59E0B"
            trend="up"
            subtitle="Above target"
          />
        </div>

        {/* Scenario Results */}
        <div className="glass-card rounded-xl shadow-lg p-6 mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-white">Demo Scenario Results</h2>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-slate-300">6 scenarios completed</span>
              <CheckCircle className="w-5 h-5 text-green-500" />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 font-semibold text-slate-200">Scenario</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-200">Status</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-200">Response Time</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-200">Accuracy</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-200">Satisfaction</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-200">Cost Impact</th>
                </tr>
              </thead>
              <tbody>
                {scenarioResults.map((scenario) => (
                  <tr key={scenario.id} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-3 px-4 font-medium text-white">{scenario.name}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        scenario.status === 'completed' ? 'bg-green-100 text-green-800' :
                        scenario.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {scenario.status === 'completed' && <CheckCircle className="w-3 h-3 mr-1" />}
                        {scenario.status === 'in_progress' && <Clock className="w-3 h-3 mr-1" />}
                        {scenario.status === 'failed' && <AlertTriangle className="w-3 h-3 mr-1" />}
                        {scenario.status.charAt(0).toUpperCase() + scenario.status.slice(1)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300">{scenario.responseTime.toFixed(1)}s</td>
                    <td className="py-3 px-4 text-slate-300">{scenario.accuracy.toFixed(1)}%</td>
                    <td className="py-3 px-4 text-slate-300">{scenario.customerSatisfaction.toFixed(1)}/10</td>
                    <td className={`py-3 px-4 font-medium ${scenario.costImpact >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
                      {scenario.costImpact >= 0 ? '+' : ''}${scenario.costImpact.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Real-time Performance */}
          <div className="glass-card rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Real-time Performance</h3>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Area yAxisId="left" type="monotone" dataKey="efficiency" stackId="1" stroke="#10B981" fill="#10B981" fillOpacity={0.3} />
                <Line yAxisId="right" type="monotone" dataKey="responseTime" stroke="#EF4444" strokeWidth={2} />
                <Line yAxisId="right" type="monotone" dataKey="accuracy" stroke="#3B82F6" strokeWidth={2} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Vehicle Health Distribution */}
          <div className="glass-card rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Vehicle Health Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={vehicleHealthData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {vehicleHealthData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Agent Performance & Cost Impact */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* AI Agent Performance */}
          <div className="glass-card rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">AI Agent Performance</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={agentPerformance} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={120} />
                <Tooltip />
                <Legend />
                <Bar dataKey="accuracy" fill="#10B981" />
                <Bar dataKey="utilization" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Cost Impact Analysis */}
          <div className="glass-card rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Cost Savings by Category</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={costImpactData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Savings']} />
                <Bar dataKey="savings" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Predictive Insights */}
        <div className="glass-card rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Predictive Insights & KPIs</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {predictiveInsights.map((insight, index) => (
              <div key={index} className="text-center">
                <div className="relative w-24 h-24 mx-auto mb-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" data={[{ value: insight.current }]}>
                      <RadialBar dataKey="value" cornerRadius={10} fill="#3B82F6" />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-lg font-bold text-white">{insight.current.toFixed(1)}%</span>
                  </div>
                </div>
                <h4 className="font-semibold text-white mb-1">{insight.metric}</h4>
                <p className="text-sm text-slate-300">Target: {insight.target.toFixed(1)}%</p>
                <div className="flex items-center justify-center mt-2">
                  {insight.trend === 'up' && <TrendingUp className="w-4 h-4 text-green-500" />}
                  {insight.trend === 'down' && <TrendingDown className="w-4 h-4 text-red-500" />}
                  {insight.trend === 'stable' && <div className="w-4 h-4 bg-slate-500 rounded-full" />}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoAnalytics;
