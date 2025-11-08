import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft,
  Car,
  MapPin,
  Calendar,
  Gauge,
  Thermometer,
  Fuel,
  Battery,
  AlertTriangle,
  Wrench,
  TrendingUp,
  Activity,
  Zap,
  RefreshCw,
  Play,
  Pause,
  Download,
  Wifi,
  WifiOff
} from 'lucide-react';
import { apiService } from '../services/api';
import { Vehicle, TelemetryData, MaintenanceRecord, Alert } from '../types';
import { useWebSocket } from '../hooks/useWebSocket';
import config from '../config';
import { useApiWithRetry } from '../hooks/useApiWithRetry';

interface TelemetryChart {
  timestamp: string;
  speed: number;
  engineRpm: number;
  engineTemp: number;
  fuelLevel: number;
  batteryVoltage: number;
}

interface DiagnosticData {
  errorCodes: string[];
  oilPressure: number;
  coolantLevel: number;
  batteryHealth: number;
  tiresPressure: { fl: number; fr: number; rl: number; rr: number };
}

const VehicleDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [telemetry, setTelemetry] = useState<TelemetryData[]>([]);
  const [chartData, setChartData] = useState<TelemetryChart[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceRecord[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [diagnostics, setDiagnostics] = useState<DiagnosticData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  
  const { executeWithFallback } = useApiWithRetry();
  
  // WebSocket connection for real-time vehicle updates
  const { 
    isConnected: wsConnected, 
    sendMessage
  } = useWebSocket(`${config.wsUrl}/vehicle/${id}`, {
    onMessage: (data) => {
      if (data.type === 'telemetry_update') {
        setTelemetry(prev => [data.telemetry, ...prev.slice(0, 49)]);
        updateChartData(data.telemetry);
      } else if (data.type === 'alert_update') {
        setAlerts(prev => [data.alert, ...prev]);
      } else if (data.type === 'diagnostics_update') {
        setDiagnostics(data.diagnostics);
      }
      setLastUpdate(new Date());
    },
    onError: () => {
      console.warn('Vehicle WebSocket connection failed, using polling');
    }
  });

  useEffect(() => {
    if (id) {
      fetchVehicleData();
    }
  }, [id]);

  // Set up polling fallback when WebSocket is not connected
  useEffect(() => {
    if (!wsConnected && isRealTimeEnabled && id) {
      const interval = setInterval(() => {
        fetchLatestTelemetry();
      }, 5000); // Poll every 5 seconds
      
      return () => clearInterval(interval);
    }
  }, [wsConnected, isRealTimeEnabled, id]);

  const fetchVehicleData = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      const [vehicleData, telemetryData, maintenanceData, alertsData] = await Promise.all([
        executeWithFallback(() => apiService.getVehicle(id), 'Failed to fetch vehicle data'),
        executeWithFallback(() => apiService.getVehicleTelemetry(id, { limit: 50 }), 'Failed to fetch telemetry'),
        executeWithFallback(() => apiService.getVehicleMaintenance(id), 'Failed to fetch maintenance data'),
        executeWithFallback(() => apiService.getVehicleAlerts(id), 'Failed to fetch alerts')
      ]);

      if (vehicleData) setVehicle(vehicleData);
      if (telemetryData) {
        setTelemetry(telemetryData);
        updateChartData(telemetryData);
      }
      if (maintenanceData) setMaintenance(maintenanceData);
      if (alertsData) setAlerts(alertsData);

      // Mock diagnostic data
      if (telemetryData && telemetryData.length > 0) {
        setDiagnostics({
          errorCodes: telemetryData[0]?.errorCodes || [],
        oilPressure: 35 + Math.random() * 10,
        coolantLevel: 85 + Math.random() * 10,
        batteryHealth: 90 + Math.random() * 8,
        tiresPressure: {
          fl: 32 + Math.random() * 3,
          fr: 32 + Math.random() * 3,
          rl: 31 + Math.random() * 3,
          rr: 31 + Math.random() * 3
        }
      });
      }

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch vehicle data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateChartData = (telemetryData: TelemetryData[] | TelemetryData) => {
    const dataArray = Array.isArray(telemetryData) ? telemetryData : [telemetryData];
    const chartPoints = dataArray.slice(0, 20).reverse().map((data: TelemetryData) => ({
      timestamp: new Date(data.timestamp).toLocaleTimeString(),
      speed: data.speed || 0,
      engineRpm: (data.engineRpm || 0) / 100, // Scale down for chart
      engineTemp: data.engineTemp || 0,
      fuelLevel: data.fuelLevel || 0,
      batteryVoltage: (data.batteryVoltage || 12) * 10 // Scale up for visibility
    }));
    setChartData(chartPoints);
  };

  const fetchLatestTelemetry = async () => {
    if (!id) return;
    
    try {
      const telemetryData = await executeWithFallback(
        () => apiService.getVehicleTelemetry(id, { limit: 1 }),
        'Failed to fetch latest telemetry'
      );
      
      if (telemetryData && telemetryData.length > 0) {
        setTelemetry(prev => [telemetryData[0], ...prev.slice(0, 49)]);
        updateChartData(telemetryData[0]);
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error('Failed to fetch latest telemetry:', error);
    }
  };

  const toggleRealTime = () => {
    setIsRealTimeEnabled(!isRealTimeEnabled);
    
    if (!isRealTimeEnabled && wsConnected) {
      // Request real-time updates via WebSocket
      sendMessage({ type: 'subscribe_telemetry', vehicleId: id });
    } else if (isRealTimeEnabled && wsConnected) {
      // Unsubscribe from real-time updates
      sendMessage({ type: 'unsubscribe_telemetry', vehicleId: id });
    }
  };

  const getStatusColor = (status: string | undefined) => {
    if (!status) {
      return 'text-slate-300 bg-white/5';
    }
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'operational':
        return 'text-success-600 bg-success-50';
      case 'warning':
      case 'maintenance_due':
        return 'text-warning-600 bg-warning-50';
      case 'critical':
      case 'breakdown':
        return 'text-danger-600 bg-danger-50';
      default:
        return 'text-slate-300 bg-white/5';
    }
  };

  const getLatestTelemetry = () => {
    return telemetry.length > 0 ? telemetry[0] : null;
  };

  const exportTelemetryData = () => {
    const csvContent = [
      ['Timestamp', 'Speed', 'Engine RPM', 'Engine Temp', 'Fuel Level', 'Battery Voltage'].join(','),
      ...telemetry.map(data => [
        new Date(data.timestamp).toISOString(),
        data.speed || 0,
        data.engineRpm || 0,
        data.engineTemp || 0,
        data.fuelLevel || 0,
        data.batteryVoltage || 0
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vehicle_${id}_telemetry.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!vehicle) {
    return (
      <div className="text-center py-12">
        <Car className="w-12 h-12 text-slate-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-white mb-2">Vehicle not found</h3>
        <p className="text-slate-300 mb-4">The requested vehicle could not be found.</p>
        <Link to="/vehicles" className="text-primary-600 hover:text-primary-700">
          Back to Vehicle List
        </Link>
      </div>
    );
  }

  const latestTelemetry = getLatestTelemetry();

  return (
    <div className="space-y-4 sm:space-y-6 p-3 sm:p-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
        <div className="flex items-center space-x-3 sm:space-x-4">
          <Link
            to="/vehicles"
            className="p-2 text-slate-400 hover:text-slate-300 rounded-lg hover:bg-white/10"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-white">
              {vehicle.make} {vehicle.model} ({vehicle.year})
            </h1>
            <p className="text-sm sm:text-base text-slate-300">VIN: {vehicle.vin}</p>
          </div>
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
          {/* Connection Status Indicator */}
          <div className="flex items-center text-xs sm:text-sm">
            {wsConnected ? (
              <div className="flex items-center text-success-600">
                <Wifi className="w-4 h-4 mr-1" />
                <span className="hidden sm:inline">Connected</span>
              </div>
            ) : (
              <div className="flex items-center text-warning-600">
                <WifiOff className="w-4 h-4 mr-1" />
                <span className="hidden sm:inline">Offline</span>
              </div>
            )}
          </div>
          
          <button
            onClick={toggleRealTime}
            className={`inline-flex items-center justify-center px-3 py-2 rounded-lg text-sm font-medium ${
              isRealTimeEnabled 
                ? 'bg-success-100 text-success-700 hover:bg-success-200' 
                : 'bg-white/10 text-slate-200 hover:bg-white/15'
            }`}
          >
            {isRealTimeEnabled ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
            {isRealTimeEnabled ? 'Live' : 'Start Live'}
          </button>
          <button
            onClick={fetchVehicleData}
            className="inline-flex items-center justify-center px-3 py-2 bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <span className={`inline-flex items-center justify-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(vehicle.status)}`}>
            {vehicle.status}
          </span>
        </div>
      </div>

      {/* Real-time Status Bar */}
      {isRealTimeEnabled && (
        <div className={`border rounded-lg p-4 ${wsConnected ? 'bg-success-50 border-success-200' : 'bg-warning-50 border-warning-200'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className={`w-2 h-2 rounded-full animate-pulse mr-3 ${wsConnected ? 'bg-success-500' : 'bg-warning-500'}`}></div>
              <span className={`font-medium ${wsConnected ? 'text-success-700' : 'text-warning-700'}`}>
                {wsConnected ? 'Live monitoring active' : 'Live monitoring (polling mode)'}
              </span>
            </div>
            <span className={`text-sm ${wsConnected ? 'text-success-600' : 'text-warning-600'}`}>
              Last update: {lastUpdate.toLocaleTimeString()}
            </span>
          </div>
        </div>
      )}

      {/* Vehicle Overview Card */}
      <div className="card">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <div className="flex items-center">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-primary-100 rounded-lg flex items-center justify-center mr-3 sm:mr-4">
              <Car className="w-5 h-5 sm:w-6 sm:h-6 text-primary-600" />
            </div>
            <div>
              <p className="text-xs sm:text-sm text-slate-300">License Plate</p>
              <p className="text-sm sm:text-base font-semibold text-white">{vehicle.licensePlate}</p>
            </div>
          </div>

          <div className="flex items-center">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-3 sm:mr-4">
              <Gauge className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-xs sm:text-sm text-slate-300">Mileage</p>
              <p className="text-sm sm:text-base font-semibold text-white">{vehicle.mileage ? vehicle.mileage.toLocaleString() : '0'} mi</p>
            </div>
          </div>

          {vehicle.location && (
            <div className="flex items-center">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-100 rounded-lg flex items-center justify-center mr-3 sm:mr-4">
                <MapPin className="w-5 h-5 sm:w-6 sm:h-6 text-green-600" />
              </div>
              <div>
                <p className="text-xs sm:text-sm text-slate-300">Location</p>
                <p className="text-sm sm:text-base font-semibold text-white">{vehicle.location.address}</p>
              </div>
            </div>
          )}

          <div className="flex items-center">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-3 sm:mr-4">
              <Calendar className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-xs sm:text-sm text-slate-300">Last Updated</p>
              <p className="text-sm sm:text-base font-semibold text-white">
                {vehicle.lastUpdated ? new Date(vehicle.lastUpdated).toLocaleDateString() : new Date().toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-white/10">
        <nav className="-mb-px flex space-x-4 sm:space-x-8 overflow-x-auto">
          {[
            { id: 'overview', name: 'Overview', icon: Activity },
            { id: 'telemetry', name: 'Telemetry', icon: TrendingUp },
            { id: 'maintenance', name: 'Maintenance', icon: Wrench },
            { id: 'alerts', name: 'Alerts', icon: AlertTriangle }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-xs sm:text-sm whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-white/20'
                }`}
              >
                <Icon className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && latestTelemetry && (
        <div className="space-y-4 sm:space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            <div className="metric-card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm font-medium text-slate-300">Engine RPM</p>
                  <p className="text-xl sm:text-2xl font-bold text-white">{latestTelemetry.engineRpm}</p>
                </div>
                <div className="p-2 sm:p-3 bg-blue-50 rounded-lg">
                  <Activity className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="metric-card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm font-medium text-slate-300">Speed</p>
                  <p className="text-xl sm:text-2xl font-bold text-white">{latestTelemetry.speed} mph</p>
                </div>
                <div className="p-2 sm:p-3 bg-green-50 rounded-lg">
                  <Gauge className="w-5 h-5 sm:w-6 sm:h-6 text-green-600" />
                </div>
              </div>
            </div>

            <div className="metric-card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm font-medium text-slate-300">Engine Temp</p>
                  <p className="text-xl sm:text-2xl font-bold text-white">{latestTelemetry.engineTemp}°F</p>
                </div>
                <div className="p-2 sm:p-3 bg-orange-50 rounded-lg">
                  <Thermometer className="w-5 h-5 sm:w-6 sm:h-6 text-orange-600" />
                </div>
              </div>
            </div>

            <div className="metric-card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs sm:text-sm font-medium text-slate-300">Fuel Level</p>
                  <p className="text-xl sm:text-2xl font-bold text-white">{latestTelemetry.fuelLevel}%</p>
                </div>
                <div className="p-2 sm:p-3 bg-yellow-50 rounded-lg">
                  <Fuel className="w-5 h-5 sm:w-6 sm:h-6 text-yellow-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Diagnostics Section */}
          {diagnostics && (
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4">Vehicle Diagnostics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Battery Health */}
                <div className="bg-white/5 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-slate-300">Battery Health</span>
                    <Battery className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="flex items-center">
                    <div className="flex-1 bg-white/15 rounded-full h-2 mr-3">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{ width: `${diagnostics.batteryHealth}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold text-white">
                      {diagnostics.batteryHealth.toFixed(1)}%
                    </span>
                  </div>
                </div>

                {/* Oil Pressure */}
                <div className="bg-white/5 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-slate-300">Oil Pressure</span>
                    <Zap className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {diagnostics.oilPressure.toFixed(1)} PSI
                  </div>
                </div>

                {/* Coolant Level */}
                <div className="bg-white/5 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-slate-300">Coolant Level</span>
                    <Thermometer className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {diagnostics.coolantLevel.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Tire Pressure */}
              <div className="mt-6">
                <h4 className="text-md font-medium text-white mb-3">Tire Pressure</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <span className="text-sm text-slate-300">Front Left</span>
                    <span className="font-semibold text-white">
                      {diagnostics.tiresPressure.fl.toFixed(1)} PSI
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <span className="text-sm text-slate-300">Front Right</span>
                    <span className="font-semibold text-white">
                      {diagnostics.tiresPressure.fr.toFixed(1)} PSI
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <span className="text-sm text-slate-300">Rear Left</span>
                    <span className="font-semibold text-white">
                      {diagnostics.tiresPressure.rl.toFixed(1)} PSI
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <span className="text-sm text-slate-300">Rear Right</span>
                    <span className="font-semibold text-white">
                      {diagnostics.tiresPressure.rr.toFixed(1)} PSI
                    </span>
                  </div>
                </div>
              </div>

              {/* Error Codes */}
              {diagnostics.errorCodes.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-md font-medium text-white mb-3">Active Error Codes</h4>
                  <div className="space-y-2">
                    {diagnostics.errorCodes.map((code, index) => (
                      <div key={index} className="flex items-center p-3 bg-red-50 border border-red-200 rounded-lg">
                        <AlertTriangle className="w-5 h-5 text-red-500 mr-3" />
                        <span className="text-sm font-medium text-red-800">{code}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Telemetry Chart */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Telemetry Trends</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={exportTelemetryData}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-slate-200 bg-white/10 rounded-lg hover:bg-white/15"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </button>
              </div>
            </div>
            
            {/* Simple Chart Visualization */}
            <div className="h-64 bg-white/5 rounded-lg p-4 flex items-end justify-between space-x-1">
              {chartData.map((point, index) => (
                <div key={index} className="flex flex-col items-center space-y-1 flex-1">
                  {/* Speed Bar */}
                  <div className="w-full bg-white/15 rounded-sm relative" style={{ height: '60px' }}>
                    <div 
                      className="bg-blue-500 rounded-sm absolute bottom-0 w-full"
                      style={{ height: `${Math.max(5, (point.speed / 100) * 60)}px` }}
                      title={`Speed: ${point.speed} mph`}
                    ></div>
                  </div>
                  
                  {/* Fuel Level Bar */}
                  <div className="w-full bg-white/15 rounded-sm relative" style={{ height: '40px' }}>
                    <div 
                      className="bg-yellow-500 rounded-sm absolute bottom-0 w-full"
                      style={{ height: `${Math.max(3, (point.fuelLevel / 100) * 40)}px` }}
                      title={`Fuel: ${point.fuelLevel}%`}
                    ></div>
                  </div>
                  
                  {/* Engine Temp Bar */}
                  <div className="w-full bg-white/15 rounded-sm relative" style={{ height: '40px' }}>
                    <div 
                      className="bg-orange-500 rounded-sm absolute bottom-0 w-full"
                      style={{ height: `${Math.max(3, (point.engineTemp / 250) * 40)}px` }}
                      title={`Temp: ${point.engineTemp}°F`}
                    ></div>
                  </div>
                  
                  <span className="text-xs text-slate-400 transform -rotate-45 origin-center">
                    {point.timestamp}
                  </span>
                </div>
              ))}
            </div>
            
            {/* Chart Legend */}
            <div className="flex items-center justify-center space-x-6 mt-4 text-sm">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
                <span className="text-slate-300">Speed (mph)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-500 rounded mr-2"></div>
                <span className="text-slate-300">Fuel Level (%)</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-orange-500 rounded mr-2"></div>
                <span className="text-slate-300">Engine Temp (°F)</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'telemetry' && (
        <div className="space-y-6">
          {/* Telemetry Controls */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Telemetry Data</h3>
              <div className="flex items-center space-x-3">
                <button
                  onClick={exportTelemetryData}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-slate-200 bg-white/10 rounded-lg hover:bg-white/15"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export CSV
                </button>
                <button
                  onClick={fetchVehicleData}
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-primary-700 bg-primary-100 rounded-lg hover:bg-primary-200"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </button>
              </div>
            </div>

            {/* Enhanced Telemetry Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-white/5">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Timestamp
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Speed
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Engine RPM
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Engine Temp
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Fuel Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Battery
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Oil Pressure
                    </th>
                  </tr>
                </thead>
                <tbody className="glass-card divide-y divide-gray-200">
                  {telemetry.map((data, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'glass-card' : 'bg-white/5'}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                        {new Date(data.timestamp).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          (data.speed || 0) > 70 ? 'bg-red-100 text-red-800' :
                          (data.speed || 0) > 35 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {data.speed || 0} mph
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                        {data.engineRpm || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          (data.engineTemp || 0) > 220 ? 'bg-red-100 text-red-800' :
                          (data.engineTemp || 0) > 200 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {data.engineTemp || 0}°F
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                        <div className="flex items-center">
                          <div className="flex-1 bg-white/15 rounded-full h-2 mr-2" style={{ width: '60px' }}>
                            <div 
                              className={`h-2 rounded-full ${
                                (data.fuelLevel || 0) < 20 ? 'bg-red-500' :
                                (data.fuelLevel || 0) < 50 ? 'bg-yellow-500' :
                                'bg-green-500'
                              }`}
                              style={{ width: `${data.fuelLevel || 0}%` }}
                            ></div>
                          </div>
                          <span className="text-xs">{data.fuelLevel || 0}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                        {(data.batteryVoltage || 12).toFixed(1)}V
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                        {(data.oilPressure || 35).toFixed(1)} PSI
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'maintenance' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Maintenance History</h3>
          <div className="space-y-4">
            {maintenance.map((record) => (
              <div key={record.id} className="flex items-start p-4 bg-white/5 rounded-lg">
                <div className="flex-shrink-0 mr-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    record.status === 'completed' ? 'bg-success-100' : 
                    record.status === 'scheduled' ? 'bg-warning-100' : 'bg-white/10'
                  }`}>
                    <Wrench className={`w-5 h-5 ${
                      record.status === 'completed' ? 'text-success-600' : 
                      record.status === 'scheduled' ? 'text-warning-600' : 'text-slate-300'
                    }`} />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-white">{record.type}</h4>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      record.status === 'completed' ? 'text-success-600 bg-success-50' :
                      record.status === 'scheduled' ? 'text-warning-600 bg-warning-50' :
                      'text-slate-300 bg-white/5'
                    }`}>
                      {record.status}
                    </span>
                  </div>
                  <p className="text-sm text-slate-300 mt-1">{record.description}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-sm text-slate-400">
                      {record.status === 'completed' ? 'Completed' : 'Scheduled'}: {record.scheduledDate ? new Date(record.scheduledDate).toLocaleDateString() : 'Pending'}
                    </span>
                    {record.cost && (
                      <span className="text-sm font-medium text-white">${record.cost}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'alerts' && (
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Active Alerts</h3>
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div key={alert.id} className="flex items-start p-4 bg-white/5 rounded-lg">
                <div className="flex-shrink-0 mr-4">
                  <AlertTriangle className={`w-5 h-5 ${
                    alert.severity === 'critical' ? 'text-danger-500' :
                    alert.severity === 'warning' ? 'text-warning-500' : 'text-primary-500'
                  }`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-white">{alert.title}</h4>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        alert.severity === 'critical' ? 'text-danger-600 bg-danger-50' :
                        alert.severity === 'warning' ? 'text-warning-600 bg-warning-50' :
                        'text-primary-600 bg-primary-50'
                      }`}>
                      {alert.severity}
                    </span>
                  </div>
                  <p className="text-sm text-slate-300 mt-1">{alert.description}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-sm text-slate-400">
                      Created: {alert.createdAt ? new Date(alert.createdAt).toLocaleDateString() : new Date().toLocaleDateString()}
                    </span>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      alert.status === 'resolved' ? 'text-success-600 bg-success-50' :
                      alert.status === 'acknowledged' ? 'text-warning-600 bg-warning-50' :
                      'text-danger-600 bg-danger-50'
                    }`}>
                      {alert.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VehicleDetail;