import React, { useEffect, useMemo, useRef, useState } from 'react';
import { apiService } from '../services/api';
import useWebSocket from '../hooks/useWebSocket';
import {
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart as RechartsLineChart,
  Line,
} from 'recharts';

interface RCAReport {
  defect_id: string;
  defect_type: string;
  component: string;
  vehicles_affected: number;
  recurring_pattern: {
    frequency: number;
    trend: string;
    severity: string;
  };
  root_cause_analysis: {
    problem_statement: string;
    rca_method: string;
    five_why_analysis: string[];
    root_cause: string;
    ishikawa_factors?: {
      method: string[];
      material: string[];
      machine: string[];
      manpower: string[];
      measurement: string[];
      environment: string[];
    };
  };
  corrective_actions: Array<{
    action_id: string;
    description: string;
    responsible_party: string;
    timeline: string;
    status: string;
  }>;
  preventive_actions: Array<{
    action_id: string;
    description: string;
    responsible_party: string;
    implementation_date: string;
    status: string;
  }>;
  manufacturing_feedback: {
    process_improvements: string[];
    quality_control_updates: string[];
    supplier_actions: string[];
  };
  impact_analysis: {
    expected_defect_reduction: string;
    estimated_cost_savings: string;
    implementation_cost: string;
    roi: string;
    quality_improvement_score: number;
  };
}

