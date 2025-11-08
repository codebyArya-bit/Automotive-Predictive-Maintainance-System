import { useEffect, useRef } from 'react';
import { X, Archive, CheckCircle2 } from 'lucide-react';
import { AppNotification, NotificationCategory } from '../hooks/useNotifications';

interface NotificationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  notifications: AppNotification[];
  categoryFilter: NotificationCategory | 'all';
  setCategoryFilter: (c: NotificationCategory | 'all') => void;
  markAsRead: (id: string) => void;
  dismiss: (id: string) => void;
  archive: (id: string) => void;
  clearAll: () => void;
  unreadCount: number;
}

const categories: { key: NotificationCategory | 'all'; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'system', label: 'System Alerts' },
  { key: 'updates', label: 'Updates' },
  { key: 'user', label: 'Messages' },
];

export default function NotificationPanel(props: NotificationPanelProps) {
  const {
    isOpen,
    onClose,
    notifications,
    categoryFilter,
    setCategoryFilter,
    markAsRead,
    dismiss,
    archive,
    clearAll,
    unreadCount,
  } = props;

  const panelRef = useRef<HTMLDivElement | null>(null);

  // Focus trap and escape key for accessibility
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape' && isOpen) onClose();
    }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (isOpen && panelRef.current) {
      panelRef.current.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50"
      aria-hidden={!isOpen}
      aria-label="Notifications"
      role="dialog"
    >
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-gray-900/40"
        onClick={onClose}
        aria-hidden="true"
      />
      {/* Panel */}
      <div className="absolute right-0 top-0 h-full w-full max-w-md glass-card shadow-xl border-l border-white/10" aria-live="polite">
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-white">Notifications</h3>
            <span className="text-xs text-slate-400" aria-label={`Unread notifications ${unreadCount}`}>
              ({unreadCount} unread)
            </span>
          </div>
          <button className="p-2 rounded hover:glass-card/10" onClick={onClose} aria-label="Close notifications">
            <X className="w-5 h-5 text-slate-300" />
          </button>
        </div>

        {/* Category filters */}
        <div className="flex gap-2 px-4 py-2 border-b border-white/5">
          {categories.map((c) => (
            <button
              key={c.key}
              className={`px-3 py-1 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 ${
                categoryFilter === c.key ? 'bg-primary-50 text-primary-700 border border-primary-200' : 'bg-white/10 text-slate-200'
              }`}
              onClick={() => setCategoryFilter(c.key)}
              aria-pressed={categoryFilter === c.key}
            >
              {c.label}
            </button>
          ))}
          <div className="ml-auto">
            <button
              className="px-3 py-1 rounded text-sm bg-white/10 text-slate-200 hover:glass-card/15 focus:outline-none focus:ring-2 focus:ring-primary-600"
              onClick={clearAll}
            >
              Clear all
            </button>
          </div>
        </div>

        {/* List */}
        <div className="overflow-y-auto" style={{ maxHeight: 'calc(100% - 110px)' }}>
          {notifications.length === 0 ? (
            <div className="p-6 text-center text-slate-400">No notifications</div>
          ) : (
            <ul className="divide-y divide-gray-100" role="list">
              {notifications.map((n) => (
                <li key={n.id} className="px-4 py-3" role="listitem">
                  <div className="flex items-start gap-3">
                    <div className={`mt-1 w-2 h-2 rounded-full ${n.unread ? 'bg-danger-500' : 'bg-gray-300'}`} aria-hidden="true" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-semibold text-white">{n.title}</p>
                        <span className="text-xs text-slate-400" aria-label={`Notified at ${new Date(n.timestamp).toLocaleString()}`}>
                          {new Date(n.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-slate-200 mt-1">{n.message}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs px-2 py-0.5 rounded-full glass-card/10 text-slate-200 capitalize">
                          {n.category}
                        </span>
                        {n.meta?.severity && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-800">
                            {String(n.meta.severity)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-3">
                    <button
                      className="px-2 py-1 text-xs rounded bg-success-50 text-success-700 hover:bg-success-100 flex items-center gap-1 focus:outline-none focus:ring-2 focus:ring-success-600"
                      onClick={() => markAsRead(n.id)}
                      aria-label="Mark as read"
                    >
                      <CheckCircle2 className="w-4 h-4" /> Read
                    </button>
                    <button
                      className="px-2 py-1 text-xs rounded bg-white/10 text-slate-200 hover:glass-card/15 flex items-center gap-1 focus:outline-none focus:ring-2 focus:ring-gray-400"
                      onClick={() => archive(n.id)}
                      aria-label="Archive notification"
                    >
                      <Archive className="w-4 h-4" /> Archive
                    </button>
                    <button
                      className="ml-auto px-2 py-1 text-xs rounded bg-danger-50 text-danger-700 hover:bg-danger-100 focus:outline-none focus:ring-2 focus:ring-danger-600"
                      onClick={() => dismiss(n.id)}
                      aria-label="Dismiss notification"
                    >
                      Dismiss
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}