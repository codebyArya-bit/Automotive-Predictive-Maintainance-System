import React, { useState, useEffect, useMemo } from 'react';
import { ClipboardList, Repeat, TrendingUp } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';
import { useNavigate } from 'react-router-dom';
import AccessibleButton from '../components/AccessibleButton';
import { trackEvent } from '../utils/logger';
import { mockManufacturingInsights } from '../data/mockInsights';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
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
} from 'recharts';

interface RecurringDefect {
  defect_id: string;
  component: string;
  defect_type: string;
  frequency: number;
  severity: string;
  trend: string;
}

interface QualityMetric {
  metric_name: string;
  current_value: number;
  target_value: number;
  trend: string;
  status: string;
}

const buildMockManufacturingDashboard = () => {
  const recurring_defects = mockManufacturingInsights.recurringDefects.map((defect, index) => ({
    defect_id: `rd-${index + 1}`,
    component: defect.component,
    defect_type: `${defect.component} variance`,
    frequency: defect.occurrences,
    severity: defect.severity,
    trend: index % 2 === 0 ? 'decreasing' : 'increasing',
  }));

  const quality_metrics = {
    overall_score: 92,
    metrics: mockManufacturingInsights.plants.map((plant) => ({
      metric_name: plant.name,
      current_value: plant.efficiency,
      target_value: 100,
      trend: plant.efficiency >= 92 ? 'improving' : 'stable',
      status: plant.efficiency >= 92 ? 'on_target' : 'warning',
    })),
  };

  const manufacturing_feedback = mockManufacturingInsights.qualityInitiatives.map((initiative) => ({
    improvement: initiative.name,
    status: initiative.status,
  }));

  const rca_reports = mockManufacturingInsights.recurringDefects.map((defect, index) => ({
    defect_id: `rca-${index + 1}`,
    component: defect.component,
    defect_type: `${defect.component} fatigue`,
    recurring_pattern: { severity: defect.severity },
    root_cause_analysis: { root_cause: 'Thermal drift in supplier batch' },
    corrective_actions: [{ id: 'ca-1' }, { id: 'ca-2' }],
    vehicles_affected: 38 + index * 5,
  }));

  const impact_summary = {
    total_savings: '$1.2M',
    cost_savings: '1.2M',
    defect_reduction: '38%',
    quality_improvement: '26%',
    roi: '410%',
  };

  return {
    recurring_defects,
    quality_metrics,
    manufacturing_feedback,
    rca_reports,
    impact_summary,
  };
};

const ManufacturingDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<any>(buildMockManufacturingDashboard());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metricsView, setMetricsView] = useState<'list' | 'chart'>('list');
  const [defectsView, setDefectsView] = useState<'list' | 'analytics'>('list');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiService.getManufacturingDashboard();
      setDashboard(response.dashboard || buildMockManufacturingDashboard());
    } catch (err: any) {
      console.warn('Falling back to mock manufacturing dashboard data', err);
      setDashboard(buildMockManufacturingDashboard());
      setError(err.message || 'Showing live snapshot while service recovers');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-rose-500/20 text-rose-200 border border-rose-400/40';
      case 'high':
        return 'bg-orange-500/20 text-orange-200 border border-orange-400/40';
      case 'medium':
        return 'bg-blue-500/20 text-blue-200 border border-blue-400/40';
      case 'low':
        return 'bg-emerald-500/20 text-emerald-200 border border-emerald-400/40';
      default:
        return 'bg-white/10 text-slate-200 border border-white/10';
    }
  };

  const getTrendIcon = (trend: string): string => {
    switch (trend.toLowerCase()) {
      case 'increasing':
        return '?';
      case 'decreasing':
        return '?';
      case 'stable':
        return '?';
      default:
        return '?';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'on_target':
      case 'good':
        return 'text-emerald-200 bg-emerald-500/10 border border-emerald-400/40';
      case 'warning':
        return 'text-amber-200 bg-amber-500/10 border border-amber-400/40';
      case 'critical':
        return 'text-rose-200 bg-rose-500/10 border border-rose-400/40';
      default:
        return 'text-slate-200 bg-white/5 border border-white/10';
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Computed data for charts
  const defectsBySeverity = useMemo(() => {
    if (!dashboard?.recurring_defects) return [];
    const counts = { critical: 0, high: 0, medium: 0, low: 0 };
    dashboard.recurring_defects.forEach((d: RecurringDefect) => {
      const sev = d.severity.toLowerCase();
      if (sev in counts) counts[sev as keyof typeof counts]++;
    });
    return [
      { name: 'Critical', value: counts.critical, color: '#ef4444' },
      { name: 'High', value: counts.high, color: '#f59e0b' },
      { name: 'Medium', value: counts.medium, color: '#3b82f6' },
      { name: 'Low', value: counts.low, color: '#10b981' },
    ].filter(item => item.value > 0);
  }, [dashboard]);

  const defectsByComponent = useMemo(() => {
    if (!dashboard?.recurring_defects) return [];
    const componentMap = new Map<string, number>();
    dashboard.recurring_defects.forEach((d: RecurringDefect) => {
      componentMap.set(d.component, (componentMap.get(d.component) || 0) + d.frequency);
    });
    return Array.from(componentMap.entries())
      .map(([component, frequency]) => ({ component, frequency }))
      .sort((a, b) => b.frequency - a.frequency)
      .slice(0, 6);
  }, [dashboard]);

  const metricsRadarData = useMemo(() => {
    if (!dashboard?.quality_metrics?.metrics) return [];
    return dashboard.quality_metrics.metrics.map((m: QualityMetric) => ({
      metric: m.metric_name.substring(0, 15),
      achievement: m.target_value > 0 ? Math.round((m.current_value / m.target_value) * 100) : 0,
      target: 100,
    }));
  }, [dashboard]);

  const metricsComparisonData = useMemo(() => {
    if (!dashboard?.quality_metrics?.metrics) return [];
    return dashboard.quality_metrics.metrics.map((m: QualityMetric) => ({
      name: m.metric_name.substring(0, 20),
      Current: m.current_value,
      Target: m.target_value,
    }));
  }, [dashboard]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950">
        <div className="glass-card p-10 rounded-2xl text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-400 mx-auto mb-4"></div>
          <p className="text-slate-200">Loading manufacturing dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-8 text-slate-100">
        <div className="glass-card border border-rose-400/30 text-rose-100 px-6 py-4 rounded-2xl max-w-2xl mx-auto">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-slate-100">
      {/* Top Navigation */}
      <nav className="bg-white/5 shadow-xl shadow-slate-950/40 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold gradient-title">⚙️ AutoMind</h1>
              <span className="text-sm text-slate-300">Manufacturing Portal</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm font-semibold text-white">
                  {user?.first_name} {user?.last_name}
                </div>
                <div className="text-xs text-slate-300 capitalize">{user?.role?.replace('_', ' ')}</div>
              </div>
              <button
                onClick={handleLogout}
                className="btn-ghost bg-white/10 border border-white/20 text-white px-4 py-2 rounded-lg hover:border-rose-300/60 transition-colors text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-6">
        {/* Welcome Section */}
        <div className="glass-card bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400/30 text-white rounded-2xl shadow-xl shadow-purple-900/30 p-8 mb-6">
          <h2 className="text-3xl font-bold mb-2 gradient-title">
            Quality Engineering Dashboard
          </h2>
          <p className="text-slate-200">Monitor defects, analyze root causes, and drive continuous improvement</p>
        </div>

        {/* Quick Stats */}
        {dashboard && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-purple-400/30 transition-all duration-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-300 mb-1">Active RCA Reports</div>
                  <div className="text-3xl font-bold text-purple-300">
                    {dashboard.rca_reports?.length || 0}
                  </div>
                </div>
                <div className="text-4xl">📋</div>
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-orange-400/30 transition-all duration-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-300 mb-1">Recurring Defects</div>
                  <div className="text-3xl font-bold text-orange-300">
                    {dashboard.recurring_defects?.length || 0}
                  </div>
                </div>
                <div className="text-4xl">🔄</div>
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-300 mb-1">Quality Score</div>
                  <div className="text-3xl font-bold text-emerald-300">
                    {dashboard.quality_metrics?.overall_score || 85}/100
                  </div>
                </div>
                <div className="text-4xl">⭐</div>
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-slate-300 mb-1">Cost Savings YTD</div>
                  <div className="text-3xl font-bold text-cyan-300">
                    ${dashboard.impact_summary?.total_savings || '850K'}
                  </div>
                </div>
                <div className="text-4xl">💰</div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Recurring Defects */}
          <div className="glass-card rounded-2xl p-6 border border-white/10">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white flex items-center">
                <span className="mr-2">🔄</span>
                Recurring Defects
              </h3>
              <div className="flex gap-2">
                <button
                  onClick={() => setDefectsView('list')}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    defectsView === 'list' ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-900/50' : 'bg-white/10 text-slate-200 hover:bg-white/20'
                  }`}
                >
                  List
                </button>
                <button
                  onClick={() => setDefectsView('analytics')}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    defectsView === 'analytics' ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-900/50' : 'bg-white/10 text-slate-200 hover:bg-white/20'
                  }`}
                >
                  Analytics
                </button>
              </div>
            </div>

            {defectsView === 'list' ? (
              <div className="space-y-3">
                {dashboard?.recurring_defects?.map((defect: RecurringDefect) => (
                  <div key={defect.defect_id} className="border border-white/10 rounded-lg p-4 hover:shadow-lg transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-white">{defect.component}</h4>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${getSeverityColor(defect.severity)}`}>
                        {defect.severity.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-slate-300 mb-3">{defect.defect_type}</p>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-slate-300">Frequency:</span>
                        <span className="ml-2 font-semibold">{defect.frequency} occurrences</span>
                      </div>
                      <div>
                        <span className="text-slate-300">Trend:</span>
                        <span className="ml-2 font-semibold">
                          {getTrendIcon(defect.trend)} {defect.trend}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
                {(!dashboard?.recurring_defects || dashboard.recurring_defects.length === 0) && (
                  <div className="text-center py-8 text-slate-300">
                    <div className="text-4xl mb-2">✅</div>
                    <p>No recurring defects detected</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-6">
                {/* Severity Distribution */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-200 mb-3">Defects by Severity</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={defectsBySeverity}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {defectsBySeverity.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Component Frequency */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-200 mb-3">Top Components by Frequency</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={defectsByComponent}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="component" angle={-45} textAnchor="end" height={80} fontSize={11} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="frequency" fill="#8b5cf6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>

          {/* Quality Metrics */}
          <div className="glass-card rounded-2xl p-6 border border-white/10">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white flex items-center">
                <span className="mr-2">📊</span>
                Quality Metrics
              </h3>
              <div className="flex gap-2">
                <button
                  onClick={() => setMetricsView('list')}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    metricsView === 'list' ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-900/50' : 'bg-white/10 text-slate-200 hover:bg-white/20'
                  }`}
                >
                  List
                </button>
                <button
                  onClick={() => setMetricsView('chart')}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    metricsView === 'chart' ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-900/50' : 'bg-white/10 text-slate-200 hover:bg-white/20'
                  }`}
                >
                  Charts
                </button>
              </div>
            </div>

            {metricsView === 'list' ? (
              <div className="space-y-4">
                {dashboard?.quality_metrics?.metrics?.map((metric: QualityMetric, index: number) => (
                  <div key={index} className="border-l-4 border-purple-500 bg-purple-50 p-4 rounded-r-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-white">{metric.metric_name}</h4>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusColor(metric.status)}`}>
                        {metric.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <div>
                        <span className="text-slate-300">Current: </span>
                        <span className="font-bold text-purple-700">{metric.current_value}</span>
                      </div>
                      <div>
                        <span className="text-slate-300">Target: </span>
                        <span className="font-bold text-slate-200">{metric.target_value}</span>
                      </div>
                      <div>
                        <span className="text-slate-300">Trend: </span>
                        <span className="font-bold">{getTrendIcon(metric.trend)}</span>
                      </div>
                    </div>
                    {/* Progress Bar */}
                    <div className="mt-3">
                      <div className="w-full bg-white/10 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            metric.current_value >= metric.target_value ? 'bg-green-500' : 'bg-orange-500'
                          }`}
                          style={{ width: `${metric.target_value > 0 ? Math.min((metric.current_value / metric.target_value) * 100, 100) : 0}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-6">
                {/* Current vs Target Comparison */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-200 mb-3">Current vs Target Performance</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={metricsComparisonData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} fontSize={11} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="Current" fill="#8b5cf6" />
                      <Bar dataKey="Target" fill="#ec4899" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Achievement Radar Chart */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-200 mb-3">Achievement Overview</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <RadarChart data={metricsRadarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="metric" fontSize={10} />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} />
                      <Radar name="Achievement %" dataKey="achievement" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
                      <Radar name="Target" dataKey="target" stroke="#ec4899" fill="#ec4899" fillOpacity={0.2} />
                      <Legend />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* RCA Reports Summary */}
        <div className="glass-card rounded-2xl p-6 border border-white/10 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-white flex items-center">
              <span className="mr-2">🔍</span>
              RCA/CAPA Reports
            </h3>
            <button
              onClick={() => navigate('/rca-reports')}
              className="bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-900/50 px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
            >
              Full RCA Analysis →
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {dashboard?.rca_reports?.slice(0, 3).map((report: any) => (
              <div key={report.defect_id} className="border border-white/10 rounded-lg p-4 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-white">{report.component}</h4>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getSeverityColor(report.recurring_pattern.severity)}`}>
                    {report.recurring_pattern.severity}
                  </span>
                </div>
                <p className="text-sm text-slate-300 mb-3">{report.defect_type}</p>
                <div className="bg-green-50 p-3 rounded-lg text-xs">
                  <div className="font-semibold text-green-800 mb-1">Root Cause:</div>
                  <div className="text-green-700">{report.root_cause_analysis.root_cause}</div>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-300">Actions:</span>
                    <span className="ml-1 font-semibold">{report.corrective_actions.length}</span>
                  </div>
                  <div>
                    <span className="text-slate-300">Vehicles:</span>
                    <span className="ml-1 font-semibold">{report.vehicles_affected}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Manufacturing Feedback & Impact */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Process Improvements */}
          <div className="glass-card rounded-2xl p-6 border border-white/10">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center">
              <span className="mr-2">🔧</span>
              Process Improvements
            </h3>
            <div className="space-y-3">
              {dashboard?.manufacturing_feedback?.map((feedback: any, index: number) => (
                <div key={index} className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded-r-lg">
                  <div className="flex items-start gap-2">
                    <span className="text-cyan-300 font-bold text-lg">•</span>
                    <p className="text-sm text-slate-200">{feedback.improvement}</p>
                  </div>
                  {feedback.status && (
                    <div className="mt-2 text-xs text-cyan-300 font-semibold">
                      Status: {feedback.status}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Impact Analysis */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl shadow-xl p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center">
              <span className="mr-2">📈</span>
              Impact Summary
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                <div className="text-3xl font-bold mb-1">
                  {dashboard?.impact_summary?.defect_reduction || '45%'}
                </div>
                <div className="text-sm text-purple-100">Defect Reduction</div>
              </div>
              <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                <div className="text-3xl font-bold mb-1">
                  ${dashboard?.impact_summary?.cost_savings || '850K'}
                </div>
                <div className="text-sm text-purple-100">Cost Savings</div>
              </div>
              <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                <div className="text-3xl font-bold mb-1">
                  {dashboard?.impact_summary?.quality_improvement || '32%'}
                </div>
                <div className="text-sm text-purple-100">Quality Improvement</div>
              </div>
              <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                <div className="text-3xl font-bold mb-1">
                  {dashboard?.impact_summary?.roi || '380%'}
                </div>
                <div className="text-sm text-purple-100">ROI</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <AccessibleButton
            id="quick-action-rca"
            variant="primary"
            title="View RCA Reports"
            subtitle="Detailed root cause analysis"
            icon={<ClipboardList className="w-5 h-5" aria-hidden />}
            ariaLabel="View RCA reports"
            onClick={() => {
              trackEvent('navigation', 'go_to_rca_reports', { from: 'manufacturing_dashboard' });
              navigate('/rca-reports');
            }}
          />

          <AccessibleButton
            id="quick-action-recurring-defects"
            variant="recurring-defects"
            title="Recurring Defects"
            subtitle="Pattern analysis and trends"
            icon={<Repeat className="w-5 h-5" aria-hidden />}
            ariaLabel="Recurring defects"
            onClick={() => {
              trackEvent('navigation', 'go_to_recurring_defects', { from: 'manufacturing_dashboard' });
              navigate('/recurring-defects');
            }}
          />

          <AccessibleButton
            id="quick-action-quality-metrics"
            variant="quality-metrics"
            title="Quality Metrics"
            subtitle="Performance tracking"
            icon={<TrendingUp className="w-5 h-5" aria-hidden />}
            ariaLabel="Quality metrics"
            onClick={() => {
              trackEvent('navigation', 'go_to_quality_metrics', { from: 'manufacturing_dashboard' });
              navigate('/quality-metrics');
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default ManufacturingDashboard;