const RCACAPAReport: React.FC = () => {
  const [reports, setReports] = useState<RCAReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<RCAReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState<'all' | 'low' | 'medium' | 'high' | 'critical'>('all');
  const [componentQuery, setComponentQuery] = useState('');
  const [sortBy, setSortBy] = useState<'frequency' | 'vehicles' | 'severity'>('frequency');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const lastRefreshRef = useRef<number>(0);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiService.getRCAReports();
      const reportData = response.rca_capa_data?.reports || [];

      setReports(reportData);
      if (reportData.length > 0) {
        setSelectedReport(reportData[0]);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load RCA/CAPA reports');
    } finally {
      setLoading(false);
    }
  };

  // WebSocket-triggered refresh for real-time updates
  // Normalize WS base: allow VITE_WS_URL to be either ws://host or ws://host/ws
  const rawWsBase: string = (import.meta as any)?.env?.VITE_WS_URL || 'ws://localhost:8000';
  const wsBase = rawWsBase.endsWith('/ws')
    ? rawWsBase
    : rawWsBase.endsWith('/')
      ? `${rawWsBase}ws`
      : `${rawWsBase}/ws`;
  const wsUrl = `${wsBase}/dashboard`;
  const { lastMessage } = useWebSocket(wsUrl, {
    reconnectInterval: 4000,
    maxReconnectAttempts: 100,
  });

  useEffect(() => {
    if (!lastMessage) return;
    const now = Date.now();
    // Throttle refresh to at most once every 12 seconds
    if (now - lastRefreshRef.current > 12000) {
      lastRefreshRef.current = now;
      loadReports();
    }
  }, [lastMessage]);

  const getSeverityColor = (severity: string): string => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'medium':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-white/10 text-white border-white/20';
    }
  };

  const getStatusBadge = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-500 text-white';
      case 'in_progress':
      case 'in progress':
        return 'bg-blue-500 text-white';
      case 'pending':
        return 'bg-orange-500 text-white';
      case 'planned':
        return 'bg-purple-500 text-white';
      default:
        return 'bg-white/50 text-white';
    }
  };

  const filteredAndSortedReports = useMemo(() => {
    const filtered = reports.filter((r) => {
      const sev = r.recurring_pattern.severity.toLowerCase();
      const sevOk = severityFilter === 'all' || sev === severityFilter;
      const compOk = componentQuery.trim() === '' || r.component.toLowerCase().includes(componentQuery.toLowerCase());
      return sevOk && compOk;
    });
    const sorted = filtered.sort((a, b) => {
      let va = 0, vb = 0;
      if (sortBy === 'frequency') {
        va = a.recurring_pattern.frequency; vb = b.recurring_pattern.frequency;
      } else if (sortBy === 'vehicles') {
        va = a.vehicles_affected; vb = b.vehicles_affected;
      } else if (sortBy === 'severity') {
        const order = { low: 1, medium: 2, high: 3, critical: 4 } as Record<string, number>;
        va = order[a.recurring_pattern.severity.toLowerCase()] || 0;
        vb = order[b.recurring_pattern.severity.toLowerCase()] || 0;
      }
      return sortDir === 'asc' ? va - vb : vb - va;
    });
    return sorted.map((r) => {
      const statusSummary = (() => {
        const statuses = [...r.corrective_actions, ...r.preventive_actions].map((a) => a.status.toLowerCase());
        const completed = statuses.filter((s) => s.includes('completed')).length;
        const inProgress = statuses.filter((s) => s.includes('in') && s.includes('progress')).length;
        const open = statuses.filter((s) => s.includes('pending') || s.includes('planned')).length;
        return { completed, inProgress, open };
      })();
      return (
        <tr key={r.defect_id} role="row" className="hover:glass-card/5">
          <td className="px-4 py-2 text-sm text-white" role="cell">
            <button className="text-primary-700 hover:underline" onClick={() => setSelectedReport(r)} aria-label={`Open report ${r.defect_id}`}>{r.defect_id}</button>
          </td>
          <td className="px-4 py-2 text-sm text-slate-200" role="cell">{r.component}</td>
          <td className="px-4 py-2 text-sm text-slate-200" role="cell">{r.defect_type}</td>
          <td className="px-4 py-2 text-sm text-slate-200" role="cell">{r.recurring_pattern.frequency}</td>
          <td className="px-4 py-2 text-sm" role="cell">
            <span className={`px-2 py-1 rounded-full border ${getSeverityColor(r.recurring_pattern.severity)}`}>{r.recurring_pattern.severity}</span>
          </td>
          <td className="px-4 py-2 text-sm text-slate-200" role="cell">{r.vehicles_affected}</td>
          <td className="px-4 py-2 text-xs" role="cell">
            <div className="flex items-center gap-2" aria-label="CAPA status counts">
              <span className="px-2 py-0.5 rounded-full bg-green-100 text-green-800">Completed {statusSummary.completed}</span>
              <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">In Progress {statusSummary.inProgress}</span>
              <span className="px-2 py-0.5 rounded-full bg-orange-100 text-orange-800">Open {statusSummary.open}</span>
            </div>
          </td>
        </tr>
      );
    });
  }, [reports, severityFilter, componentQuery, sortBy, sortDir]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading RCA/CAPA reports...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      </div>
    );
  }

  if (reports.length === 0) {
    return (
      <div className="p-8">
        <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded-lg">
          No RCA/CAPA reports available at this time.
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 glass-card/5 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Filters and Summary */}
        <div className="glass-card rounded-xl shadow-md p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-end gap-4">
            <div>
              <label htmlFor="severity" className="block text-sm font-medium text-slate-200">Severity</label>
              <select
                id="severity"
                className="mt-1 block w-44 rounded-md border-white/20 shadow-sm focus:border-primary-600 focus:ring-primary-600"
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value as any)}
              >
                <option value="all">All</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div className="flex-1">
              <label htmlFor="component" className="block text-sm font-medium text-slate-200">Component</label>
              <input
                id="component"
                type="text"
                className="mt-1 block w-full rounded-md border-white/20 shadow-sm focus:border-primary-600 focus:ring-primary-600"
                placeholder="Search component..."
                value={componentQuery}
                onChange={(e) => setComponentQuery(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="sortby" className="block text-sm font-medium text-slate-200">Sort by</label>
              <div className="flex gap-2">
                <select
                  id="sortby"
                  className="mt-1 block w-44 rounded-md border-white/20 shadow-sm focus:border-primary-600 focus:ring-primary-600"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                >
                  <option value="frequency">Frequency</option>
                  <option value="vehicles">Vehicles Affected</option>
                  <option value="severity">Severity</option>
                </select>
                <button
                  className="mt-1 px-3 py-2 rounded-md border border-white/20 hover:glass-card/5"
                  onClick={() => setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))}
                  aria-label={`Toggle sort direction, currently ${sortDir}`}
                >
                  {sortDir === 'asc' ? 'Asc' : 'Desc'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Interactive Table */}
        <div className="glass-card rounded-xl shadow-md p-6 mb-6" role="region" aria-label="RCA findings table" aria-live="polite">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200" role="table">
              <thead className="glass-card/5" role="rowgroup">
                <tr role="row">
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Defect ID</th>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Component</th>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Defect Type</th>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Frequency</th>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Severity</th>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Vehicles</th>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="glass-card divide-y divide-gray-100" role="rowgroup">
                {filteredAndSortedReports}
              </tbody>
            </table>
          </div>
        </div>
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-2xl shadow-xl p-8 mb-6">
          <h1 className="text-3xl font-bold mb-2 flex items-center">
            <span className="mr-3">🔍</span>
            Root Cause Analysis (RCA) & CAPA Reports
          </h1>
          <p className="text-purple-100">Systematic defect analysis with corrective and preventive actions</p>
        </div>

        {/* Report Selector */}
        <div className="glass-card rounded-xl shadow-md p-6 mb-6">
          <h2 className="text-lg font-semibold text-white mb-4">Select Report</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {reports.map((report) => (
              <button
                key={report.defect_id}
                onClick={() => setSelectedReport(report)}
                className={`text-left p-4 rounded-lg border-2 transition-all ${
                  selectedReport?.defect_id === report.defect_id
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-white/10 hover:border-purple-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-white">{report.component}</span>
                  <span className={`text-xs px-2 py-1 rounded-full border ${getSeverityColor(report.recurring_pattern.severity)}`}>
                    {report.recurring_pattern.severity}
                  </span>
                </div>
                <div className="text-sm text-slate-300">{report.defect_type}</div>
                <div className="text-xs text-slate-400 mt-2">
                  {report.vehicles_affected} vehicles affected
                </div>
              </button>
            ))}
          </div>
        </div>

        {selectedReport && (
          <>
            {/* Report Details */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              {/* Problem Statement */}
              <div className="lg:col-span-3 glass-card rounded-xl shadow-md p-6">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                  <span className="mr-2">❗</span>
                  Problem Statement
                </h2>
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
                  <p className="text-white leading-relaxed">
                    {selectedReport.root_cause_analysis.problem_statement}
                  </p>
                </div>
                <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                  <div className="glass-card/5 p-3 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {selectedReport.vehicles_affected}
                    </div>
                    <div className="text-xs text-slate-300 mt-1">Vehicles Affected</div>
                  </div>
                  <div className="glass-card/5 p-3 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {selectedReport.recurring_pattern.frequency}
                    </div>
                    <div className="text-xs text-slate-300 mt-1">Occurrence Frequency</div>
                  </div>
                  <div className="glass-card/5 p-3 rounded-lg">
                    <div className={`text-sm font-bold px-3 py-1 rounded-full inline-block ${getSeverityColor(selectedReport.recurring_pattern.severity)}`}>
                      {selectedReport.recurring_pattern.severity.toUpperCase()}
                    </div>
                    <div className="text-xs text-slate-300 mt-1">Severity Level</div>
                  </div>
                </div>
              </div>

              {/* 5-Why Analysis */}
              <div className="lg:col-span-2 glass-card rounded-xl shadow-md p-6">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                  <span className="mr-2">🤔</span>
                  5-Why Analysis
                </h2>
                <div className="space-y-3">
                  {selectedReport.root_cause_analysis.five_why_analysis.map((why, index) => {
                    const isQuestion = why.toLowerCase().startsWith('why');
                    const isRootCause = index === selectedReport.root_cause_analysis.five_why_analysis.length - 1;

                    return (
                      <div
                        key={index}
                        className={`p-4 rounded-lg ${
                          isQuestion
                            ? 'bg-blue-50 border-l-4 border-blue-500'
                            : isRootCause
                            ? 'bg-green-50 border-l-4 border-green-500 font-semibold'
                            : 'bg-white/5 border-l-4 border-white/20'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex-shrink-0 w-8 h-8 glass-card rounded-full flex items-center justify-center font-bold text-sm">
                            {Math.floor(index / 2) + 1}
                          </div>
                          <p className="text-sm text-white flex-1">{why}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Root Cause Highlight */}
                <div className="mt-6 bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-xl">
                  <h3 className="text-lg font-bold mb-2 flex items-center">
                    <span className="mr-2">🎯</span>
                    Root Cause Identified
                  </h3>
                  <p className="text-lg">{selectedReport.root_cause_analysis.root_cause}</p>
                </div>
              </div>

              {/* Ishikawa Factors */}
              {selectedReport.root_cause_analysis.ishikawa_factors && (
                <div className="glass-card rounded-xl shadow-md p-6">
                  <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                    <span className="mr-2">🐟</span>
                    Ishikawa Factors
                  </h2>
                  <div className="space-y-4">
                    {Object.entries(selectedReport.root_cause_analysis.ishikawa_factors).map(([category, factors]) => (
                      <div key={category} className="border-l-4 border-purple-500 pl-4">
                        <h4 className="font-semibold text-purple-700 capitalize mb-2">{category}</h4>
                        <ul className="space-y-1">
                          {(factors as string[]).map((factor, idx) => (
                            <li key={idx} className="text-sm text-slate-200 flex items-start">
                              <span className="mr-2">•</span>
                              <span>{factor}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* CAPA Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Corrective Actions */}
              <div className="glass-card rounded-xl shadow-md p-6">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                  <span className="mr-2">🔧</span>
                  Corrective Actions
                </h2>
                <div className="space-y-3">
                  {selectedReport.corrective_actions.map((action) => (
                    <div key={action.action_id} className="border border-white/10 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(action.status)}`}>
                          {action.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-white mb-3">{action.description}</p>
                      <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                        <div>
                          <span className="font-semibold">Responsible:</span> {action.responsible_party}
                        </div>
                        <div>
                          <span className="font-semibold">Timeline:</span> {action.timeline}
                        </div>
                        <div className="col-span-2 text-slate-400">Updated: {new Date().toLocaleString()}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Preventive Actions */}
              <div className="glass-card rounded-xl shadow-md p-6">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                  <span className="mr-2">🛡️</span>
                  Preventive Actions
                </h2>
                <div className="space-y-3">
                  {selectedReport.preventive_actions.map((action) => (
                    <div key={action.action_id} className="border border-white/10 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(action.status)}`}>
                          {action.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-white mb-3">{action.description}</p>
                      <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                        <div>
                          <span className="font-semibold">Responsible:</span> {action.responsible_party}
                        </div>
                        <div>
                          <span className="font-semibold">Implementation:</span> {action.implementation_date}
                        </div>
                        <div className="col-span-2 text-slate-400">Updated: {new Date().toLocaleString()}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Manufacturing Feedback */}
            <div className="glass-card rounded-xl shadow-md p-6 mb-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <span className="mr-2">⚙️</span>
                Manufacturing Feedback
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h3 className="font-semibold text-blue-700 mb-3">Process Improvements</h3>
                  <ul className="space-y-2">
                    {selectedReport.manufacturing_feedback.process_improvements.map((item, idx) => (
                      <li key={idx} className="text-sm text-slate-200 flex items-start">
                        <span className="text-blue-500 mr-2">✓</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-green-700 mb-3">Quality Control Updates</h3>
                  <ul className="space-y-2">
                    {selectedReport.manufacturing_feedback.quality_control_updates.map((item, idx) => (
                      <li key={idx} className="text-sm text-slate-200 flex items-start">
                        <span className="text-green-500 mr-2">✓</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-orange-700 mb-3">Supplier Actions</h3>
                  <ul className="space-y-2">
                    {selectedReport.manufacturing_feedback.supplier_actions.map((item, idx) => (
                      <li key={idx} className="text-sm text-slate-200 flex items-start">
                        <span className="text-orange-500 mr-2">✓</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Trend Charts & Impact Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <div className="glass-card rounded-xl shadow-md p-6" role="region" aria-label="Recurring issues trend">
                <h3 className="text-lg font-semibold text-white mb-3">Recurring Defect Frequency by Component</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsBarChart data={reports.map((r) => ({ name: r.component, frequency: r.recurring_pattern.frequency }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="frequency" fill="#6366F1" name="Frequency" />
                    </RechartsBarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="glass-card rounded-xl shadow-md p-6" role="region" aria-label="Vehicles affected trend">
                <h3 className="text-lg font-semibold text-white mb-3">Vehicles Affected Trend</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsLineChart data={reports.map((r, i) => ({ index: i + 1, vehicles: r.vehicles_affected }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="index" tickFormatter={(v) => `#${v}`} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="vehicles" stroke="#10B981" name="Vehicles" />
                    </RechartsLineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Impact Analysis */}
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl shadow-xl p-6">
              <h2 className="text-2xl font-bold mb-6 flex items-center">
                <span className="mr-2">📊</span>
                Impact Analysis & ROI
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                  <div className="text-3xl font-bold mb-1">
                    {selectedReport.impact_analysis.expected_defect_reduction}
                  </div>
                  <div className="text-sm text-purple-100">Defect Reduction</div>
                </div>
                <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                  <div className="text-3xl font-bold mb-1">
                    {selectedReport.impact_analysis.estimated_cost_savings}
                  </div>
                  <div className="text-sm text-purple-100">Cost Savings</div>
                </div>
                <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                  <div className="text-3xl font-bold mb-1">
                    {selectedReport.impact_analysis.implementation_cost}
                  </div>
                  <div className="text-sm text-purple-100">Implementation Cost</div>
                </div>
                <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                  <div className="text-3xl font-bold mb-1">
                    {selectedReport.impact_analysis.roi}
                  </div>
                  <div className="text-sm text-purple-100">Return on Investment</div>
                </div>
                <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                  <div className="text-3xl font-bold mb-1">
                    {selectedReport.impact_analysis.quality_improvement_score}/100
                  </div>
                  <div className="text-sm text-purple-100">Quality Score</div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default RCACAPAReport;
