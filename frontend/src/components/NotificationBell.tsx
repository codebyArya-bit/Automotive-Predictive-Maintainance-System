import { useState } from 'react';
import { Bell } from 'lucide-react';
import useNotifications from '../hooks/useNotifications';
import NotificationPanel from './NotificationPanel';

interface NotificationBellProps {
  wsBaseUrl?: string;
}

export default function NotificationBell({ wsBaseUrl }: NotificationBellProps) {
  const [open, setOpen] = useState(false);
  const {
    unreadCount,
    visibleNotifications,
    categoryFilter,
    setCategoryFilter,
    markAsRead,
    dismiss,
    archive,
    clearAll,
  } = useNotifications({ wsBaseUrl });

  return (
    <div className="relative">
      <button
        className="relative p-2 text-slate-400 hover:text-slate-300 focus:outline-none focus:ring-2 focus:ring-primary-600"
        onClick={() => setOpen(true)}
        aria-label={`Open notifications, ${unreadCount} unread`}
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span
            className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-danger-600 text-white rounded-full text-xs flex items-center justify-center"
            aria-label={`${unreadCount} unread notifications`}
          >
            {unreadCount}
          </span>
        )}
      </button>

      <NotificationPanel
        isOpen={open}
        onClose={() => setOpen(false)}
        notifications={visibleNotifications}
        categoryFilter={categoryFilter}
        setCategoryFilter={setCategoryFilter}
        markAsRead={markAsRead}
        dismiss={dismiss}
        archive={archive}
        clearAll={clearAll}
        unreadCount={unreadCount}
      />
    </div>
  );
}