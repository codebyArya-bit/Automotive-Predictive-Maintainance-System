import React, { useState, useEffect, useRef } from 'react';
import config from '../config';
import { logWebSocketError } from '../utils/logger';
import {
  AlertTriangle,
  CheckCircle,
  Minus,
  AlertCircle,
  Info,
  X,
  Network,
  Wifi,
  Clock,
  Server,
  Search,
  Play,
  RefreshCw,
  Cpu,
  MemoryStick,
  HardDrive,
  BarChart3,
  Settings,
  Bell,
  TrendingUp,
  Database,
  Shield,
  Download,
  Pause,
  Monitor,
  Activity
} from 'lucide-react';
import { apiService } from '../services/api';

interface SystemHealth {
  overall_health: string;
  timestamp: string;
  components: Record<string, any>;
  issues: string[];
  metrics: Record<string, any>;
}

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_io: number;
  active_connections: number;
  response_time: number;
  uptime: string;
  error_rate: number;
}

interface MaintenanceTask {
  id: string;
  title: string;
  description: string;
  type: 'scheduled' | 'automated' | 'manual';
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'running' | 'completed' | 'failed';
  scheduled_time: string;
  estimated_duration: number;
  last_run?: string;
  next_run?: string;
}

interface SystemAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
  component: string;
}

