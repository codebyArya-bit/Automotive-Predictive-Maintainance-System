import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  AreaChart,
  Area,
} from 'recharts';

interface QualityMetric {
  metric_name: string;
  current_value: number;
  target_value: number;
  trend: string;
  status: string;
  unit?: string;
  historical_data?: Array<{ date: string; value: number }>;
}

const QualityMetrics: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<QualityMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'cards' | 'charts'>('cards');

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const response = await apiService.getManufacturingDashboard();
      setMetrics(response.dashboard?.quality_metrics?.metrics || []);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'on_target':
      case 'good':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-orange-600 bg-orange-100';
      case 'critical':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-slate-300 bg-white/10';
    }
  };

  const getTrendIcon = (trend: string): string => {
    switch (trend.toLowerCase()) {
      case 'increasing':
        return '📈';
      case 'decreasing':
        return '📉';
      case 'stable':
        return '➡️';
      default:
        return '📊';
    }
  };

  // Chart data computations
  const comparisonData = useMemo(() => {
    return metrics.map((m) => ({
      name: m.metric_name.substring(0, 20),
      Current: m.current_value,
      Target: m.target_value,
    }));
  }, [metrics]);

  const radarData = useMemo(() => {
    return metrics.map((m) => ({
      metric: m.metric_name.substring(0, 15),
      achievement: m.target_value > 0 ? Math.round((m.current_value / m.target_value) * 100) : 0,
      target: 100,
    }));
  }, [metrics]);

  const achievementRate = useMemo(() => {
    if (metrics.length === 0) return 0;
    const onTarget = metrics.filter(m => m.status.toLowerCase() === 'on_target' || m.status.toLowerCase() === 'good').length;
    return Math.round((onTarget / metrics.length) * 100);
  }, [metrics]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Top Navigation */}
      <nav className="glass-card shadow-md">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate('/manufacturing-dashboard')} className="text-blue-600 hover:text-blue-800">
                ← Back
              </button>
              <h1 className="text-2xl font-bold text-white">📊 Quality Metrics Dashboard</h1>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm font-semibold text-white">
                  {user?.first_name} {user?.last_name}
                </div>
                <div className="text-xs text-slate-400 capitalize">{user?.role?.replace('_', ' ')}</div>
              </div>
              <button
                onClick={handleLogout}
                className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-6">
        {/* Header Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl shadow-xl p-8 mb-6">
          <h2 className="text-3xl font-bold mb-2">Quality Performance Metrics</h2>
          <p className="text-blue-100">Track, analyze, and optimize quality indicators</p>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
              <div className="text-2xl font-bold">{metrics.length}</div>
              <div className="text-sm text-blue-100">Total Metrics</div>
            </div>
            <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
              <div className="text-2xl font-bold">{achievementRate}%</div>
              <div className="text-sm text-blue-100">Achievement Rate</div>
            </div>
            <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
              <div className="text-2xl font-bold">
                {metrics.filter(m => m.trend?.toLowerCase() === 'increasing').length}
              </div>
              <div className="text-sm text-blue-100">Improving Metrics</div>
            </div>
          </div>
        </div>

        {/* View Controls */}
        <div className="glass-card rounded-xl shadow-md p-4 mb-6">
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('cards')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'cards' ? 'bg-blue-600 text-white' : 'bg-white/10 text-slate-200 hover:bg-white/15'
              }`}
            >
              Cards View
            </button>
            <button
              onClick={() => setViewMode('charts')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'charts' ? 'bg-blue-600 text-white' : 'bg-white/10 text-slate-200 hover:bg-white/15'
              }`}
            >
              Charts View
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
            <p className="text-slate-300">Loading quality metrics...</p>
          </div>
        ) : metrics.length === 0 ? (
          <div className="glass-card rounded-xl shadow-md p-12 text-center">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-xl font-bold text-white mb-2">No Metrics Available</h3>
            <p className="text-slate-300">Quality metrics data is not available at this time.</p>
          </div>
        ) : viewMode === 'cards' ? (
          /* Cards View */
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {metrics.map((metric, index) => (
              <div key={index} className="glass-card rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-white">{metric.metric_name}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(metric.status)}`}>
                    {metric.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div>
                    <div className="text-xs text-slate-400 mb-1">Current</div>
                    <div className="text-2xl font-bold text-blue-600">
                      {metric.current_value}
                      {metric.unit && <span className="text-sm ml-1">{metric.unit}</span>}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 mb-1">Target</div>
                    <div className="text-2xl font-bold text-slate-200">
                      {metric.target_value}
                      {metric.unit && <span className="text-sm ml-1">{metric.unit}</span>}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 mb-1">Trend</div>
                    <div className="text-2xl">{getTrendIcon(metric.trend)}</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div>
                  <div className="flex justify-between text-xs text-slate-300 mb-1">
                    <span>Progress</span>
                    <span>
                      {metric.target_value > 0
                        ? Math.round((metric.current_value / metric.target_value) * 100)
                        : 0}%
                    </span>
                  </div>
                  <div className="w-full bg-white/15 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all ${
                        metric.current_value >= metric.target_value ? 'bg-green-500' : 'bg-orange-500'
                      }`}
                      style={{
                        width: `${metric.target_value > 0
                          ? Math.min((metric.current_value / metric.target_value) * 100, 100)
                          : 0}%`
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Charts View */
          <div className="space-y-6">
            {/* Current vs Target Comparison */}
            <div className="glass-card rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold text-white mb-6">Current vs Target Performance</h3>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={comparisonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={120} fontSize={11} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Current" fill="#3b82f6" />
                  <Bar dataKey="Target" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Achievement Radar Chart */}
            <div className="glass-card rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold text-white mb-6">Achievement Overview (% of Target)</h3>
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" fontSize={10} />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar
                    name="Achievement %"
                    dataKey="achievement"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.6}
                  />
                  <Radar
                    name="Target"
                    dataKey="target"
                    stroke="#8b5cf6"
                    fill="#8b5cf6"
                    fillOpacity={0.2}
                  />
                  <Legend />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QualityMetrics;
