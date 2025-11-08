import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Activity,
  CheckCircle,
  Clock,
  Zap,
  RefreshCw,
  Settings,
  BarChart3,
  TrendingUp,
  Cpu,
  Database,
  Network,
  Shield,
  Play,
  Pause,
  AlertTriangle,
  Info,
  Download,
  Search,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  TrendingDown,
  XCircle
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { apiService } from '../services/api';
import config from '../config';
import { Agent } from '../types';

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  active_connections: number;
  response_time: number;
  error_rate: number;
  throughput: number;
}

interface AgentPerformanceMetrics {
  success_rate: number;
  error_count: number;
  avg_execution_time: number;
  peak_memory_usage: number;
  circuit_breaker_state: string;
  last_error?: string;
  performance_trend: 'improving' | 'stable' | 'degrading';
}

interface RealtimeActivity {
  id: string;
  timestamp: string;
  agent_id: string;
  agent_name: string;
  action: string;
  status: 'success' | 'warning' | 'error';
  details?: string;
  execution_time?: number;
  error_message?: string;
}

interface AgentLog {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  agent_id: string;
  context?: any;
}

// Mock data for better showcase
const generateMockAgents = (): Agent[] => [
  {
    id: 'agent-001',
    name: 'Diagnostic Engine AI',
    type: 'diagnostic',
    status: 'active',
    description: 'Advanced vehicle diagnostics and fault detection',
    tasksProcessed: 1247,
    avgResponseTime: 125,
    uptime: '28h 45m',
    version: '2.3.1',
    createdAt: '2024-12-01',
    lastUpdated: '2025-11-05'
  },
  {
    id: 'agent-002',
    name: 'Predictive Maintenance AI',
    type: 'predictive',
    status: 'active',
    description: 'Predictive analytics for maintenance scheduling',
    tasksProcessed: 892,
    avgResponseTime: 189,
    uptime: '72h 15m',
    version: '1.8.5',
    createdAt: '2024-11-15',
    lastUpdated: '2025-11-06'
  },
  {
    id: 'agent-003',
    name: 'Performance Analytics AI',
    type: 'analytics',
    status: 'active',
    description: 'Real-time vehicle performance monitoring',
    tasksProcessed: 2104,
    avgResponseTime: 98,
    uptime: '156h 30m',
    version: '3.1.0',
    createdAt: '2024-10-20',
    lastUpdated: '2025-11-07'
  },
  {
    id: 'agent-004',
    name: 'Fleet Monitoring AI',
    type: 'monitoring',
    status: 'active',
    description: 'Comprehensive fleet health monitoring',
    tasksProcessed: 1567,
    avgResponseTime: 142,
    uptime: '98h 20m',
    version: '2.0.3',
    createdAt: '2024-11-10',
    lastUpdated: '2025-11-06'
  },
  {
    id: 'agent-005',
    name: 'Customer Service AI',
    type: 'support',
    status: 'idle',
    description: 'Automated customer support and query handling',
    tasksProcessed: 645,
    avgResponseTime: 215,
    uptime: '12h 10m',
    version: '1.5.2',
    createdAt: '2024-12-01',
    lastUpdated: '2025-11-07'
  },
  {
    id: 'agent-006',
    name: 'Quality Control AI',
    type: 'diagnostic',
    status: 'error',
    description: 'Manufacturing quality assurance checks',
    tasksProcessed: 423,
    avgResponseTime: 267,
    uptime: '4h 35m',
    version: '1.2.8',
    createdAt: '2024-11-25',
    lastUpdated: '2025-11-07'
  }
];

const generateMockSystemMetrics = (): SystemMetrics => ({
  cpu_usage: 42.5 + Math.random() * 20,
  memory_usage: 56.8 + Math.random() * 15,
  active_connections: 127 + Math.floor(Math.random() * 20),
  response_time: 145 + Math.random() * 50,
  error_rate: 1.2 + Math.random() * 1.5,
  throughput: 850 + Math.floor(Math.random() * 200)
});

