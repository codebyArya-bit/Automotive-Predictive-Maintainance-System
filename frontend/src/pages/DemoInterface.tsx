import React, { useState, useEffect, useRef } from 'react';
import {
  Play,
  Pause,
  Square,
  RotateCcw,
  Settings,
  Car,
  Activity,
  Zap,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  Gauge,
  Maximize,
  Minimize,
  Volume2,
  VolumeX,
  Eye,
  EyeOff,
  Presentation,
  Target,
  TrendingUp,
  Shield,
  Cpu,
  Sparkles,
  Rocket,
  BarChart3
} from 'lucide-react';
import { apiService } from '../services/api';
import { Vehicle, Agent } from '../types';

interface DemoScenario {
  id: string;
  name: string;
  description: string;
  duration: number;
  vehicles: number;
  events: string[];
  keyPoints: string[];
  expectedOutcomes: string[];
  icon: any;
  gradient: string;
}

interface DemoEvent {
  id: string;
  timestamp: number;
  type: 'alert' | 'decision' | 'optimization' | 'maintenance' | 'emergency';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  vehicleId?: string;
  agentId?: string;
}

const DemoInterface: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentScenario, setCurrentScenario] = useState<DemoScenario | null>(null);
  const [progress, setProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showNotes, setShowNotes] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const [demoEvents, setDemoEvents] = useState<DemoEvent[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const [liveMetrics, setLiveMetrics] = useState({
    totalVehicles: 0,
    activeAgents: 0,
    alertsGenerated: 0,
    decisionsPerSecond: 0,
    avgResponseTime: 0,
    systemLoad: 0,
    dataProcessed: 0,
    aiAccuracy: 0,
    fuelSaved: 0,
    emissionsReduced: 0
  });

  const demoScenarios: DemoScenario[] = [
    {
      id: 'fleet-monitoring',
      name: 'Fleet Monitoring',
      description: 'Demonstrate real-time fleet monitoring with live telemetry data',
      duration: 300,
      vehicles: 25,
      events: ['Vehicle tracking', 'Telemetry updates', 'Status changes', 'Route optimization'],
      keyPoints: [
        'Real-time vehicle location tracking',
        'Live telemetry data streaming',
        'Automated status monitoring',
        'Performance analytics dashboard'
      ],
      expectedOutcomes: [
        '100% vehicle visibility',
        '< 2s response time',
        '95% uptime monitoring',
        'Real-time alerts'
      ],
      icon: Car,
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'predictive-maintenance',
      name: 'Predictive Maintenance',
      description: 'Show AI-powered predictive maintenance alerts and recommendations',
      duration: 240,
      vehicles: 15,
      events: ['Maintenance predictions', 'Component analysis', 'Alert generation', 'Scheduling'],
      keyPoints: [
        'AI-powered failure prediction',
        'Component health analysis',
        'Automated maintenance scheduling',
        'Cost optimization algorithms'
      ],
      expectedOutcomes: [
        '30% reduction in breakdowns',
        '25% cost savings',
        '90% prediction accuracy',
        'Optimized maintenance schedules'
      ],
      icon: Settings,
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      id: 'emergency-response',
      name: 'Emergency Response',
      description: 'Simulate emergency scenarios and automated response protocols',
      duration: 180,
      vehicles: 10,
      events: ['Emergency detection', 'Alert dispatch', 'Route rerouting', 'Response coordination'],
      keyPoints: [
        'Instant emergency detection',
        'Automated alert systems',
        'Dynamic route rerouting',
        'Multi-agency coordination'
      ],
      expectedOutcomes: [
        '< 30s emergency response',
        '100% alert delivery',
        'Optimized emergency routes',
        'Coordinated response teams'
      ],
      icon: Shield,
      gradient: 'from-red-500 to-orange-500'
    },
    {
      id: 'optimization',
      name: 'Route Optimization',
      description: 'Demonstrate AI-driven route optimization and fuel efficiency',
      duration: 360,
      vehicles: 30,
      events: ['Route analysis', 'Traffic optimization', 'Fuel calculations', 'Performance metrics'],
      keyPoints: [
        'Real-time traffic analysis',
        'Dynamic route optimization',
        'Fuel efficiency calculations',
        'Environmental impact tracking'
      ],
      expectedOutcomes: [
        '20% fuel savings',
        '15% time reduction',
        '25% emission reduction',
        'Optimized delivery schedules'
      ],
      icon: TrendingUp,
      gradient: 'from-green-500 to-emerald-500'
    }
  ];

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isRunning && !isPaused && currentScenario) {
      interval = setInterval(() => {
        setElapsedTime(prev => {
          const newTime = prev + 1;
          const newProgress = (newTime / currentScenario.duration) * 100;
          setProgress(newProgress);

          triggerDemoEvents(newProgress);

          if (newTime >= currentScenario.duration) {
            handleStop();
            return 0;
          }

          return newTime;
        });

        updateLiveMetrics();
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning, isPaused, currentScenario]);

  useEffect(() => {
    fetchDemoData();
    setupWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const setupWebSocket = () => {
    try {
      wsRef.current = new WebSocket('ws://localhost:8000/ws/demo');

      wsRef.current.onopen = () => {
        setIsConnected(true);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'demo_event') {
            addDemoEvent(data.event);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onerror = () => setIsConnected(false);
      wsRef.current.onclose = () => setIsConnected(false);
    } catch (error) {
      setIsConnected(false);
    }
  };

  const fetchDemoData = async () => {
    try {
      const [vehiclesResponse, agentsResponse] = await Promise.all([
        apiService.getVehicles({ limit: 50 }),
        apiService.getAgents()
      ]);

      setVehicles(vehiclesResponse.items || []);
      setAgents(agentsResponse || []);
    } catch (error) {
      console.error('Failed to fetch demo data:', error);
    }
  };

  const triggerDemoEvents = (_progress: number) => {
    if (!currentScenario) return;

    const eventTypes: DemoEvent['type'][] = ['alert', 'decision', 'optimization', 'maintenance'];
    const randomType = eventTypes[Math.floor(Math.random() * eventTypes.length)];

    if (Math.random() < 0.3) {
      const event: DemoEvent = {
        id: `event_${Date.now()}`,
        timestamp: Date.now(),
        type: randomType,
        title: generateEventTitle(randomType),
        description: generateEventDescription(randomType),
        severity: Math.random() < 0.2 ? 'high' : Math.random() < 0.5 ? 'medium' : 'low',
        vehicleId: vehicles[Math.floor(Math.random() * vehicles.length)]?.id,
        agentId: agents[Math.floor(Math.random() * agents.length)]?.id
      };

      addDemoEvent(event);

      if (soundEnabled) {
        playNotificationSound(event.severity);
      }
    }
  };

  const generateEventTitle = (type: DemoEvent['type']): string => {
    const titles = {
      alert: ['Engine Temperature Alert', 'Low Fuel Warning', 'Maintenance Required', 'Speed Limit Exceeded'],
      decision: ['Route Optimization', 'Traffic Rerouting', 'Fuel Stop Recommended', 'Rest Break Suggested'],
      optimization: ['Route Optimized', 'Fuel Efficiency Improved', 'Delivery Time Reduced', 'Cost Savings Achieved'],
      maintenance: ['Brake Inspection Due', 'Oil Change Scheduled', 'Tire Rotation Needed', 'Battery Check Required'],
      emergency: ['Emergency Detected', 'Accident Alert', 'Medical Emergency', 'Vehicle Breakdown']
    };

    const typeTitle = titles[type] || titles.alert;
    return typeTitle[Math.floor(Math.random() * typeTitle.length)];
  };

  const generateEventDescription = (type: DemoEvent['type']): string => {
    const descriptions = {
      alert: 'System detected anomaly requiring attention',
      decision: 'AI agent made optimization decision',
      optimization: 'Performance improvement achieved',
      maintenance: 'Preventive maintenance scheduled',
      emergency: 'Emergency situation detected and handled'
    };

    return descriptions[type] || descriptions.alert;
  };

  const addDemoEvent = (event: DemoEvent) => {
    setDemoEvents(prev => [event, ...prev.slice(0, 19)]);
  };

  const playNotificationSound = (_severity: string) => {
    if (audioRef.current) {
      audioRef.current.play().catch(() => {});
    }
  };

  const updateLiveMetrics = () => {
    if (!currentScenario) return;

    setLiveMetrics(prev => ({
      totalVehicles: currentScenario.vehicles + Math.floor(Math.random() * 5),
      activeAgents: Math.floor(Math.random() * 8) + 5,
      alertsGenerated: prev.alertsGenerated + Math.floor(Math.random() * 3),
      decisionsPerSecond: Math.floor(Math.random() * 50) + 20,
      avgResponseTime: Math.floor(Math.random() * 100) + 50,
      systemLoad: Math.floor(Math.random() * 30) + 40,
      dataProcessed: prev.dataProcessed + Math.floor(Math.random() * 1000) + 500,
      aiAccuracy: 92 + Math.random() * 6,
      fuelSaved: prev.fuelSaved + Math.random() * 10,
      emissionsReduced: prev.emissionsReduced + Math.random() * 5
    }));
  };

  const handleStart = (scenario: DemoScenario) => {
    setCurrentScenario(scenario);
    setIsRunning(true);
    setIsPaused(false);
    setProgress(0);
    setElapsedTime(0);
    setDemoEvents([]);
    setLiveMetrics({
      totalVehicles: scenario.vehicles,
      activeAgents: 0,
      alertsGenerated: 0,
      decisionsPerSecond: 0,
      avgResponseTime: 0,
      systemLoad: 0,
      dataProcessed: 0,
      aiAccuracy: 0,
      fuelSaved: 0,
      emissionsReduced: 0
    });
  };

  const handlePause = () => setIsPaused(!isPaused);
  const handleStop = () => {
    setIsRunning(false);
    setIsPaused(false);
    setProgress(0);
    setElapsedTime(0);
    setCurrentScenario(null);
    setDemoEvents([]);
  };

  const handleReset = () => {
    setProgress(0);
    setElapsedTime(0);
    setDemoEvents([]);
    setLiveMetrics({
      totalVehicles: currentScenario?.vehicles || 0,
      activeAgents: 0,
      alertsGenerated: 0,
      decisionsPerSecond: 0,
      avgResponseTime: 0,
      systemLoad: 0,
      dataProcessed: 0,
      aiAccuracy: 0,
      fuelSaved: 0,
      emissionsReduced: 0
    });
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getEventIcon = (type: DemoEvent['type']) => {
    switch (type) {
      case 'alert': return AlertTriangle;
      case 'decision': return Target;
      case 'optimization': return TrendingUp;
      case 'maintenance': return Settings;
      case 'emergency': return Shield;
      default: return Activity;
    }
  };

  const getEventColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'from-red-500 to-red-600 text-white border-red-400';
      case 'medium': return 'from-yellow-500 to-yellow-600 text-white border-yellow-400';
      case 'low': return 'from-green-500 to-green-600 text-white border-green-400';
      default: return 'from-slate-600 to-slate-700 text-white border-white/20';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-3 sm:p-6 text-slate-100">
      <audio ref={audioRef} preload="auto">
        <source src="/notification.mp3" type="audio/mpeg" />
      </audio>

      {/* Stunning Header with Animated Background */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary-600 via-blue-600 to-purple-600 p-6 sm:p-8 mb-8 shadow-2xl">
        {/* Animated background pattern */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-pulse"></div>
        </div>

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-3 glass-card/20 rounded-xl backdrop-blur-sm">
                <Presentation className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl sm:text-4xl font-bold text-white flex items-center">
                Live Demo Interface
                <Sparkles className="w-6 h-6 ml-2 animate-pulse" />
              </h1>
            </div>
            <p className="text-blue-100 text-lg">
              Interactive demonstration of AutoMind AI capabilities
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Connection Status */}
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg backdrop-blur-sm ${isConnected ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
              <div className={`w-3 h-3 rounded-full animate-pulse ${isConnected ? 'bg-green-300' : 'bg-red-300'}`}></div>
              <span className="text-white font-medium text-sm">
                {isConnected ? 'Live Connected' : 'Disconnected'}
              </span>
            </div>

            {/* Demo Controls */}
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleFullscreen}
                className="p-2 bg-white/20 hover:glass-card/30 text-white rounded-lg transition-all backdrop-blur-sm"
                title={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
              >
                {isFullscreen ? <Minimize className="w-5 h-5" /> : <Maximize className="w-5 h-5" />}
              </button>

              <button
                onClick={() => setSoundEnabled(!soundEnabled)}
                className="p-2 bg-white/20 hover:glass-card/30 text-white rounded-lg transition-all backdrop-blur-sm"
                title={soundEnabled ? 'Mute Sound' : 'Enable Sound'}
              >
                {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </button>

              <button
                onClick={() => setShowNotes(!showNotes)}
                className="p-2 bg-white/20 hover:glass-card/30 text-white rounded-lg transition-all backdrop-blur-sm"
                title={showNotes ? 'Hide Notes' : 'Show Notes'}
              >
                {showNotes ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stunning Control Panel */}
      {currentScenario && (
        <div className="relative overflow-hidden rounded-2xl glass-card p-6 mb-8 shadow-xl border-2 border-primary-200">
          {/* Animated gradient border */}
          <div className="absolute inset-0 bg-gradient-to-r from-primary-400 via-blue-400 to-purple-400 opacity-20 animate-pulse"></div>

          <div className="relative z-10">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className={`p-3 rounded-xl bg-gradient-to-br ${currentScenario.gradient} shadow-lg transform hover:scale-110 transition-transform`}>
                  {React.createElement(currentScenario.icon, { className: 'w-6 h-6 text-white' })}
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white">{currentScenario.name}</h3>
                  <p className="text-sm text-slate-300">{currentScenario.description}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-primary-600">
                  {formatTime(elapsedTime)}
                </div>
                <div className="text-sm text-slate-400">
                  of {formatTime(currentScenario.duration)}
                </div>
              </div>
            </div>

            {/* Stunning Progress Bar */}
            <div className="relative w-full h-4 glass-card/15 rounded-full overflow-hidden mb-6 shadow-inner">
              <div
                className={`absolute inset-y-0 left-0 bg-gradient-to-r ${currentScenario.gradient} transition-all duration-1000 shadow-lg`}
                style={{ width: `${progress}%` }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse"></div>
              </div>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-bold text-slate-200">
                  {progress.toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Control Buttons */}
            <div className="flex items-center justify-center space-x-4">
              <button
                onClick={handlePause}
                className={`flex items-center px-6 py-3 rounded-xl font-bold shadow-lg transform hover:scale-105 transition-all ${
                  isPaused
                    ? 'bg-gradient-to-r from-green-500 to-green-600 text-white hover:from-green-600 hover:to-green-700'
                    : 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-white hover:from-yellow-600 hover:to-yellow-700'
                }`}
              >
                {isPaused ? <Play className="w-5 h-5 mr-2" /> : <Pause className="w-5 h-5 mr-2" />}
                {isPaused ? 'Resume' : 'Pause'}
              </button>
              <button
                onClick={handleStop}
                className="flex items-center px-6 py-3 rounded-xl font-bold bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 shadow-lg transform hover:scale-105 transition-all"
              >
                <Square className="w-5 h-5 mr-2" />
                Stop
              </button>
              <button
                onClick={handleReset}
                className="flex items-center px-6 py-3 rounded-xl font-bold bg-gradient-to-r from-slate-700 to-slate-800 text-white hover:from-slate-600 hover:to-slate-700 shadow-lg transform hover:scale-105 transition-all"
              >
                <RotateCcw className="w-5 h-5 mr-2" />
                Reset
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Stunning Demo Scenarios Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {demoScenarios.map((scenario) => {
          const ScenarioIcon = scenario.icon;
          return (
            <div
              key={scenario.id}
              className={`group relative overflow-hidden rounded-2xl transition-all duration-300 cursor-pointer ${
                currentScenario?.id === scenario.id
                  ? 'ring-4 ring-primary-400 shadow-2xl'
                  : 'shadow-lg hover:shadow-2xl hover:-translate-y-2'
              }`}
              onClick={() => !isRunning && handleStart(scenario)}
            >
              {/* Animated gradient background */}
              <div className={`absolute inset-0 bg-gradient-to-br ${scenario.gradient} opacity-10 group-hover:opacity-20 transition-opacity`}></div>

              <div className="relative z-10 glass-card p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className={`p-3 rounded-xl bg-gradient-to-br ${scenario.gradient} shadow-lg group-hover:scale-110 transition-transform`}>
                        <ScenarioIcon className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-white">{scenario.name}</h3>
                        <p className="text-sm text-slate-300 mt-1">{scenario.description}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4 text-sm mb-4">
                      <div className="flex items-center text-slate-300">
                        <Clock className="w-4 h-4 mr-1" />
                        <span className="font-medium">{formatTime(scenario.duration)}</span>
                      </div>
                      <div className="flex items-center text-slate-300">
                        <Car className="w-4 h-4 mr-1" />
                        <span className="font-medium">{scenario.vehicles} vehicles</span>
                      </div>
                    </div>

                    {/* Expected Results */}
                    <div className="grid grid-cols-2 gap-2 mb-4">
                      {scenario.expectedOutcomes.slice(0, 4).map((outcome, index) => (
                        <div key={index} className={`text-xs font-bold text-white px-3 py-2 rounded-lg bg-gradient-to-r ${scenario.gradient} shadow-sm`}>
                          {outcome}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex-shrink-0 ml-4">
                    {currentScenario?.id === scenario.id && isRunning ? (
                      <div className={`p-4 rounded-xl bg-gradient-to-br ${scenario.gradient} animate-pulse`}>
                        <Activity className="w-8 h-8 text-white" />
                      </div>
                    ) : (
                      <button
                        disabled={isRunning}
                        className={`p-4 rounded-xl bg-gradient-to-br ${scenario.gradient} text-white shadow-lg hover:scale-110 transition-all disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        <Rocket className="w-8 h-8" />
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Corner decoration */}
              <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${scenario.gradient} opacity-10 rounded-bl-full group-hover:opacity-20 transition-opacity`}></div>
            </div>
          );
        })}
      </div>

      {/* Stunning Live Metrics */}
      {isRunning && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Metrics */}
          <div className="lg:col-span-2 relative overflow-hidden rounded-2xl glass-card p-6 shadow-xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center">
                <BarChart3 className="w-6 h-6 mr-2 text-primary-600" />
                Live Metrics
              </h2>
              <div className="flex items-center px-3 py-1 bg-green-100 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
                <span className="text-sm font-bold text-green-700">Live Data</span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              {[
                { label: 'Vehicles', value: liveMetrics.totalVehicles, icon: Car, gradient: 'from-blue-500 to-blue-600' },
                { label: 'Active Agents', value: liveMetrics.activeAgents, icon: Users, gradient: 'from-green-500 to-green-600' },
                { label: 'Alerts', value: liveMetrics.alertsGenerated, icon: AlertTriangle, gradient: 'from-yellow-500 to-yellow-600' },
                { label: 'Decisions/sec', value: liveMetrics.decisionsPerSecond, icon: Zap, gradient: 'from-purple-500 to-purple-600' },
                { label: 'Response Time', value: `${liveMetrics.avgResponseTime}ms`, icon: Clock, gradient: 'from-pink-500 to-pink-600' },
                { label: 'System Load', value: `${liveMetrics.systemLoad}%`, icon: Gauge, gradient: 'from-orange-500 to-orange-600' }
              ].map((metric, index) => {
                const MetricIcon = metric.icon;
                return (
                  <div key={index} className={`relative overflow-hidden rounded-xl bg-gradient-to-br ${metric.gradient} p-4 shadow-lg transform hover:scale-105 transition-transform`}>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20 animate-pulse"></div>
                    <div className="relative z-10">
                      <p className="text-white/80 text-sm font-medium mb-1">{metric.label}</p>
                      <p className="text-white text-3xl font-bold">{metric.value}</p>
                      <MetricIcon className="absolute bottom-2 right-2 w-8 h-8 text-white/30" />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Additional Performance Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Data Processed', value: Math.round(liveMetrics.dataProcessed).toLocaleString(), unit: 'MB', icon: Cpu, gradient: 'from-blue-500 to-cyan-500' },
                { label: 'AI Accuracy', value: liveMetrics.aiAccuracy.toFixed(1), unit: '%', icon: Target, gradient: 'from-green-500 to-emerald-500' },
                { label: 'Fuel Saved', value: liveMetrics.fuelSaved.toFixed(1), unit: 'L', icon: TrendingUp, gradient: 'from-purple-500 to-pink-500' },
                { label: 'CO₂ Reduced', value: liveMetrics.emissionsReduced.toFixed(1), unit: 'kg', icon: Shield, gradient: 'from-emerald-500 to-green-500' }
              ].map((metric, index) => {
                const MetricIcon = metric.icon;
                return (
                  <div key={index} className={`relative overflow-hidden rounded-xl bg-gradient-to-br ${metric.gradient} p-4 shadow-lg`}>
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 animate-pulse"></div>
                    <div className="relative z-10 text-white">
                      <p className="text-white/80 text-xs font-medium mb-1">{metric.label}</p>
                      <div className="flex items-baseline">
                        <p className="text-2xl font-bold">{metric.value}</p>
                        <span className="text-sm ml-1 opacity-80">{metric.unit}</span>
                      </div>
                      <MetricIcon className="absolute bottom-2 right-2 w-6 h-6 text-white/30" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Live Event Feed */}
          <div className="relative overflow-hidden rounded-2xl glass-card p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">Live Events</h3>
              <div className="px-2 py-1 bg-primary-100 rounded-lg">
                <span className="text-sm font-bold text-primary-700">{demoEvents.length}</span>
              </div>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {demoEvents.length === 0 ? (
                <div className="text-center py-12">
                  <Activity className="w-12 h-12 mx-auto mb-3 text-slate-500 animate-pulse" />
                  <p className="text-sm font-medium text-slate-400">Waiting for events...</p>
                  <p className="text-xs text-slate-400">Events will appear when demo starts</p>
                </div>
              ) : (
                demoEvents.map((event) => {
                  const EventIcon = getEventIcon(event.type);
                  return (
                    <div
                      key={event.id}
                      className={`relative overflow-hidden p-3 rounded-xl bg-gradient-to-r ${getEventColor(event.severity)} shadow-md transform hover:scale-102 transition-all`}
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20 animate-pulse"></div>
                      <div className="relative z-10 flex items-start space-x-3">
                        <EventIcon className="w-5 h-5 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <h4 className="text-sm font-bold truncate">{event.title}</h4>
                            <span className="text-xs opacity-75">
                              {new Date(event.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="text-xs opacity-90 mb-1">{event.description}</p>
                          {event.vehicleId && (
                            <div className="flex items-center text-xs opacity-75">
                              <Car className="w-3 h-3 mr-1" />
                              Vehicle {event.vehicleId.slice(-4)}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}

      {/* Presentation Notes */}
      {showNotes && currentScenario && (
        <div className="mt-8 relative overflow-hidden rounded-2xl glass-card p-6 shadow-xl border-2 border-purple-200">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-50 via-pink-50 to-blue-50 opacity-50"></div>
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center">
                <Presentation className="w-6 h-6 mr-2 text-purple-600" />
                Presentation Notes
              </h2>
              <button
                onClick={() => setShowNotes(false)}
                className="p-2 bg-purple-100 hover:bg-purple-200 rounded-lg transition-colors"
              >
                <EyeOff className="w-5 h-5 text-purple-600" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Key Points */}
              <div className="glass-card rounded-xl p-4 shadow-md">
                <h3 className="font-bold text-white mb-3 flex items-center">
                  <Target className="w-5 h-5 mr-2 text-primary-600" />
                  Key Talking Points
                </h3>
                <div className="space-y-2">
                  {currentScenario.keyPoints.map((point, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-1 flex-shrink-0" />
                      <p className="text-sm text-slate-200">{point}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Expected Outcomes */}
              <div className="glass-card rounded-xl p-4 shadow-md">
                <h3 className="font-bold text-white mb-3 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
                  Expected Outcomes
                </h3>
                <div className="space-y-2">
                  {currentScenario.expectedOutcomes.map((outcome, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <div className="w-4 h-4 bg-green-500 rounded-full mt-1 flex-shrink-0"></div>
                      <p className="text-sm text-slate-200">{outcome}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DemoInterface;