const SystemMaintenance: React.FC = () => {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [maintenanceTasks, setMaintenanceTasks] = useState<MaintenanceTask[]>([]);
  const [systemAlerts, setSystemAlerts] = useState<SystemAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'health' | 'maintenance' | 'alerts' | 'metrics'>('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [searchTerm, setSearchTerm] = useState('');
  const [alertFilter, setAlertFilter] = useState<'all' | 'info' | 'warning' | 'error' | 'critical'>('all');
  const [taskFilter, setTaskFilter] = useState<'all' | 'pending' | 'running' | 'completed' | 'failed'>('all');
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetchSystemData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchSystemData, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(`${config.wsUrl}/system-maintenance`);
      
      ws.onopen = () => {
        console.log('Connected to system maintenance WebSocket');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'health_update') {
          setSystemHealth(data.health);
        } else if (data.type === 'metrics_update') {
          setSystemMetrics(data.metrics);
        } else if (data.type === 'alert') {
          setSystemAlerts(prev => [data.alert, ...prev.slice(0, 49)]);
        } else if (data.type === 'task_update') {
          setMaintenanceTasks(prev => 
            prev.map(task => task.id === data.task.id ? data.task : task)
          );
        }
      };
      
      ws.onclose = () => {
        console.log('Disconnected from system maintenance WebSocket');
        logWebSocketError('WebSocket connection error', { page: 'SystemMaintenance', url: `${config.wsUrl}/system-maintenance` });
        // Attempt to reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };
      ws.onerror = () => {
        logWebSocketError('WebSocket connection error', { page: 'SystemMaintenance', url: `${config.wsUrl}/system-maintenance` });
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
      logWebSocketError('WebSocket connection error', { page: 'SystemMaintenance', error });
    }
  };

  const fetchSystemData = async () => {
    try {
      setLoading(true);
      
      // Fetch system health
      const healthResponse = await apiService.healthCheck();
      setSystemHealth(healthResponse);
      
      // Fetch system metrics (mock data for now)
      const metricsData: SystemMetrics = {
        cpu_usage: Math.random() * 100,
        memory_usage: Math.random() * 100,
        disk_usage: Math.random() * 100,
        network_io: Math.random() * 1000,
        active_connections: Math.floor(Math.random() * 500),
        response_time: Math.random() * 1000,
        uptime: '99.9%',
        error_rate: Math.random() * 5
      };
      setSystemMetrics(metricsData);
      
      // Fetch maintenance tasks (mock data)
      const tasksData: MaintenanceTask[] = [
        {
          id: '1',
          title: 'Database Cleanup',
          description: 'Clean up old logs and optimize database performance',
          type: 'scheduled',
          priority: 'medium',
          status: 'pending',
          scheduled_time: new Date(Date.now() + 3600000).toISOString(),
          estimated_duration: 30,
          last_run: new Date(Date.now() - 86400000).toISOString(),
          next_run: new Date(Date.now() + 3600000).toISOString()
        },
        {
          id: '2',
          title: 'Security Scan',
          description: 'Automated security vulnerability scan',
          type: 'automated',
          priority: 'high',
          status: 'running',
          scheduled_time: new Date().toISOString(),
          estimated_duration: 45
        },
        {
          id: '3',
          title: 'Backup Verification',
          description: 'Verify integrity of system backups',
          type: 'scheduled',
          priority: 'critical',
          status: 'completed',
          scheduled_time: new Date(Date.now() - 1800000).toISOString(),
          estimated_duration: 15,
          last_run: new Date(Date.now() - 1800000).toISOString()
        }
      ];
      setMaintenanceTasks(tasksData);
      
      // Fetch system alerts (mock data)
      const alertsData: SystemAlert[] = [
        {
          id: '1',
          type: 'warning',
          title: 'High Memory Usage',
          message: 'System memory usage is above 85%',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          acknowledged: false,
          component: 'system'
        },
        {
          id: '2',
          type: 'info',
          title: 'Maintenance Completed',
          message: 'Database cleanup completed successfully',
          timestamp: new Date(Date.now() - 600000).toISOString(),
          acknowledged: true,
          component: 'database'
        },
        {
          id: '3',
          type: 'error',
          title: 'API Endpoint Timeout',
          message: 'Timeout detected on /api/v1/vehicles endpoint',
          timestamp: new Date(Date.now() - 900000).toISOString(),
          acknowledged: false,
          component: 'api'
        }
      ];
      setSystemAlerts(alertsData);
      
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to fetch system data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-slate-300 bg-white/10';
    }
  };

  const getHealthStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy': return <CheckCircle className="w-5 h-5" />;
      case 'degraded': return <AlertTriangle className="w-5 h-5" />;
      case 'critical': return <AlertCircle className="w-5 h-5" />;
      default: return <Minus className="w-5 h-5" />;
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'info': return <Info className="w-5 h-5 text-blue-500" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'error': return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'critical': return <X className="w-5 h-5 text-red-600" />;
      default: return <Info className="w-5 h-5 text-slate-400" />;
    }
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-slate-300 bg-white/10';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-slate-300 bg-white/10';
    }
  };

  const runMaintenanceTask = async (taskId: string) => {
    try {
      // Mock API call to run maintenance task
      setMaintenanceTasks(prev =>
        prev.map(task =>
          task.id === taskId ? { ...task, status: 'running' } : task
        )
      );
      
      // Simulate task completion after 3 seconds
      setTimeout(() => {
        setMaintenanceTasks(prev =>
          prev.map(task =>
            task.id === taskId ? { ...task, status: 'completed', last_run: new Date().toISOString() } : task
          )
        );
      }, 3000);
    } catch (error) {
      console.error('Failed to run maintenance task:', error);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      setSystemAlerts(prev =>
        prev.map(alert =>
          alert.id === alertId ? { ...alert, acknowledged: true } : alert
        )
      );
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const filteredAlerts = systemAlerts.filter(alert => {
    const matchesFilter = alertFilter === 'all' || alert.type === alertFilter;
    const matchesSearch = alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.message.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const filteredTasks = maintenanceTasks.filter(task => {
    const matchesFilter = taskFilter === 'all' || task.status === taskFilter;
    const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  if (loading && !systemHealth) {
    return (
      <div className="min-h-screen bg-white/5 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-slate-300">Loading system maintenance data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white/5">
      {/* Header */}
      <div className="glass-card shadow-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Settings className="w-8 h-8 text-primary-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-white">System Maintenance</h1>
                <p className="text-sm text-slate-400">
                  Monitor system health, manage maintenance tasks, and view alerts
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm text-slate-300">Auto Refresh:</label>
                <button
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className={`p-2 rounded-lg ${autoRefresh ? 'bg-green-100 text-green-600' : 'bg-white/10 text-slate-300'}`}
                >
                  {autoRefresh ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                </button>
              </div>
              
              <button
                onClick={fetchSystemData}
                className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </button>
            </div>
          </div>
          
          {/* Tab Navigation */}
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: Monitor },
              { id: 'health', label: 'System Health', icon: Activity },
              { id: 'maintenance', label: 'Maintenance Tasks', icon: Settings },
              { id: 'alerts', label: 'Alerts', icon: Bell },
              { id: 'metrics', label: 'Metrics', icon: BarChart3 }
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center px-1 py-4 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-white/20'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Last Updated */}
        <div className="mb-6 text-sm text-slate-400">
          Last updated: {lastUpdated.toLocaleString()}
        </div>

        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* System Status Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-300">Overall Health</p>
                    <p className={`text-2xl font-bold ${getHealthStatusColor(systemHealth?.overall_health || 'unknown').split(' ')[0]}`}>
                      {systemHealth?.overall_health || 'Unknown'}
                    </p>
                  </div>
                  <div className={`p-3 rounded-full ${getHealthStatusColor(systemHealth?.overall_health || 'unknown')}`}>
                    {getHealthStatusIcon(systemHealth?.overall_health || 'unknown')}
                  </div>
                </div>
              </div>

              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-300">Active Tasks</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {maintenanceTasks.filter(t => t.status === 'running').length}
                    </p>
                  </div>
                  <div className="p-3 bg-blue-100 rounded-full">
                    <Settings className="w-5 h-5 text-blue-600" />
                  </div>
                </div>
              </div>

              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-300">Unacknowledged Alerts</p>
                    <p className="text-2xl font-bold text-red-600">
                      {systemAlerts.filter(a => !a.acknowledged).length}
                    </p>
                  </div>
                  <div className="p-3 bg-red-100 rounded-full">
                    <Bell className="w-5 h-5 text-red-600" />
                  </div>
                </div>
              </div>

              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-300">System Uptime</p>
                    <p className="text-2xl font-bold text-green-600">
                      {systemMetrics?.uptime || '99.9%'}
                    </p>
                  </div>
                  <div className="p-3 bg-green-100 rounded-full">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button className="flex items-center justify-center p-4 border border-white/20 rounded-lg hover:bg-white/5">
                  <Database className="w-5 h-5 mr-2 text-blue-600" />
                  <span className="text-sm font-medium">Database Cleanup</span>
                </button>
                <button className="flex items-center justify-center p-4 border border-white/20 rounded-lg hover:bg-white/5">
                  <Shield className="w-5 h-5 mr-2 text-green-600" />
                  <span className="text-sm font-medium">Security Scan</span>
                </button>
                <button className="flex items-center justify-center p-4 border border-white/20 rounded-lg hover:bg-white/5">
                  <Download className="w-5 h-5 mr-2 text-purple-600" />
                  <span className="text-sm font-medium">Backup System</span>
                </button>
                <button className="flex items-center justify-center p-4 border border-white/20 rounded-lg hover:bg-white/5">
                  <RefreshCw className="w-5 h-5 mr-2 text-orange-600" />
                  <span className="text-sm font-medium">Restart Services</span>
                </button>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
              <div className="space-y-4">
                {systemAlerts.slice(0, 5).map(alert => (
                  <div key={alert.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center">
                      {getAlertIcon(alert.type)}
                      <div className="ml-3">
                        <p className="text-sm font-medium text-white">{alert.title}</p>
                        <p className="text-xs text-slate-400">{new Date(alert.timestamp).toLocaleString()}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      alert.acknowledged ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {alert.acknowledged ? 'Acknowledged' : 'Pending'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'health' && systemHealth && (
          <div className="space-y-6">
            {/* System Health Status */}
            <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">System Health Status</h3>
                <div className={`flex items-center px-3 py-1 rounded-full ${getHealthStatusColor(systemHealth.overall_health)}`}>
                  {getHealthStatusIcon(systemHealth.overall_health)}
                  <span className="ml-2 text-sm font-medium">{systemHealth.overall_health}</span>
                </div>
              </div>

              {/* Component Health */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(systemHealth.components || {}).map(([component, status]) => (
                  <div key={component} className="p-4 border border-white/10 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Server className="w-5 h-5 text-slate-300 mr-2" />
                        <span className="text-sm font-medium text-white capitalize">{component}</span>
                      </div>
                      <div className={`flex items-center px-2 py-1 rounded-full text-xs font-medium ${getHealthStatusColor(status)}`}>
                        {getHealthStatusIcon(status)}
                        <span className="ml-1">{status}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Health Issues */}
              {systemHealth.issues && systemHealth.issues.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-md font-semibold text-white mb-3">Health Issues</h4>
                  <div className="space-y-2">
                    {systemHealth.issues.map((issue, index) => (
                      <div key={index} className="flex items-center p-3 bg-red-50 border border-red-200 rounded-lg">
                        <AlertTriangle className="w-5 h-5 text-red-500 mr-3" />
                        <span className="text-sm text-red-700">{issue}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'maintenance' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                    <input
                      type="text"
                      placeholder="Search maintenance tasks..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-white/20 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <select
                    value={taskFilter}
                    onChange={(e) => setTaskFilter(e.target.value as any)}
                    className="px-3 py-2 border border-white/20 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="running">Running</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Maintenance Tasks */}
            <div className="grid gap-6">
              {filteredTasks.map(task => (
                <div key={task.id} className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <h4 className="text-lg font-semibold text-white mr-3">{task.title}</h4>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTaskStatusColor(task.status)}`}>
                          {task.status}
                        </span>
                        <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                      </div>
                      <p className="text-slate-300 mb-4">{task.description}</p>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-slate-400">Type:</span>
                          <span className="ml-1 font-medium capitalize">{task.type}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Duration:</span>
                          <span className="ml-1 font-medium">{task.estimated_duration}m</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Scheduled:</span>
                          <span className="ml-1 font-medium">
                            {new Date(task.scheduled_time).toLocaleString()}
                          </span>
                        </div>
                        {task.last_run && (
                          <div>
                            <span className="text-slate-400">Last Run:</span>
                            <span className="ml-1 font-medium">
                              {new Date(task.last_run).toLocaleString()}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      {task.status === 'pending' && (
                        <button
                          onClick={() => runMaintenanceTask(task.id)}
                          className="flex items-center px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                        >
                          <Play className="w-4 h-4 mr-1" />
                          Run Now
                        </button>
                      )}
                      {task.status === 'running' && (
                        <div className="flex items-center px-3 py-1 bg-blue-100 text-blue-600 rounded-lg text-sm">
                          <RefreshCw className="w-4 h-4 mr-1 animate-spin" />
                          Running
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                    <input
                      type="text"
                      placeholder="Search alerts..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-white/20 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <select
                    value={alertFilter}
                    onChange={(e) => setAlertFilter(e.target.value as any)}
                    className="px-3 py-2 border border-white/20 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="all">All Types</option>
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="error">Error</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>
            </div>

            {/* System Alerts */}
            <div className="space-y-4">
              {filteredAlerts.map(alert => (
                <div key={alert.id} className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start">
                      <div className="mr-4 mt-1">
                        {getAlertIcon(alert.type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <h4 className="text-lg font-semibold text-white mr-3">{alert.title}</h4>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            alert.type === 'critical' ? 'bg-red-100 text-red-800' :
                            alert.type === 'error' ? 'bg-red-100 text-red-800' :
                            alert.type === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {alert.type}
                          </span>
                        </div>
                        <p className="text-slate-300 mb-2">{alert.message}</p>
                        <div className="flex items-center text-sm text-slate-400">
                          <Clock className="w-4 h-4 mr-1" />
                          <span>{new Date(alert.timestamp).toLocaleString()}</span>
                          <span className="mx-2">•</span>
                          <span className="capitalize">{alert.component}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      {!alert.acknowledged && (
                        <button
                          onClick={() => acknowledgeAlert(alert.id)}
                          className="flex items-center px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                        >
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Acknowledge
                        </button>
                      )}
                      {alert.acknowledged && (
                        <div className="flex items-center px-3 py-1 bg-green-100 text-green-600 rounded-lg text-sm">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Acknowledged
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'metrics' && systemMetrics && (
          <div className="space-y-6">
            {/* System Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <Cpu className="w-5 h-5 text-blue-600 mr-2" />
                    <span className="text-sm font-medium text-slate-300">CPU Usage</span>
                  </div>
                </div>
                <div className="mb-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-300">Usage</span>
                    <span className="font-medium">{systemMetrics.cpu_usage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-white/15 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        systemMetrics.cpu_usage > 80 ? 'bg-red-500' :
                        systemMetrics.cpu_usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${systemMetrics.cpu_usage}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <MemoryStick className="w-5 h-5 text-green-600 mr-2" />
                    <span className="text-sm font-medium text-slate-300">Memory Usage</span>
                  </div>
                </div>
                <div className="mb-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-300">Usage</span>
                    <span className="font-medium">{systemMetrics.memory_usage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-white/15 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        systemMetrics.memory_usage > 80 ? 'bg-red-500' :
                        systemMetrics.memory_usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${systemMetrics.memory_usage}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <HardDrive className="w-5 h-5 text-purple-600 mr-2" />
                    <span className="text-sm font-medium text-slate-300">Disk Usage</span>
                  </div>
                </div>
                <div className="mb-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-300">Usage</span>
                    <span className="font-medium">{systemMetrics.disk_usage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-white/15 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        systemMetrics.disk_usage > 80 ? 'bg-red-500' :
                        systemMetrics.disk_usage > 60 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${systemMetrics.disk_usage}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <Network className="w-5 h-5 text-orange-600 mr-2" />
                    <span className="text-sm font-medium text-slate-300">Network I/O</span>
                  </div>
                </div>
                <div className="mb-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-300">Throughput</span>
                    <span className="font-medium">{systemMetrics.network_io.toFixed(0)} MB/s</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <Wifi className="w-5 h-5 text-blue-600 mr-2" />
                    <span className="text-sm font-medium text-slate-300">Active Connections</span>
                  </div>
                </div>
                <p className="text-2xl font-bold text-blue-600">{systemMetrics.active_connections}</p>
              </div>

              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <Clock className="w-5 h-5 text-green-600 mr-2" />
                    <span className="text-sm font-medium text-slate-300">Response Time</span>
                  </div>
                </div>
                <p className="text-2xl font-bold text-green-600">{systemMetrics.response_time.toFixed(0)}ms</p>
              </div>

              <div className="glass-card rounded-lg shadow-sm border border-white/10 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
                    <span className="text-sm font-medium text-slate-300">Error Rate</span>
                  </div>
                </div>
                <p className="text-2xl font-bold text-red-600">{systemMetrics.error_rate.toFixed(2)}%</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemMaintenance;