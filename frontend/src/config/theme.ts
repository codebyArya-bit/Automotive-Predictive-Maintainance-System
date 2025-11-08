export const agentMonitorPalette = {
  page: 'bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-slate-100',
  sidebar: 'bg-slate-900/80 backdrop-blur-2xl border-r border-white/10',
  header: 'bg-slate-900/70 backdrop-blur-xl border-b border-white/10',
  glassCard: 'glass-card',
  glassPanel: 'glass-panel',
  accentBorder: 'border border-white/10',
  neonText: 'gradient-title',
  divider: 'glow-divider',
};

const accentGradients = [
  'from-sky-400 via-cyan-300 to-emerald-300',
  'from-indigo-400 via-purple-400 to-pink-400',
  'from-amber-400 via-orange-400 to-rose-400',
  'from-violet-400 via-fuchsia-400 to-blue-400',
];

export const getAccentGradient = (index: number = 0): string => {
  const safeIndex = Math.abs(index) % accentGradients.length;
  return `bg-gradient-to-r ${accentGradients[safeIndex]}`;
};

export const statusTokens: Record<string, string> = {
  healthy: 'text-emerald-200 bg-emerald-500/10 border border-emerald-400/30',
  warning: 'text-amber-200 bg-amber-500/10 border border-amber-400/30',
  critical: 'text-rose-200 bg-rose-500/10 border border-rose-400/30',
  default: 'text-slate-200 bg-white/5 border border-white/10',
};

export const getStatusToken = (status?: string): string => {
  if (!status) return statusTokens.default;
  const key = status.toLowerCase();
  return statusTokens[key] || statusTokens.default;
};

export const chipStyles = {
  outline: 'px-3 py-1 rounded-full border border-white/20 text-xs tracking-wide uppercase text-slate-200',
  solid: 'px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-blue-500 to-cyan-400 text-white shadow-lg shadow-blue-900/40',
};

export const surfaceRing = 'ring-1 ring-white/10';

export const badgeVariants = {
  neutral: 'text-slate-200 bg-white/5 border border-white/10',
  info: 'text-cyan-200 bg-cyan-500/15 border border-cyan-400/30 shadow shadow-cyan-500/10',
  success: 'text-emerald-200 bg-emerald-500/15 border border-emerald-400/30 shadow shadow-emerald-500/10',
  warning: 'text-amber-200 bg-amber-500/15 border border-amber-400/30 shadow shadow-amber-500/10',
  danger: 'text-rose-200 bg-rose-500/20 border border-rose-400/30 shadow shadow-rose-500/10',
  accent: 'text-blue-200 bg-blue-500/15 border border-blue-400/30 shadow shadow-blue-500/10',
} as const;

export type BadgeVariant = keyof typeof badgeVariants;

export const getBadgeVariant = (variant?: BadgeVariant): string => {
  if (!variant) {
    return badgeVariants.neutral;
  }
  return badgeVariants[variant] || badgeVariants.neutral;
};

export const hoverCardSurface =
  'group relative overflow-hidden glass-card rounded-2xl border border-white/10 transition-all duration-300 hover:-translate-y-1 hover:border-cyan-400/40 shadow-lg shadow-slate-950/40 hover:shadow-cyan-500/30';

export const hoverCardGlow =
  'pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-r from-cyan-500/20 via-blue-500/10 to-transparent blur-2xl';

export const darkChartTheme = {
  axis: '#cbd5f5',
  grid: 'rgba(148, 163, 184, 0.2)',
  tooltipBg: 'rgba(2, 6, 23, 0.95)',
  tooltipBorder: 'rgba(59, 130, 246, 0.35)',
  tooltipText: '#e2e8f0',
  legendText: '#e2e8f0',
  palette: ['#38bdf8', '#a855f7', '#22d3ee', '#f472b6', '#f97316', '#34d399'],
} as const;
