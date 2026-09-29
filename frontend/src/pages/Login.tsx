import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, getRoleBasedRoute } from '../contexts/AuthContext';

interface DemoUser {
  email: string;
  password: string;
  role: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

const DEMO_USERS: DemoUser[] = [
  {
    email: 'rajesh@demo.com',
    password: 'demo123',
    role: 'customer',
    name: 'Rajesh Kumar',
    description: 'View your vehicles, alerts, and appointments',
    icon: '🚗',
    color: 'from-blue-500 to-blue-700'
  },
  {
    email: 'priya@demo.com',
    password: 'demo123',
    role: 'service_staff',
    name: 'Priya Sharma',
    description: 'Manage service appointments and workload',
    icon: '🔧',
    color: 'from-green-500 to-green-700'
  },
  {
    email: 'amit@demo.com',
    password: 'demo123',
    role: 'manufacturing_engineer',
    name: 'Amit Patel',
    description: 'Analyze RCA/CAPA reports and quality metrics',
    icon: '⚙️',
    color: 'from-orange-500 to-orange-700'
  },
  {
    email: 'sarah@demo.com',
    password: 'demo123',
    role: 'system_admin',
    name: 'Sarah Johnson',
    description: 'Full system access and monitoring',
    icon: '👨‍💼',
    color: 'from-purple-500 to-purple-700'
  }
];

const Login: React.FC = () => {
  const [loadingUserEmail, setLoadingUserEmail] = useState<string | null>(null);
  const [customLoading, setCustomLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [customEmail, setCustomEmail] = useState('');
  const [customPassword, setCustomPassword] = useState('');
  const [showCustomLogin, setShowCustomLogin] = useState(false);
  const [selectedDemoUser, setSelectedDemoUser] = useState<DemoUser | null>(null);
  const [demoEmail, setDemoEmail] = useState('');
  const [demoPassword, setDemoPassword] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const openDemoLogin = (user: DemoUser) => {
    setSelectedDemoUser(user);
    setDemoEmail(user.email);
    setDemoPassword(user.password);
    setError(null);
  };

  const closeDemoLogin = () => {
    if (loadingUserEmail) return;
    setSelectedDemoUser(null);
    setDemoEmail('');
    setDemoPassword('');
  };

  const handleDemoLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDemoUser) return;

    try {
      setLoadingUserEmail(selectedDemoUser.email);
      setError(null);

      await login(demoEmail, demoPassword);

      // Route using the authenticated user's actual role.
      const userStr = localStorage.getItem('user');
      const authenticatedUser = userStr ? JSON.parse(userStr) : null;
      const route = getRoleBasedRoute(authenticatedUser?.role || selectedDemoUser.role);
      setSelectedDemoUser(null);
      navigate(route);
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoadingUserEmail(null);
    }
  };

