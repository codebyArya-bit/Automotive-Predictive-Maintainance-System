import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Car,
  Bot,
  Wrench,
  AlertTriangle,
  Play,
  BarChart3,
  Menu,
  X,
  Settings,
  User,
  FileText
} from 'lucide-react';
import NotificationBell from './NotificationBell';
import { useAuth } from '../contexts/AuthContext';
import { agentMonitorPalette } from '../config/theme';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Vehicles', href: '/vehicles', icon: Car },
    { name: 'AI Agents', href: '/agents', icon: Bot },
    { name: 'Maintenance', href: '/maintenance', icon: Wrench },
    { name: 'Alerts', href: '/alerts', icon: AlertTriangle },
    { name: 'Logs', href: '/logs', icon: FileText },
    { name: 'Demo', href: '/demo', icon: Play },
    { name: 'Demo Analytics', href: '/demo-analytics', icon: BarChart3 },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  ];

  const isActive = (href: string) => location.pathname === href;

  return (
    <div className={`flex h-screen ${agentMonitorPalette.page}`}>
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-slate-900/80 backdrop-blur" onClick={() => setSidebarOpen(false)} />
        </div>
      )}

      {/* Sidebar */}
      <aside
        id="sidebar"
        className={`fixed inset-y-0 left-0 z-50 w-64 ${agentMonitorPalette.sidebar} text-slate-100 shadow-2xl shadow-blue-950/40 transform ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-white/10">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <img
                src="/logo.svg"
                alt="AutoMind Logo"
                className="w-10 h-10"
              />
            </div>
            <div className="ml-3">
              <h1 className="text-xl font-bold gradient-title">
                AutoMind
              </h1>
              <p className="text-xs text-slate-300">AI Predictive Maintenance</p>
            </div>
          </div>
          <button
            className="lg:hidden"
            type="button"
            aria-label="Close sidebar"
            aria-controls="sidebar"
            aria-expanded={sidebarOpen}
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-6 h-6 text-slate-400" aria-hidden="true" />
          </button>
        </div>

        <nav className="mt-6 px-3" aria-label="Primary">
          <div className="space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 ${
                    isActive(item.href)
                      ? 'bg-white/10 text-white border border-cyan-400/40 shadow-lg shadow-cyan-900/30'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  }`}
                  aria-current={isActive(item.href) ? 'page' : undefined}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className={`mr-3 h-5 w-5 ${
                    isActive(item.href) ? 'text-cyan-300' : 'text-slate-400 group-hover:text-white'
                  }`} aria-hidden="true" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* System Status */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/10 bg-slate-900/80">
          <div className="flex items-center justify-between text-slate-300">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse shadow shadow-emerald-400/50"></div>
              <span className="ml-2 text-xs text-slate-300">System Online</span>
            </div>
            <div className="flex items-center space-x-2">
              <button className="p-1 text-slate-400 hover:text-white transition-colors">
                <Settings className="w-4 h-4" />
              </button>
              <button className="p-1 text-slate-400 hover:text-white transition-colors">
                <User className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top header */}
        <header className={`${agentMonitorPalette.header} shadow-lg shadow-slate-950/40`} role="banner">
          <div className="flex items-center justify-between h-16 px-6">
            <div className="flex items-center">
              <button
                className="lg:hidden"
                type="button"
                aria-label="Open sidebar"
                aria-controls="sidebar"
                aria-expanded={sidebarOpen}
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="w-6 h-6 text-slate-300" aria-hidden="true" />
              </button>
              <div className="ml-4 lg:ml-0">
                <h2 className="text-lg font-semibold text-white capitalize">
                  {location.pathname.slice(1) || 'Dashboard'}
                </h2>
              </div>
            </div>

            <nav className="flex items-center space-x-4" aria-label="User actions">
              {/* Notifications */}
              <NotificationBell />

              {/* User menu */}
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <div className="text-sm font-semibold text-white">
                    {user?.first_name} {user?.last_name}
                  </div>
                  <div className="text-xs text-slate-300 capitalize">
                    {user?.role ? user.role.replace('_', ' ') : 'Logged in'}
                  </div>
                </div>
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-full flex items-center justify-center shadow-lg shadow-blue-900/40">
                  <User className="w-4 h-4 text-white" aria-hidden="true" />
                </div>
                <button
                  type="button"
                  className="bg-gradient-to-r from-rose-500 to-orange-500 text-white px-4 py-2 rounded-lg shadow-lg shadow-rose-900/30 hover:opacity-90 transition-colors text-sm font-medium focus:outline-none focus:ring-2 focus:ring-rose-300/60"
                  aria-label="Logout"
                  onClick={async () => {
                    try {
                      await logout();
                    } catch (e) {
                      // Ignore logout API failure; proceed to navigation
                    } finally {
                      navigate('/login');
                    }
                  }}
                >
                  Logout
                </button>
              </div>
            </nav>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-transparent">
          <div className="p-6 space-y-6">
            <div className="glow-divider" />
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
