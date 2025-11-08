import React, { useEffect, useMemo, useState } from 'react';
import config from '../config';
import useWebSocket from '../hooks/useWebSocket';
import { apiService } from '../services/api';
import { badgeVariants } from '../config/theme';
import {
  Activity,
  Filter,
  Pause,
  Play,
  Trash2,
  Download,
  CircleDot,
  AlertTriangle,
  Info,
  Bug,
  Terminal,
} from 'lucide-react';

type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';

interface LogEntry {
  id?: string;
  timestamp: string;
  level: LogLevel;
  message: string;
  source?: string;
  event_type?: string;
  tags?: string[];
  context?: Record<string, any>;
}

interface LogSuggestion {
  id?: string;
  title: string;
  description?: string;
  severity?: 'low' | 'medium' | 'high';
  hint?: string;
}

const levelColors: Record<LogLevel, string> = {
  DEBUG: badgeVariants.neutral,
  INFO: badgeVariants.info,
  WARNING: badgeVariants.warning,
  ERROR: badgeVariants.danger,
  CRITICAL: `${badgeVariants.danger} bg-rose-600/25`,
};

const LogsMonitor: React.FC = () => {
  const wsBase = useMemo(() => {
    const { wsUrl } = config;
    return `${wsUrl.replace(/\/$/, '')}/logs`;
  }, []);

  const { lastMessage, isConnected, connect, disconnect, readyState, error, reconnectCount } = useWebSocket(wsBase, {
    reconnectInterval: 2000,
    maxReconnectAttempts: 50,
  });

  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [suggestions, setSuggestions] = useState<LogSuggestion[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [realtime, setRealtime] = useState(true);
  const [levelFilter, setLevelFilter] = useState<'all' | LogLevel>('all');
  const [sourceFilter, setSourceFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  useEffect(() => {
    (async () => {
      try {
        const s = await apiService.getLogStats(60);
        setStats(s);
      } catch (e) {
        console.warn('Failed to load log stats', e);
      }
      try {
        const sug = await apiService.getLogSuggestions(50);
        setSuggestions(sug?.items || sug || []);
      } catch (e) {
        console.warn('Failed to load suggestions', e);
      }
    })();
  }, []);

  useEffect(() => {
    if (!lastMessage) return;
    try {
      const msg: any = lastMessage;
      // Helper to deduplicate logs by id or a composite key
      const dedupe = (arr: LogEntry[]): LogEntry[] => {
        const seen = new Set<string>();
        const result: LogEntry[] = [];
        for (const l of arr) {
          const key = (l.id && String(l.id)) || [
            String(new Date(l.timestamp).getTime()),
            l.level,
            (l.source || ''),
            (l.event_type || ''),
            (l.message || '')
          ].join('|');
          if (!seen.has(key)) {
            seen.add(key);
            result.push(l);
          }
        }
        // Keep recent 2000 entries
        return result.slice(0, 2000);
      };
      switch (msg.type) {
        case 'log_backfill': {
          const items: LogEntry[] = msg.items || msg.data?.items || [];
          if (Array.isArray(items) && items.length > 0) {
            setLogs((prev) => {
              const merged = [...items, ...prev];
              return dedupe(merged);
            });
          }
          break;
        }
        case 'log_event': {
          const item: LogEntry | undefined = msg.data || msg.log || undefined;
          if (item && realtime) {
            setLogs((prev) => dedupe([item, ...prev]));
          }
          break;
        }
        case 'suggestions': {
          const items: LogSuggestion[] = msg.items || msg.data?.items || [];
          setSuggestions(items);
          break;
        }
        default: {
          // Unknown message type; ignore
        }
      }
    } catch (e) {
      console.warn('Failed processing WS message', e, lastMessage);
    }
  }, [lastMessage, realtime]);

  const filteredLogs = useMemo(() => {
    return logs.filter((l) => {
      const matchLevel = levelFilter === 'all' || l.level === levelFilter;
      const matchSource = sourceFilter === 'all' || (l.source || '').toLowerCase() === sourceFilter.toLowerCase();
      const matchType = typeFilter === 'all' || (l.event_type || '').toLowerCase() === typeFilter.toLowerCase();
      const s = search.trim().toLowerCase();
      const matchSearch = !s ||
        (l.message || '').toLowerCase().includes(s) ||
        (l.tags || []).join(' ').toLowerCase().includes(s) ||
        (l.source || '').toLowerCase().includes(s) ||
        (l.event_type || '').toLowerCase().includes(s);
      return matchLevel && matchSource && matchType && matchSearch;
    });
  }, [logs, levelFilter, sourceFilter, typeFilter, search]);

  const clearLogs = () => setLogs([]);

  const exportCSV = () => {
    const headers = ['timestamp', 'level', 'source', 'event_type', 'message'];
    const rows = filteredLogs.map((l) => [l.timestamp, l.level, l.source || '', l.event_type || '', (l.message || '').replace(/\n/g, ' ') ]);
    const csv = [headers.join(','), ...rows.map((r) => r.map((x) => `"${String(x).replace(/"/g, '"')}"`).join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs_export_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const levelOptions: LogLevel[] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 space-y-8">
      {/* Header */}
      <div className="glass-card/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent flex items-center gap-2">
              <Activity className="w-7 h-7 text-blue-600" />
              Log Monitor
            </h1>
            <p className="text-slate-300">Real-time logs, filters, and actionable suggestions</p>
          </div>
          <div className="flex items-center gap-3">
            <span className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${isConnected ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
              <CircleDot className={`w-4 h-4 ${isConnected ? 'text-green-600' : 'text-yellow-600'}`} />
              {isConnected ? 'Connected' : `Connecting… (${reconnectCount})`}
            </span>
            <button
              className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm ${realtime ? 'bg-blue-600 text-white border-blue-600' : 'glass-card text-slate-200 border-white/20'}`}
              onClick={() => setRealtime((v) => !v)}
            >
              {realtime ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {realtime ? 'Pause' : 'Resume'}
            </button>
            <button
              className="flex items-center gap-2 px-3 py-2 rounded-lg border glass-card text-slate-200 border-white/20 text-sm"
              onClick={clearLogs}
            >
              <Trash2 className="w-4 h-4" />
              Clear
            </button>
            <button
              className="flex items-center gap-2 px-3 py-2 rounded-lg border glass-card text-slate-200 border-white/20 text-sm"
              onClick={exportCSV}
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="glass-card rounded-2xl shadow-md p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
          <span className="flex items-center gap-2 text-slate-200 whitespace-nowrap"><Filter className="w-4 h-4" /> Filters</span>
          <select
            className="input-field w-full sm:w-40"
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value as any)}
          >
            <option value="all">All levels</option>
            {levelOptions.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
          <input
            placeholder="Source (api, agent, system)"
            className="input-field w-full sm:w-48"
            value={sourceFilter === 'all' ? '' : sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value || 'all')}
          />
          <input
            placeholder="Type (websocket, metrics, maintenance)"
            className="input-field w-full sm:w-52"
            value={typeFilter === 'all' ? '' : typeFilter}
            onChange={(e) => setTypeFilter(e.target.value || 'all')}
          />
          <input
            placeholder="Search text"
            className="input-field flex-1"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Stats + Suggestions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-card rounded-2xl shadow-md p-4 border border-white/10">
          <div className="flex items-center justify-between mb-3">
            <div className="text-lg font-semibold text-white flex items-center gap-2">
              <Terminal className="w-5 h-5" />
              Recent Logs ({filteredLogs.length})
            </div>
            <div className="text-xs text-slate-400">WS readyState: {readyState}</div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-slate-400">
                  <th className="px-3 py-2">Time</th>
                  <th className="px-3 py-2">Level</th>
                  <th className="px-3 py-2">Source</th>
                  <th className="px-3 py-2">Type</th>
                  <th className="px-3 py-2">Message</th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.map((l, idx) => (
                  <tr key={(l.id || '') + idx} className="border-t border-white/5 hover:bg-white/5 transition-colors">
                    <td className="px-3 py-2 whitespace-nowrap text-slate-300">{new Date(l.timestamp).toLocaleString()}</td>
                    <td className="px-3 py-2 whitespace-nowrap">
                      <span className={`status-indicator ${levelColors[l.level]}`}>{l.level}</span>
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-slate-200">{l.source || '-'}</td>
                    <td className="px-3 py-2 whitespace-nowrap text-slate-200">{l.event_type || '-'}</td>
                    <td className="px-3 py-2 text-white">
                      <div className="max-w-xl truncate" title={l.message}>{l.message}</div>
                    </td>
                  </tr>
                ))}
                {filteredLogs.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-3 py-6 text-center text-slate-400">No logs match current filters.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-card rounded-2xl shadow-md p-4 space-y-4 border border-white/10">
          <div className="text-lg font-semibold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Suggestions
          </div>
          <div className="space-y-2">
            {suggestions?.length > 0 ? suggestions.map((s, idx) => (
              <div key={(s.id || '') + idx} className="glass-panel border border-white/10 rounded-xl p-3 hover:border-cyan-400/30 transition-colors">
                <div className="font-medium text-white">{s.title}</div>
                {s.description && <div className="text-xs text-slate-300 mt-1">{s.description}</div>}
                {s.hint && <div className="text-xs text-slate-400 mt-1">Hint: {s.hint}</div>}
              </div>
            )) : (
              <div className="text-sm text-slate-400">No suggestions available.</div>
            )}
          </div>

          <div className="pt-2 border-t border-white/10">
            <div className="text-lg font-semibold text-white flex items-center gap-2">
              <Info className="w-5 h-5" />
              Stats (last 60m)
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div className="glass-panel rounded-lg p-3 text-sm border border-white/10">
                <div className="text-slate-400">Total</div>
                <div className="text-xl font-semibold text-white">{stats?.total || logs.length}</div>
              </div>
              <div className="glass-panel rounded-lg p-3 text-sm border border-white/10">
                <div className="text-slate-400">Errors</div>
                <div className="text-xl font-semibold text-rose-300">{stats?.errors || logs.filter(l => l.level === 'ERROR' || l.level === 'CRITICAL').length}</div>
              </div>
              <div className="glass-panel rounded-lg p-3 text-sm border border-white/10">
                <div className="text-slate-400">Warnings</div>
                <div className="text-xl font-semibold text-amber-300">{stats?.warnings || logs.filter(l => l.level === 'WARNING').length}</div>
              </div>
              <div className="glass-panel rounded-lg p-3 text-sm border border-white/10">
                <div className="text-slate-400">Info</div>
                <div className="text-xl font-semibold text-cyan-300">{stats?.infos || logs.filter(l => l.level === 'INFO').length}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="status-indicator status-offline w-full justify-center text-sm">
          WebSocket error: {String(error)}
        </div>
      )}
    </div>
  );
};

export default LogsMonitor;

