import React, { useState, useEffect, useMemo } from 'react';
import { TrendingUp, TrendingDown, Minus, ArrowLeft } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { getBadgeVariant, darkChartTheme } from '../config/theme';
import type { BadgeVariant } from '../config/theme';

interface RecurringDefect {
  defect_id: string;
  component: string;
  defect_type: string;
  frequency: number;
  severity: string;
  trend: string;
  vehicles_affected: number;
  first_occurrence: string;
  last_occurrence: string;
  cost_impact: number;
}

const RecurringDefects: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [defects, setDefects] = useState<RecurringDefect[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'list' | 'charts'>('list');
  const [severityFilter, setSeverityFilter] = useState<string>('all');

  useEffect(() => {
    loadDefects();
  }, []);

  const loadDefects = async () => {
    try {
      setLoading(true);
      const response = await apiService.getManufacturingDashboard();
      setDefects(response.dashboard?.recurring_defects || []);
    } catch (error) {
      console.error('Failed to load defects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const severityVariantMap: Record<string, BadgeVariant> = {
    critical: 'danger',
    high: 'warning',
    medium: 'info',
    low: 'success'
  };

  const getSeverityBadge = (severity: string): string => {
    const variant = severityVariantMap[severity?.toLowerCase()] || 'neutral';
    return getBadgeVariant(variant);
  };

  const getTrendIcon = (trend: string) => {
    switch (trend.toLowerCase()) {
      case 'increasing':
        return <TrendingUp className="w-4 h-4 text-emerald-300" />;
      case 'decreasing':
        return <TrendingDown className="w-4 h-4 text-rose-300" />;
      case 'stable':
        return <Minus className="w-4 h-4 text-slate-300" />;
      default:
        return <Minus className="w-4 h-4 text-slate-500" />;
    }
  };

  const tooltipProps = {
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

  // Chart data
  const severityData = useMemo(() => {
    const counts = { critical: 0, high: 0, medium: 0, low: 0 };
    defects.forEach((d) => {
      const sev = d.severity.toLowerCase();
      if (sev in counts) counts[sev as keyof typeof counts]++;
    });
    return [
      { name: 'Critical', value: counts.critical, color: '#ef4444' },
      { name: 'High', value: counts.high, color: '#f59e0b' },
      { name: 'Medium', value: counts.medium, color: '#3b82f6' },
      { name: 'Low', value: counts.low, color: '#10b981' },
    ].filter(item => item.value > 0);
  }, [defects]);

  const componentData = useMemo(() => {
    const componentMap = new Map<string, number>();
    defects.forEach((d) => {
      componentMap.set(d.component, (componentMap.get(d.component) || 0) + d.frequency);
    });
    return Array.from(componentMap.entries())
      .map(([component, frequency]) => ({ component, frequency }))
      .sort((a, b) => b.frequency - a.frequency)
      .slice(0, 10);
  }, [defects]);

  const filteredDefects = severityFilter === 'all'
    ? defects
    : defects.filter(d => d.severity.toLowerCase() === severityFilter.toLowerCase());

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-purple-950 text-slate-100">
      {/* Top Navigation */}
      <nav className="glass-card shadow-md border border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/manufacturing-dashboard')}
                className="btn-ghost flex items-center gap-2 text-sm text-slate-200"
              >
                <ArrowLeft className="w-4 h-4" />
                Back
              </button>
              <h1 className="text-2xl font-bold text-white">Recurring Defects Dashboard</h1>
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
        <div className="relative overflow-hidden glass-card rounded-2xl border border-white/10 p-8 mb-6">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600/40 via-pink-500/30 to-orange-400/30 opacity-60 blur-3xl" />
          <div className="relative">
            <p className="text-sm uppercase tracking-widest text-pink-100">Quality intelligence</p>
            <h2 className="text-3xl font-bold mb-2 text-white">Recurring Defects Dashboard</h2>
            <p className="text-slate-200">Surface component trends, severity insights, and cost impact at a glance.</p>
          </div>
        </div>

        {/* Controls */}
        <div className="glass-card rounded-xl shadow-md p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${
                  viewMode === 'list'
                    ? 'border-pink-400/60 bg-gradient-to-r from-purple-600 to-pink-500 text-white shadow-lg shadow-pink-900/30'
                    : 'text-slate-200 border-white/10 hover:border-pink-400/40 hover:bg-white/10'
                }`}
              >
                List View
              </button>
              <button
                onClick={() => setViewMode('charts')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors border ${
                  viewMode === 'charts'
                    ? 'border-pink-400/60 bg-gradient-to-r from-purple-600 to-pink-500 text-white shadow-lg shadow-pink-900/30'
                    : 'text-slate-200 border-white/10 hover:border-pink-400/40 hover:bg-white/10'
                }`}
              >
                Charts View
              </button>
            </div>

            <div className="flex gap-2 items-center">
              <span className="text-sm font-medium text-slate-200">Filter:</span>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="input-field w-40"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
            <p className="text-slate-300">Loading defects data...</p>
          </div>
        ) : viewMode === 'list' ? (
          /* List View */
          <div className="grid grid-cols-1 gap-4">
            {filteredDefects.length === 0 ? (
              <div className="glass-card rounded-xl shadow-md p-12 text-center">
                <div className="flex items-center justify-center mb-4">
                <TrendingUp className="w-12 h-12 text-emerald-300" />
              </div>
                <h3 className="text-xl font-bold text-white mb-2">No Recurring Defects</h3>
                <p className="text-slate-300">Great news! No recurring defect patterns detected.</p>
              </div>
            ) : (
              filteredDefects.map((defect) => (
                <div key={defect.defect_id} className="glass-card rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-bold text-white">{defect.component}</h3>
                        <p className="text-sm text-slate-300">{defect.defect_type}</p>
                        <p className="text-xs text-slate-400 mt-1">ID: {defect.defect_id}</p>
                      </div>
                      <div className="flex gap-2 items-center">
                        <span className={`status-indicator ${getSeverityBadge(defect.severity)}`}>
                          {defect.severity.toUpperCase()}
                        </span>
                        <span className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 p-2">
                          {getTrendIcon(defect.trend)}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <div className="text-xs text-slate-400 mb-1">Frequency</div>
                        <div className="font-bold text-cyan-200">{defect.frequency} times</div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-400 mb-1">Vehicles Affected</div>
                        <div className="font-bold text-amber-200">{defect.vehicles_affected}</div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-400 mb-1">Trend</div>
                        <div className="font-bold capitalize">{defect.trend}</div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-400 mb-1">Cost Impact</div>
                        <div className="font-bold text-rose-300">${defect.cost_impact?.toLocaleString() || 'N/A'}</div>
                    </div>
                  </div>

                  <div className="border-t pt-3">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-xs text-slate-400">First Occurrence</div>
                        <div className="text-slate-200">{new Date(defect.first_occurrence).toLocaleDateString()}</div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-400">Last Occurrence</div>
                        <div className="text-slate-200">{new Date(defect.last_occurrence).toLocaleDateString()}</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          /* Charts View */
          <div className="space-y-6">
            {/* Severity Distribution */}
            <div className="glass-card rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold text-white mb-6">Defects by Severity</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip {...tooltipProps} />
                  <Legend wrapperStyle={{ color: darkChartTheme.legendText }} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Top Components */}
            <div className="glass-card rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold text-white mb-6">Top 10 Components by Frequency</h3>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={componentData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={darkChartTheme.grid} />
                  <XAxis
                    dataKey="component"
                    angle={-45}
                    textAnchor="end"
                    height={120}
                    tick={axisTickStyle}
                    stroke={darkChartTheme.axis}
                  />
                  <YAxis stroke={darkChartTheme.axis} tick={axisTickStyle} />
                  <Tooltip {...tooltipProps} />
                  <Bar dataKey="frequency" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecurringDefects;