const generateMockAgentMetrics = (): Record<string, AgentPerformanceMetrics> => ({
  'agent-001': {
    success_rate: 98.5,
    error_count: 12,
    avg_execution_time: 125,
    peak_memory_usage: 245,
    circuit_breaker_state: 'closed',
    performance_trend: 'improving'
  },
  'agent-002': {
    success_rate: 96.8,
    error_count: 28,
    avg_execution_time: 189,
    peak_memory_usage: 312,
    circuit_breaker_state: 'closed',
    performance_trend: 'stable'
  },
  'agent-003': {
    success_rate: 99.2,
    error_count: 5,
    avg_execution_time: 98,
    peak_memory_usage: 198,
    circuit_breaker_state: 'closed',
    performance_trend: 'improving'
  },
  'agent-004': {
    success_rate: 97.5,
    error_count: 18,
    avg_execution_time: 142,
    peak_memory_usage: 267,
    circuit_breaker_state: 'closed',
    performance_trend: 'stable'
  },
  'agent-005': {
    success_rate: 94.2,
    error_count: 45,
    avg_execution_time: 215,
    peak_memory_usage: 389,
    circuit_breaker_state: 'half-open',
    performance_trend: 'degrading',
    last_error: 'Connection timeout after 30s'
  },
  'agent-006': {
    success_rate: 87.3,
    error_count: 78,
    avg_execution_time: 267,
    peak_memory_usage: 423,
    circuit_breaker_state: 'open',
    performance_trend: 'degrading',
    last_error: 'Database connection lost'
  }
});

const generateMockActivities = (): RealtimeActivity[] => {
  const actions = [
    'Analyzed vehicle diagnostics',
    'Predicted maintenance required',
    'Processed sensor data',
    'Generated performance report',
    'Detected anomaly in engine',
    'Updated fleet status',
    'Completed health check',
    'Responded to customer query'
  ];

  const agentNames = [
    'Diagnostic Engine AI',
    'Predictive Maintenance AI',
    'Performance Analytics AI',
    'Fleet Monitoring AI'
  ];

  return Array.from({ length: 25 }, (_, i) => ({
    id: `activity-${i}`,
    timestamp: new Date(Date.now() - i * 120000).toISOString(),
    agent_id: `agent-${String(Math.floor(Math.random() * 4) + 1).padStart(3, '0')}`,
    agent_name: agentNames[Math.floor(Math.random() * agentNames.length)],
    action: actions[Math.floor(Math.random() * actions.length)],
    status: Math.random() > 0.15 ? 'success' : (Math.random() > 0.5 ? 'warning' : 'error'),
    execution_time: Math.floor(80 + Math.random() * 200),
    details: Math.random() > 0.6 ? `Processed ${Math.floor(Math.random() * 50)} items` : undefined
  }));
};

const generateMockLogs = (): AgentLog[] => {
  const messages = [
    'Agent initialized successfully',
    'Processing task queue',
    'Connection to database established',
    'Task completed successfully',
    'Warning: High memory usage detected',
    'Error: Connection timeout',
    'Performing health check',
    'Cache cleared successfully',
    'Configuration updated'
  ];

  return Array.from({ length: 50 }, (_, i) => ({
    id: `log-${i}`,
    timestamp: new Date(Date.now() - i * 60000).toISOString(),
    level: (['info', 'info', 'info', 'warning', 'error'] as const)[Math.floor(Math.random() * 5)],
    message: messages[Math.floor(Math.random() * messages.length)],
    agent_id: `agent-${String(Math.floor(Math.random() * 6) + 1).padStart(3, '0')}`,
    context: { task_id: `task-${i}`, duration: Math.floor(Math.random() * 500) }
  }));
};

