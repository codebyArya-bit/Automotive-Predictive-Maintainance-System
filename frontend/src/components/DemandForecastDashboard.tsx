import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface DemandForecast {
  forecast_period: {
    start_date: string;
    end_date: string;
    total_days: number;
  };
  daily_forecast: Array<{
    date: string;
    predicted_demand: number;
    confidence: number;
  }>;
  summary: {
    average_daily_demand: number;
    peak_demand: number;
    peak_date: string;
    total_predicted_demand: number;
  };
}

interface ServiceCenterCapacity {
  service_centers: Array<{
    center_id: string;
    name: string;
    location: string;
    capacity: {
      daily_capacity: number;
      current_utilization: number;
      available_slots: number;
    };
    staffing: {
      current_staff: number;
      recommended_staff: number;
      utilization_rate: number;
    };
  }>;
  staffing_recommendations: Array<{
    recommendation: string;
    priority: string;
    impact: string;
  }>;
  optimization_opportunities: Array<{
    opportunity: string;
    potential_savings: string;
    implementation_complexity: string;
  }>;
}

const DemandForecastDashboard: React.FC = () => {
  const [forecast, setForecast] = useState<DemandForecast | null>(null);
  const [capacity, setCapacity] = useState<ServiceCenterCapacity | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDays, setSelectedDays] = useState(7);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [forecastData, capacityData] = await Promise.all([
        apiService.getDemandForecast(30),
        apiService.getServiceCenterCapacity()
      ]);

      setForecast(forecastData.forecast);
      setCapacity(capacityData.capacity);
    } catch (err: any) {
      setError(err.message || 'Failed to load forecast data');
    } finally {
      setLoading(false);
    }
  };

  const getDisplayForecast = () => {
    if (!forecast) return [];
    return forecast.daily_forecast.slice(0, selectedDays);
  };

  const getUtilizationColor = (utilization: number): string => {
    if (utilization >= 90) return 'text-red-600 bg-red-100';
    if (utilization >= 75) return 'text-orange-600 bg-orange-100';
    if (utilization >= 50) return 'text-blue-600 bg-blue-100';
    return 'text-green-600 bg-green-100';
  };

  const getPriorityBadge = (priority: string): string => {
    switch (priority.toLowerCase()) {
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading forecast data...</p>
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

  const displayForecast = getDisplayForecast();
  const maxDemand = displayForecast.length
    ? Math.max(...displayForecast.map(d => d.predicted_demand))
    : 100;

  return (
    <div className="p-6 bg-white/5 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl shadow-xl p-8 mb-6">
          <h1 className="text-3xl font-bold mb-2 flex items-center">
            <span className="mr-3">📊</span>
            Service Demand Forecasting
          </h1>
          <p className="text-blue-100">AI-powered predictive analytics for optimal resource planning</p>
        </div>

        {/* Summary Cards */}
        {forecast && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="glass-card rounded-xl shadow-md p-6">
              <div className="text-sm text-slate-400 mb-1">Average Daily Demand</div>
              <div className="text-3xl font-bold text-blue-600">
                {Number(forecast.summary?.average_daily_demand ?? 0).toFixed(1)}
              </div>
              <div className="text-xs text-slate-400 mt-1">vehicles/day</div>
            </div>

            <div className="glass-card rounded-xl shadow-md p-6">
              <div className="text-sm text-slate-400 mb-1">Peak Demand</div>
              <div className="text-3xl font-bold text-orange-600">
                {forecast.summary?.peak_demand ?? 0}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                on {forecast.summary?.peak_date ? new Date(forecast.summary.peak_date).toLocaleDateString() : '-'}
              </div>
            </div>

            <div className="glass-card rounded-xl shadow-md p-6">
              <div className="text-sm text-slate-400 mb-1">Total Forecast</div>
              <div className="text-3xl font-bold text-purple-600">
                {forecast.summary?.total_predicted_demand ?? 0}
              </div>
              <div className="text-xs text-slate-400 mt-1">vehicles ({forecast.forecast_period.total_days} days)</div>
            </div>

            <div className="glass-card rounded-xl shadow-md p-6">
              <div className="text-sm text-slate-400 mb-1">Forecast Period</div>
              <div className="text-lg font-bold text-green-600">
                {forecast.forecast_period?.total_days ?? 0} Days
              </div>
              <div className="text-xs text-slate-400 mt-1">
                {forecast.forecast_period?.start_date ? new Date(forecast.forecast_period.start_date).toLocaleDateString() : '-'} -
                {forecast.forecast_period?.end_date ? new Date(forecast.forecast_period.end_date).toLocaleDateString() : '-'}
              </div>
            </div>
          </div>
        )}

        {/* Forecast Chart */}
        <div className="glass-card rounded-xl shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">Daily Demand Forecast</h2>
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedDays(7)}
                className={`px-4 py-2 rounded-lg font-medium ${
                  selectedDays === 7 ? 'bg-blue-600 text-white' : 'bg-white/10 text-slate-300 hover:bg-white/15'
                }`}
              >
                7 Days
              </button>
              <button
                onClick={() => setSelectedDays(14)}
                className={`px-4 py-2 rounded-lg font-medium ${
                  selectedDays === 14 ? 'bg-blue-600 text-white' : 'bg-white/10 text-slate-300 hover:bg-white/15'
                }`}
              >
                14 Days
              </button>
              <button
                onClick={() => setSelectedDays(30)}
                className={`px-4 py-2 rounded-lg font-medium ${
                  selectedDays === 30 ? 'bg-blue-600 text-white' : 'bg-white/10 text-slate-300 hover:bg-white/15'
                }`}
              >
                30 Days
              </button>
            </div>
          </div>

          {/* Bar Chart */}
          <div className="relative h-64 flex items-end justify-between gap-1 border-b border-l border-white/20 p-4">
            {displayForecast.map((day, index) => {
              const heightPercent = (day.predicted_demand / maxDemand) * 100;
              const isWeekend = new Date(day.date).getDay() === 0 || new Date(day.date).getDay() === 6;

              return (
                <div key={index} className="flex flex-col items-center flex-1 group relative">
                  {/* Bar */}
                  <div
                    className={`w-full ${
                      isWeekend ? 'bg-purple-400' : 'bg-blue-500'
                    } hover:opacity-80 transition-all rounded-t-lg cursor-pointer`}
                    style={{ height: `${heightPercent}%` }}
                  >
                    {/* Tooltip */}
                    <div className="hidden group-hover:block absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-gray-900 text-white text-xs rounded-lg py-2 px-3 whitespace-nowrap z-10">
                      <div className="font-semibold">{new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
                      <div>{day.predicted_demand} vehicles</div>
                      <div className="text-gray-300">{day.confidence}% confidence</div>
                    </div>
                  </div>

                  {/* Date Label */}
                  {selectedDays <= 14 && (
                    <div className="text-xs text-slate-300 mt-2 transform -rotate-45 origin-top-left whitespace-nowrap">
                      {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div className="flex items-center justify-center gap-6 mt-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span className="text-slate-300">Weekday</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-purple-400 rounded"></div>
              <span className="text-slate-300">Weekend</span>
            </div>
          </div>
        </div>

        {/* Service Center Capacity */}
        {capacity && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="glass-card rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <span className="mr-2">🏢</span>
                Service Center Capacity
              </h2>
              <div className="space-y-4">
                {capacity.service_centers.map((center, index) => (
                  <div key={index} className="border border-white/10 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-white">{center.name}</h3>
                        <p className="text-xs text-slate-400">{center.location}</p>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-semibold ${getUtilizationColor(
                          center.capacity.current_utilization
                        )}`}
                      >
                        {center.capacity.current_utilization}%
                      </span>
                    </div>

                    {/* Utilization Bar */}
                    <div className="mb-3">
                      <div className="flex items-center justify-between text-xs text-slate-300 mb-1">
                        <span>Utilization</span>
                        <span>
                          {center.capacity.daily_capacity - center.capacity.available_slots} / {center.capacity.daily_capacity}
                        </span>
                      </div>
                      <div className="w-full bg-white/15 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            center.capacity.current_utilization >= 90
                              ? 'bg-red-500'
                              : center.capacity.current_utilization >= 75
                              ? 'bg-orange-500'
                              : 'bg-blue-500'
                          }`}
                          style={{ width: `${center.capacity.current_utilization}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Staffing Info */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-slate-400">Current Staff</div>
                        <div className="font-semibold text-white">{center.staffing.current_staff}</div>
                      </div>
                      <div>
                        <div className="text-slate-400">Recommended</div>
                        <div className="font-semibold text-blue-600">{center.staffing.recommended_staff}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Staffing Recommendations */}
            <div className="glass-card rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <span className="mr-2">👥</span>
                Staffing Recommendations
              </h2>
              <div className="space-y-3">
                {capacity.staffing_recommendations.map((rec, index) => (
                  <div
                    key={index}
                    className={`border-l-4 p-4 rounded-r-lg ${
                      rec.priority.toLowerCase() === 'high'
                        ? 'border-red-500 bg-red-50'
                        : rec.priority.toLowerCase() === 'medium'
                        ? 'border-orange-500 bg-orange-50'
                        : 'border-green-500 bg-green-50'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className={`text-xs font-semibold px-2 py-1 rounded border ${getPriorityBadge(rec.priority)}`}>
                        {rec.priority.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-slate-200 mb-2">{rec.recommendation}</p>
                    <div className="text-xs text-slate-300">
                      <strong>Impact:</strong> {rec.impact}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Optimization Opportunities */}
        {capacity && (
          <div className="glass-card rounded-xl shadow-md p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center">
              <span className="mr-2">💡</span>
              Optimization Opportunities
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {capacity.optimization_opportunities.map((opp, index) => (
                <div key={index} className="border border-white/10 rounded-lg p-4 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="text-2xl">🎯</div>
                    <span
                      className={`text-xs px-2 py-1 rounded font-semibold ${
                        opp.implementation_complexity.toLowerCase() === 'low'
                          ? 'bg-green-100 text-green-800'
                          : opp.implementation_complexity.toLowerCase() === 'medium'
                          ? 'bg-orange-100 text-orange-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {opp.implementation_complexity} Complexity
                    </span>
                  </div>
                  <p className="text-sm text-slate-200 mb-3">{opp.opportunity}</p>
                  <div className="text-xs text-green-600 font-semibold">
                    💰 {opp.potential_savings}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DemandForecastDashboard;
