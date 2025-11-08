import { useEffect, useMemo, useRef, useState } from 'react';
import useWebSocket from './useWebSocket';

export type NotificationCategory = 'system' | 'user' | 'updates';

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  category: NotificationCategory;
  timestamp: string; // ISO string
  unread: boolean;
  archived?: boolean;
  meta?: Record<string, any>;
}

const STORAGE_KEY = 'app_notifications_v1';

function readStored(): AppNotification[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed as AppNotification[];
    return [];
  } catch {
    return [];
  }
}

function writeStored(notifs: AppNotification[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(notifs));
  } catch {
    // Silently ignore localStorage errors (e.g., quota exceeded, private browsing)
  }
}

interface UseNotificationsOptions {
  wsBaseUrl?: string; // e.g., ws://localhost:8000
}

export default function useNotifications(options?: UseNotificationsOptions) {
  const [notifications, setNotifications] = useState<AppNotification[]>(() => readStored());
  const [categoryFilter, setCategoryFilter] = useState<NotificationCategory | 'all'>('all');
  const [error, setError] = useState<string | null>(null);
  const lastPersistRef = useRef<number>(Date.now());

  const wsUrl = useMemo(() => {
    const rawWsBase: string | undefined = options?.wsBaseUrl || (import.meta as any)?.env?.VITE_WS_URL;
    const apiBase: string = (import.meta as any)?.env?.VITE_API_BASE_URL || 'http://localhost:8000';

    // Derive WS base from API base if VITE_WS_URL not set
    const derivedWsBase = apiBase
      .replace(/^http:\/\//, 'ws://')
      .replace(/^https:\/\//, 'wss://');

    const base = rawWsBase || derivedWsBase;

    // Normalize to include single /ws segment
    const wsBase = base.endsWith('/ws')
      ? base
      : base.endsWith('/')
        ? `${base}ws`
        : `${base}/ws`;

    // Listen to dashboard stream as a general system feed
    return `${wsBase}/dashboard`;
  }, [options?.wsBaseUrl]);

  const { isConnected, lastMessage, error: wsError } = useWebSocket(wsUrl, {
    reconnectInterval: 3000,
    maxReconnectAttempts: 50,
    onError: (e: any) => setError(e?.message || 'WebSocket error'),
  });

  // Auto-connect is handled inside useWebSocket; no manual connect here

  // Persist to localStorage (throttled)
  useEffect(() => {
    const now = Date.now();
    if (now - lastPersistRef.current > 500) {
      writeStored(notifications);
      lastPersistRef.current = now;
    }
  }, [notifications]);

  // Hydrate with recent alerts from API on first mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { default: apiService } = await import('../services/api');
        const alerts = await apiService.getRecentAlerts?.();
        if (alerts && Array.isArray(alerts)) {
          const mapped: AppNotification[] = alerts.map((a: any, idx: number) => ({
            id: a.id || `alert_${Date.now()}_${idx}`,
            title: a.title || a.type || 'Alert',
            message: a.description || a.details || a.message || 'New alert',
            category: 'system',
            timestamp: a.timestamp || new Date().toISOString(),
            unread: true,
            meta: { severity: a.severity, vehicleId: a.vehicle_id },
          }));
          if (!cancelled) {
            setNotifications((prev) => {
              // Avoid duplicates by id
              const existingIds = new Set(prev.map((p) => p.id));
              const merged = [...mapped.filter((m) => !existingIds.has(m.id)), ...prev];
              return merged.sort((a, b) => +new Date(b.timestamp) - +new Date(a.timestamp));
            });
          }
        }
      } catch (e: any) {
        // Silent fail — API may not be available yet
      }
    })();
    return () => { cancelled = true; };
  }, []);

  // Handle websocket messages to create notifications
  useEffect(() => {
    if (!lastMessage) return;
    try {
      const data: any = lastMessage;
      // Normalize different possible shapes
      const type = data.type || data.event || 'dashboard_update';

      if (type === 'dashboard_update') {
        const alertsCount = data.alerts_count ?? data.alertsCount;
        const systemHealth = data.system_health ?? data.systemHealth;
        const ts = data.timestamp || new Date().toISOString();
        if (typeof alertsCount === 'number') {
          const notif: AppNotification = {
            id: `alerts_${ts}`,
            title: 'Alerts Updated',
            message: `There are now ${alertsCount} active alerts on the dashboard`,
            category: 'updates',
            timestamp: ts,
            unread: true,
            meta: { alertsCount },
          };
          setNotifications((prev) => [notif, ...prev].slice(0, 500));
        }
        if (systemHealth) {
          const notif: AppNotification = {
            id: `health_${ts}`,
            title: 'System Health Update',
            message: `System health is ${systemHealth}`,
            category: 'system',
            timestamp: ts,
            unread: true,
            meta: { systemHealth },
          };
          setNotifications((prev) => [notif, ...prev].slice(0, 500));
        }
      } else if (type === 'alert' || type === 'task_update') {
        const ts = data.timestamp || new Date().toISOString();
        const notif: AppNotification = {
          id: `${type}_${ts}_${Math.random().toString(36).slice(2)}`,
          title: data.title || (type === 'alert' ? 'New Alert' : 'Task Update'),
          message: data.message || data.description || 'Update received',
          category: 'system',
          timestamp: ts,
          unread: true,
          meta: { severity: data.severity, details: data.details },
        };
        setNotifications((prev) => [notif, ...prev].slice(0, 500));
      } else if (type === 'user_message') {
        const ts = data.timestamp || new Date().toISOString();
        const notif: AppNotification = {
          id: `${type}_${ts}_${Math.random().toString(36).slice(2)}`,
          title: data.title || 'New Message',
          message: data.message || 'You have a new message',
          category: 'user',
          timestamp: ts,
          unread: true,
          meta: { from: data.from },
        };
        setNotifications((prev) => [notif, ...prev].slice(0, 500));
      }
    } catch (e) {
      // Ignore parse errors
    }
  }, [lastMessage]);

  const unreadCount = useMemo(() => notifications.filter((n) => n.unread && !n.archived).length, [notifications]);

  const visibleNotifications = useMemo(() => {
    const list = notifications.filter((n) => !n.archived);
    if (categoryFilter === 'all') return list;
    return list.filter((n) => n.category === categoryFilter);
  }, [notifications, categoryFilter]);

  const markAsRead = (id: string) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, unread: false } : n)));
  };

  const dismiss = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const archive = (id: string) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, archived: true, unread: false } : n)));
  };

  const clearAll = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, archived: true, unread: false })));
  };

  return {
    isConnected,
    wsError,
    error,
    notifications,
    unreadCount,
    visibleNotifications,
    categoryFilter,
    setCategoryFilter,
    markAsRead,
    dismiss,
    archive,
    clearAll,
  };
}