// Generate historical data for charts
const generateHistoricalData = () => {
  const hours = 24;
  return Array.from({ length: hours }, (_, i) => ({
    time: `${23 - i}h`,
    cpu: 30 + Math.random() * 40,
    memory: 40 + Math.random() * 30,
    throughput: 600 + Math.random() * 400,
    errors: Math.floor(Math.random() * 10)
  })).reverse();
};

const generateAgentPerformanceHistory = () => {
  return Array.from({ length: 12 }, (_, i) => ({
    time: `${11 - i}h`,
    diagnostic: 95 + Math.random() * 5,
    predictive: 93 + Math.random() * 5,
    analytics: 96 + Math.random() * 4,
    monitoring: 94 + Math.random() * 5
  })).reverse();
};

const AgentMonitor: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [realtimeActivities, setRealtimeActivities] = useState<RealtimeActivity[]>([]);
  const [agentLogs, setAgentLogs] = useState<AgentLog[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>(generateMockSystemMetrics());
  const [agentMetrics, setAgentMetrics] = useState<Record<string, AgentPerformanceMetrics>>({});
  const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true);
  const [showAdvancedMetrics, setShowAdvancedMetrics] = useState(false);
  const [logFilter, setLogFilter] = useState<'all' | 'info' | 'warning' | 'error'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [historicalData] = useState(generateHistoricalData());
  const [agentPerformanceHistory] = useState(generateAgentPerformanceHistory());
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    loadInitialData();

    const interval = setInterval(() => {
      if (!isRealTimeEnabled) return;
      updateMetrics();
    }, 3000);

    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [isRealTimeEnabled]);

  const loadInitialData = async () => {
    try {
      setLoading(true);

      // Try to fetch from API first, fallback to mock data
      try {
        const response = await apiService.get('/agents');
        if (response.data && response.data.length > 0) {
          setAgents(response.data);
          setSelectedAgent(response.data[0]);
        } else {
          throw new Error('No data from API');
        }
      } catch {
        // Use mock data
        const mockAgents = generateMockAgents();
        setAgents(mockAgents);
        setSelectedAgent(mockAgents[0]);
      }

      setAgentMetrics(generateMockAgentMetrics());
      setRealtimeActivities(generateMockActivities());
      setAgentLogs(generateMockLogs());

    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateMetrics = () => {
    setSystemMetrics(generateMockSystemMetrics());

    // Add new activity
    if (Math.random() > 0.7) {
      const newActivity = generateMockActivities()[0];
      setRealtimeActivities(prev => [newActivity, ...prev.slice(0, 49)]);
    }

    // Add new log
    if (Math.random() > 0.5) {
      const newLog = generateMockLogs()[0];
      setAgentLogs(prev => [newLog, ...prev.slice(0, 99)]);
    }
  };

  const toggleRealTime = () => {
    setIsRealTimeEnabled(!isRealTimeEnabled);
  };

  const exportLogs = () => {
    const filteredLogs = agentLogs.filter(log =>
      logFilter === 'all' || log.level === logFilter
    );

    const csvContent = [
      'Timestamp,Level,Agent,Message,Context',
      ...filteredLogs.map(log =>
        `"${log.timestamp}","${log.level}","${log.agent_id || 'Unknown'}","${log.message}","${JSON.stringify(log.context || {})}"`
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agent-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const restartAgent = async (agentId: string) => {
    try {
      await apiService.post(`/agents/${agentId}/restart`);
      loadInitialData();
    } catch (error) {
      console.error('Failed to restart agent:', error);
    }
  };

  const pauseAgent = async (agentId: string) => {
    try {
      await apiService.post(`/agents/${agentId}/pause`);
      loadInitialData();
    } catch (error) {
      console.error('Failed to pause agent:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'running':
        return 'text-green-700 bg-green-100 border-green-200';
      case 'idle':
        return 'text-yellow-700 bg-yellow-100 border-yellow-200';
      case 'error':
      case 'failed':
        return 'text-red-700 bg-red-100 border-red-200';
      case 'paused':
        return 'text-slate-200 bg-white/10 border-white/10';
      default:
        return 'text-slate-200 bg-white/10 border-white/10';
    }
  };

  const getAgentIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'diagnostic':
        return Shield;
      case 'predictive':
        return TrendingUp;
      case 'analytics':
        return BarChart3;
      case 'monitoring':
        return Activity;
      case 'support':
        return Bot;
      default:
        return Bot;
    }
  };

  const getAgentColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'diagnostic':
        return 'from-blue-500 to-blue-600';
      case 'predictive':
        return 'from-green-500 to-green-600';
      case 'analytics':
        return 'from-purple-500 to-purple-600';
      case 'monitoring':
        return 'from-orange-500 to-orange-600';
      case 'support':
        return 'from-pink-500 to-pink-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const getPerformanceTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'degrading':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      default:
        return <Activity className="w-4 h-4 text-slate-300" />;
    }
  };

  const filteredLogs = agentLogs.filter(log => {
    const matchesFilter = logFilter === 'all' || log.level === logFilter;
    const matchesSearch = searchTerm === '' ||
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.agent_id && log.agent_id.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesFilter && matchesSearch;
  });

  const agentStatusDistribution = [
    { name: 'Active', value: agents.filter(a => a.status === 'active').length, color: '#10b981' },
    { name: 'Idle', value: agents.filter(a => a.status === 'idle').length, color: '#f59e0b' },
    { name: 'Error', value: agents.filter(a => a.status === 'error').length, color: '#ef4444' }
  ].filter(item => item.value > 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-400 mx-auto mb-4"></div>
          <p className="text-white text-lg font-medium">Loading Agent Monitor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white p-6">
      {/* Enhanced Header */}
      <div className="bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8 mb-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent mb-3">
              AI Agent Control Center
            </h1>
            <p className="text-xl text-blue-200 font-medium">Real-time monitoring, analytics, and orchestration</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowAdvancedMetrics(!showAdvancedMetrics)}
              className={`flex items-center px-5 py-3 rounded-xl text-sm font-bold transition-all duration-300 shadow-lg ${
                showAdvancedMetrics
                  ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white hover:shadow-purple-500/50'
                  : 'bg-white/10 text-white hover:bg-white/20 border border-white/30'
              }`}
            >
              {showAdvancedMetrics ? <EyeOff className="w-4 h-4 mr-2" /> : <Eye className="w-4 h-4 mr-2" />}
              Advanced
            </button>
            <button
              onClick={exportLogs}
              className="flex items-center px-5 py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-blue-500 to-cyan-500 text-white hover:shadow-lg hover:shadow-blue-500/50 transition-all duration-300"
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
            <button
              onClick={toggleRealTime}
              className={`flex items-center px-5 py-3 rounded-xl text-sm font-bold transition-all duration-300 shadow-lg ${
                isRealTimeEnabled
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:shadow-green-500/50'
                  : 'bg-white/10 text-white hover:bg-white/20 border border-white/30'
              }`}
            >
              {isRealTimeEnabled ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
              {isRealTimeEnabled ? 'Pause' : 'Resume'}
            </button>
            <button
              onClick={loadInitialData}
              className="flex items-center px-5 py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:shadow-lg hover:shadow-indigo-500/50 transition-all duration-300"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>

        {/* Live Status Indicator */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3 bg-white/5 rounded-xl px-4 py-2 border border-white/20">
            <div className={`w-3 h-3 rounded-full ${isRealTimeEnabled ? 'bg-green-400 animate-pulse shadow-lg shadow-green-400/50' : 'bg-gray-400'}`}></div>
            <span className="text-sm font-semibold text-blue-200">
              {isRealTimeEnabled ? 'Live Monitoring Active' : 'Monitoring Paused'}
            </span>
          </div>
          <div className="text-sm font-medium text-blue-300">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* System Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-6">
        <MetricCard
          icon={Cpu}
          label="CPU Usage"
          value={`${Math.round(systemMetrics.cpu_usage)}%`}
          progress={systemMetrics.cpu_usage}
          color="blue"
        />
        <MetricCard
          icon={Database}
          label="Memory"
          value={`${Math.round(systemMetrics.memory_usage)}%`}
          progress={systemMetrics.memory_usage}
          color="purple"
        />
        <MetricCard
          icon={Network}
          label="Connections"
          value={systemMetrics.active_connections}
          color="green"
        />
        <MetricCard
          icon={Clock}
          label="Response Time"
          value={`${Math.round(systemMetrics.response_time)}ms`}
          color="orange"
        />
        <MetricCard
          icon={AlertTriangle}
          label="Error Rate"
          value={`${systemMetrics.error_rate.toFixed(1)}%`}
          color="red"
        />
        <MetricCard
          icon={Zap}
          label="Throughput"
          value={systemMetrics.throughput}
          subtitle="req/min"
          color="indigo"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* System Performance Chart */}
        <div className="lg:col-span-2 bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 p-6">
          <h3 className="text-2xl font-bold text-white mb-4">System Performance (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={historicalData}>
              <defs>
                <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
              <XAxis dataKey="time" stroke="#ffffff80" />
              <YAxis stroke="#ffffff80" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Legend />
              <Area type="monotone" dataKey="cpu" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCpu)" name="CPU %" />
              <Area type="monotone" dataKey="memory" stroke="#a855f7" fillOpacity={1} fill="url(#colorMemory)" name="Memory %" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Agent Status Distribution */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 p-6">
          <h3 className="text-2xl font-bold text-white mb-4">Agent Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={agentStatusDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {agentStatusDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Agent Performance History */}
      {showAdvancedMetrics && (
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 p-6 mb-6">
          <h3 className="text-2xl font-bold text-white mb-4">Agent Success Rate Trends (12h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={agentPerformanceHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
              <XAxis dataKey="time" stroke="#ffffff80" />
              <YAxis domain={[90, 100]} stroke="#ffffff80" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="diagnostic" stroke="#3b82f6" strokeWidth={2} name="Diagnostic AI" />
              <Line type="monotone" dataKey="predictive" stroke="#10b981" strokeWidth={2} name="Predictive AI" />
              <Line type="monotone" dataKey="analytics" stroke="#a855f7" strokeWidth={2} name="Analytics AI" />
              <Line type="monotone" dataKey="monitoring" stroke="#f59e0b" strokeWidth={2} name="Monitoring AI" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Agent Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <SummaryCard
          icon={Bot}
          label="Total Agents"
          value={agents.length}
          color="blue"
        />
        <SummaryCard
          icon={CheckCircle}
          label="Active Agents"
          value={agents.filter(a => a.status === 'active').length}
          color="green"
        />
        <SummaryCard
          icon={Zap}
          label="Tasks Processed"
          value={agents.reduce((sum, agent) => sum + (agent.tasksProcessed || 0), 0)}
          color="yellow"
        />
        <SummaryCard
          icon={Clock}
          label="Avg Response"
          value={`${agents.length > 0 ? Math.round(agents.reduce((sum, agent) => sum + (agent.avgResponseTime || 0), 0) / agents.length) : 0}ms`}
          color="indigo"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Agent List */}
        <div className="lg:col-span-1">
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 p-6">
            <h3 className="text-xl font-bold text-white mb-4">Active Agents ({agents.length})</h3>
            <div className="space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar">
              {agents.map((agent) => {
                const Icon = getAgentIcon(agent.type);
                const metrics = agentMetrics[agent.id];
                return (
                  <div
                    key={agent.id}
                    onClick={() => setSelectedAgent(agent)}
                    className={`cursor-pointer transition-all duration-300 p-4 rounded-xl border-2 ${
                      selectedAgent?.id === agent.id
                        ? 'bg-white/20 border-cyan-400 shadow-lg shadow-cyan-400/30'
                        : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/30'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        <div className={`w-10 h-10 bg-gradient-to-br ${getAgentColor(agent.type)} rounded-lg flex items-center justify-center mr-3 shadow-lg`}>
                          <Icon className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h4 className="font-bold text-white text-sm">{agent.name}</h4>
                          <p className="text-xs text-blue-300">{agent.type}</p>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className={`inline-flex items-center px-2 py-1 rounded-lg text-xs font-bold border ${getStatusColor(agent.status)}`}>
                        {agent.status.toUpperCase()}
                      </span>
                      {metrics && (
                        <div className="flex items-center space-x-1">
                          {getPerformanceTrendIcon(metrics.performance_trend)}
                          <span className="text-xs text-blue-300 font-semibold">{metrics.success_rate.toFixed(0)}%</span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Agent Details */}
        <div className="lg:col-span-2">
          {selectedAgent ? (
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <div className={`w-14 h-14 bg-gradient-to-br ${getAgentColor(selectedAgent.type)} rounded-xl flex items-center justify-center mr-4 shadow-lg`}>
                    {React.createElement(getAgentIcon(selectedAgent.type), { className: "w-7 h-7 text-white" })}
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">{selectedAgent.name}</h3>
                    <p className="text-blue-300">{selectedAgent.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => restartAgent(selectedAgent.id)}
                    className="p-3 text-blue-400 hover:text-blue-300 rounded-xl hover:bg-white/10 transition-all"
                    title="Restart Agent"
                  >
                    <RefreshCw className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => pauseAgent(selectedAgent.id)}
                    className="p-3 text-blue-400 hover:text-blue-300 rounded-xl hover:bg-white/10 transition-all"
                    title="Pause/Resume Agent"
                  >
                    {selectedAgent.status === 'active' ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  </button>
                  <button className="p-3 text-blue-400 hover:text-blue-300 rounded-xl hover:bg-white/10 transition-all">
                    <Settings className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Agent Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 border border-blue-400/30 rounded-xl p-4">
                  <div className="text-xs text-blue-300 mb-1">Tasks Processed</div>
                  <div className="text-2xl font-bold text-white">{selectedAgent.tasksProcessed || 0}</div>
                </div>
                <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 border border-green-400/30 rounded-xl p-4">
                  <div className="text-xs text-green-300 mb-1">Avg Response</div>
                  <div className="text-2xl font-bold text-white">{selectedAgent.avgResponseTime || 0}ms</div>
                </div>
                <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 border border-purple-400/30 rounded-xl p-4">
                  <div className="text-xs text-purple-300 mb-1">Uptime</div>
                  <div className="text-2xl font-bold text-white">{selectedAgent.uptime || '0h'}</div>
                </div>
              </div>

              {/* Performance Metrics */}
              {agentMetrics[selectedAgent.id] && (
                <div className="mb-6">
                  <h4 className="font-bold text-white mb-3 text-lg">Performance Metrics</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-green-500/20 border border-green-400/30 rounded-xl p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-green-300">Success Rate</span>
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      </div>
                      <div className="text-3xl font-bold text-white mt-2">{agentMetrics[selectedAgent.id].success_rate.toFixed(1)}%</div>
                      <div className="w-full bg-green-900/30 rounded-full h-2 mt-2">
                        <div
                          className="bg-green-400 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${agentMetrics[selectedAgent.id].success_rate}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="bg-red-500/20 border border-red-400/30 rounded-xl p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-red-300">Error Count</span>
                        <XCircle className="w-5 h-5 text-red-400" />
                      </div>
                      <div className="text-3xl font-bold text-white mt-2">{agentMetrics[selectedAgent.id].error_count}</div>
                    </div>
                    <div className="bg-blue-500/20 border border-blue-400/30 rounded-xl p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-blue-300">Avg Execution</span>
                        <Clock className="w-5 h-5 text-blue-400" />
                      </div>
                      <div className="text-3xl font-bold text-white mt-2">{agentMetrics[selectedAgent.id].avg_execution_time}ms</div>
                    </div>
                    <div className="bg-purple-500/20 border border-purple-400/30 rounded-xl p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-purple-300">Peak Memory</span>
                        <Database className="w-5 h-5 text-purple-400" />
                      </div>
                      <div className="text-3xl font-bold text-white mt-2">{agentMetrics[selectedAgent.id].peak_memory_usage}MB</div>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center justify-between bg-white/5 rounded-xl p-4">
                    <div>
                      <span className="text-sm text-blue-300">Circuit Breaker State</span>
                      <div className="flex items-center mt-1">
                        <span className={`inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold ${
                          agentMetrics[selectedAgent.id].circuit_breaker_state === 'closed' ? 'bg-green-500/20 text-green-400 border border-green-400/30' :
                          agentMetrics[selectedAgent.id].circuit_breaker_state === 'open' ? 'bg-red-500/20 text-red-400 border border-red-400/30' :
                          'bg-yellow-500/20 text-yellow-400 border border-yellow-400/30'
                        }`}>
                          {agentMetrics[selectedAgent.id].circuit_breaker_state.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    {agentMetrics[selectedAgent.id].last_error && (
                      <div className="text-right">
                        <span className="text-xs text-red-300">Last Error</span>
                        <p className="text-xs text-red-400 mt-1 max-w-xs truncate" title={agentMetrics[selectedAgent.id].last_error}>
                          {agentMetrics[selectedAgent.id].last_error}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Recent Activity */}
              <div>
                <h4 className="font-bold text-white mb-3 text-lg">Recent Activity</h4>
                <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                  {realtimeActivities
                    .filter(activity => activity.agent_id === selectedAgent.id)
                    .slice(0, 8)
                    .map((activity, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10">
                        <div className="flex items-center">
                          <div className={`w-2 h-2 rounded-full mr-3 ${
                            activity.status === 'success' ? 'bg-green-400' :
                            activity.status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                          }`}></div>
                          <div>
                            <span className="text-sm text-white font-medium">{activity.action}</span>
                            {activity.execution_time && (
                              <span className="text-xs text-blue-300 ml-2">({activity.execution_time}ms)</span>
                            )}
                          </div>
                        </div>
                        <span className="text-xs text-blue-300">
                          {new Date(activity.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 p-12 flex items-center justify-center h-full">
              <div className="text-center">
                <Bot className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Select an Agent</h3>
                <p className="text-blue-300">Choose an agent from the list to view detailed information</p>
              </div>
            </div>
          )}
        </div>

        {/* Activity Feed and Logs */}
        <div className="lg:col-span-1">
          <div className="space-y-4">
            {/* Live Activity */}
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">Live Activity</h3>
                <div className={`w-2 h-2 rounded-full ${isRealTimeEnabled ? 'bg-green-400 animate-pulse shadow-lg shadow-green-400/50' : 'bg-gray-400'}`}></div>
              </div>

              <div className="space-y-2 max-h-80 overflow-y-auto custom-scrollbar">
                {realtimeActivities.slice(0, 15).map((activity) => (
                  <div key={activity.id} className="p-3 bg-white/5 rounded-lg border border-white/10">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start flex-1">
                        <div className={`w-2 h-2 rounded-full mt-2 mr-2 ${
                          activity.status === 'success' ? 'bg-green-400' :
                          activity.status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                        }`}></div>
                        <div className="flex-1">
                          <p className="text-xs text-white font-medium">{activity.action}</p>
                          <p className="text-xs text-blue-300 mt-1">{activity.agent_name}</p>
                        </div>
                      </div>
                      <span className="text-xs text-blue-400">
                        {new Date(activity.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Logs */}
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">System Logs</h3>
                <select
                  value={logFilter}
                  onChange={(e) => setLogFilter(e.target.value as any)}
                  className="text-xs bg-white/10 border border-white/20 rounded-lg px-3 py-1 text-white"
                >
                  <option value="all" className="bg-slate-800">All</option>
                  <option value="info" className="bg-slate-800">Info</option>
                  <option value="warning" className="bg-slate-800">Warning</option>
                  <option value="error" className="bg-slate-800">Error</option>
                </select>
              </div>

              <div className="mb-3">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-blue-300" />
                  <input
                    type="text"
                    placeholder="Search logs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 text-sm bg-white/10 border border-white/20 rounded-lg text-white placeholder-blue-300/50 focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                {filteredLogs.slice(0, 20).map((log) => (
                  <div key={log.id} className="p-2 bg-white/5 rounded-lg text-xs border border-white/10">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`inline-flex items-center px-2 py-1 rounded-lg text-xs font-bold ${
                        log.level === 'error' ? 'bg-red-500/20 text-red-400 border border-red-400/30' :
                        log.level === 'warning' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-400/30' :
                        'bg-blue-500/20 text-blue-400 border border-blue-400/30'
                      }`}>
                        {log.level.toUpperCase()}
                      </span>
                      <span className="text-blue-400">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-white mb-1">{log.message}</p>
                    <p className="text-blue-300">Agent: {log.agent_id || 'Unknown'}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(59, 130, 246, 0.5);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(59, 130, 246, 0.7);
        }
      `}</style>
    </div>
  );
};

// Reusable MetricCard Component
const MetricCard: React.FC<{
  icon: any;
  label: string;
  value: string | number;
  subtitle?: string;
  progress?: number;
  color: string;
}> = ({ icon: Icon, label, value, subtitle, progress, color }) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    green: 'from-green-500 to-green-600',
    orange: 'from-orange-500 to-orange-600',
    red: 'from-red-500 to-red-600',
    indigo: 'from-indigo-500 to-indigo-600',
    yellow: 'from-yellow-500 to-yellow-600'
  };

  return (
    <div className="bg-white/10 backdrop-blur-xl rounded-xl shadow-xl border border-white/20 p-5 hover:scale-105 transition-all duration-300">
      <div className="flex items-center justify-between mb-3">
        <div className="flex-1">
          <p className="text-xs font-semibold text-blue-300 mb-1">{label}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-xs text-blue-400 font-medium mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 bg-gradient-to-br ${colorClasses[color as keyof typeof colorClasses]} rounded-xl shadow-lg`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
      {progress !== undefined && (
        <div className="w-full bg-white/10 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-500 bg-gradient-to-r ${colorClasses[color as keyof typeof colorClasses]}`}
            style={{ width: `${Math.min(progress, 100)}%` }}
          ></div>
        </div>
      )}
    </div>
  );
};

// Reusable SummaryCard Component
const SummaryCard: React.FC<{
  icon: any;
  label: string;
  value: string | number;
  color: string;
}> = ({ icon: Icon, label, value, color }) => {
  const colorClasses = {
    blue: 'from-blue-500/20 to-blue-600/20 border-blue-400/30',
    green: 'from-green-500/20 to-green-600/20 border-green-400/30',
    yellow: 'from-yellow-500/20 to-yellow-600/20 border-yellow-400/30',
    indigo: 'from-indigo-500/20 to-indigo-600/20 border-indigo-400/30'
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color as keyof typeof colorClasses]} border rounded-xl p-5 hover:scale-105 transition-all duration-300`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-blue-300 mb-1">{label}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
        </div>
        <Icon className="w-10 h-10 text-blue-400 opacity-80" />
      </div>
    </div>
  );
};

export default AgentMonitor;