  const handleCustomLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!customEmail || !customPassword) {
      setError('Please enter both email and password');
      return;
    }

    try {
      setCustomLoading(true);
      setError(null);

      await login(customEmail, customPassword);

      // Get user role from localStorage and navigate
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        const route = getRoleBasedRoute(user.role);
        navigate(route);
      }
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
      console.error('Login error:', err);
    } finally {
      setCustomLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-6xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 flex items-center justify-center">
            <img src="/logo.svg" alt="AutoMind AI" className="h-12 w-12 mr-3" />
            <span className="gradient-title">AutoMind AI</span>
          </h1>
          <p className="text-xl text-slate-300 mb-2">
            Predictive Automotive Service Platform
          </p>
          <div className="mt-4 inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border border-cyan-400/30 rounded-full">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse mr-2"></div>
            <span className="text-sm text-slate-200">System Online</span>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 glass-card bg-rose-500/20 border-rose-400/30 text-rose-200 px-4 py-3 rounded-lg text-center">
            <p className="font-medium">{error}</p>
          </div>
        )}

        {!showCustomLogin ? (
          <>
            {/* Demo User Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {DEMO_USERS.map((user) => (
                <div
                  key={user.email}
                  className="glass-card rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 hover:scale-105 overflow-hidden border border-white/20 group"
                >
                  <div className={`bg-gradient-to-br ${user.color} p-8 text-white relative overflow-hidden`}>
                    <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
                    <div className="text-6xl mb-4 text-center relative z-10 drop-shadow-lg">{user.icon}</div>
                    <h3 className="text-xl font-bold text-center relative z-10">{user.name}</h3>
                  </div>

                  <div className="p-6 bg-white/5 backdrop-blur-xl">
                    <p className="text-cyan-300 text-sm mb-1 capitalize font-semibold">
                      {user.role.replace('_', ' ')}
                    </p>
                    <p className="text-slate-200 text-xs font-mono mb-2 break-all">
                      {user.email}
                    </p>
                    <p className="text-slate-300 text-xs mb-6 min-h-[40px]">
                      {user.description}
                    </p>

                    <button
                      type="button"
                      onClick={() => openDemoLogin(user)}
                      className={`w-full bg-gradient-to-r ${user.color} text-white py-3 px-4 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-900/50 transition-all duration-300 transform hover:-translate-y-0.5`}
                    >
                      Quick Login
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Toggle to Custom Login */}
            <div className="text-center">
              <button
                onClick={() => setShowCustomLogin(true)}
                className="text-cyan-300 hover:text-white font-medium transition-colors duration-200 px-6 py-3 rounded-lg border border-white/10 hover:border-cyan-300/50 bg-white/5 hover:bg-white/10"
              >
                Or login with custom credentials
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Custom Login Form */}
            <div className="max-w-md mx-auto glass-card rounded-2xl shadow-2xl p-8 border border-white/20">
              <h2 className="text-3xl font-bold mb-6 text-center">
                <span className="gradient-title">Custom Login</span>
              </h2>

              <form onSubmit={handleCustomLogin} className="space-y-5">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-slate-200 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={customEmail}
                    onChange={(e) => setCustomEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white placeholder-slate-400 transition-all duration-200"
                    placeholder="Enter your email"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-slate-200 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    id="password"
                    value={customPassword}
                    onChange={(e) => setCustomPassword(e.target.value)}
                    className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white placeholder-slate-400 transition-all duration-200"
                    placeholder="Enter your password"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={customLoading}
                  className="w-full btn-primary mt-6"
                >
                  {customLoading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Logging in...
                    </span>
                  ) : 'Login'}
                </button>
              </form>

              <button
                onClick={() => setShowCustomLogin(false)}
                className="w-full mt-4 text-slate-300 hover:text-white font-medium py-3 rounded-lg border border-white/10 hover:border-white/20 bg-white/5 hover:bg-white/10 transition-all duration-200"
              >
                Back to demo users
              </button>
            </div>
          </>
        )}

        {/* Demo Quick Login Dialog */}
        {selectedDemoUser && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm"
            role="dialog"
            aria-modal="true"
            aria-labelledby="demo-login-title"
            onMouseDown={(e) => {
              if (e.target === e.currentTarget) closeDemoLogin();
            }}
          >
            <div className="w-full max-w-md glass-card rounded-2xl border border-cyan-400/30 shadow-2xl p-6">
              <div className="flex items-start justify-between gap-4 mb-5">
                <div>
                  <p className="text-sm font-semibold text-cyan-300 capitalize">
                    {selectedDemoUser.role.replace('_', ' ')}
                  </p>
                  <h2 id="demo-login-title" className="text-2xl font-bold text-white mt-1">
                    Login as {selectedDemoUser.name}
                  </h2>
                  <p className="text-sm text-slate-300 mt-2">
                    Demo credentials are autofilled. Review them and continue.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={closeDemoLogin}
                  disabled={loadingUserEmail !== null}
                  className="text-slate-400 hover:text-white text-2xl leading-none disabled:opacity-40"
                  aria-label="Close demo login"
                >
                  ×
                </button>
              </div>

              <form onSubmit={handleDemoLogin} className="space-y-4">
                <div>
                  <label htmlFor="demo-email" className="block text-sm font-medium text-slate-200 mb-2">
                    Email
                  </label>
                  <input
                    id="demo-email"
                    type="email"
                    value={demoEmail}
                    onChange={(e) => setDemoEmail(e.target.value)}
                    autoComplete="username"
                    className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="demo-password" className="block text-sm font-medium text-slate-200 mb-2">
                    Password
                  </label>
                  <input
                    id="demo-password"
                    type="text"
                    value={demoPassword}
                    onChange={(e) => setDemoPassword(e.target.value)}
                    autoComplete="current-password"
                    className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-xl focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white font-mono"
                    required
                  />
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={closeDemoLogin}
                    disabled={loadingUserEmail !== null}
                    className="flex-1 py-3 rounded-xl border border-white/15 bg-white/5 text-slate-200 hover:bg-white/10 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loadingUserEmail !== null}
                    className={`flex-1 bg-gradient-to-r ${selectedDemoUser.color} text-white py-3 px-4 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {loadingUserEmail === selectedDemoUser.email ? (
                      <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Logging in...
                      </span>
                    ) : 'Continue'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Demo Credentials Info */}
        <div className="mt-8 glass-card rounded-2xl shadow-xl p-6 max-w-2xl mx-auto border border-cyan-400/20">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
            <span className="mr-2">ℹ️</span>
            Demo Credentials
          </h3>
          <div className="text-sm text-slate-300 space-y-1">
            <p><strong className="text-cyan-300">Password for all demo users:</strong> <code>demo123</code></p>
            <p><strong className="text-cyan-300">Demo emails:</strong> rajesh@demo.com, priya@demo.com, amit@demo.com, sarah@demo.com</p>
            <p className="text-xs text-slate-400 mt-2">
              Use Quick Login or enter any demo email with the shared password. Logout is safe even after token expiry.
            </p>
          </div>
        </div>

        {/* Features Banner */}
        <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="glass-panel rounded-xl shadow-lg p-4 border border-white/10 hover:border-cyan-400/30 transition-all duration-300 hover:scale-105">
            <div className="text-3xl mb-2">📞</div>
            <p className="text-xs text-slate-300 font-medium">AI Voice Agent</p>
          </div>
          <div className="glass-panel rounded-xl shadow-lg p-4 border border-white/10 hover:border-cyan-400/30 transition-all duration-300 hover:scale-105">
            <div className="text-3xl mb-2">📊</div>
            <p className="text-xs text-slate-300 font-medium">Demand Forecasting</p>
          </div>
          <div className="glass-panel rounded-xl shadow-lg p-4 border border-white/10 hover:border-cyan-400/30 transition-all duration-300 hover:scale-105">
            <div className="text-3xl mb-2">🔍</div>
            <p className="text-xs text-slate-300 font-medium">RCA/CAPA Analysis</p>
          </div>
          <div className="glass-panel rounded-xl shadow-lg p-4 border border-white/10 hover:border-cyan-400/30 transition-all duration-300 hover:scale-105">
            <div className="text-3xl mb-2">🔒</div>
            <p className="text-xs text-slate-300 font-medium">UEBA Security</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
