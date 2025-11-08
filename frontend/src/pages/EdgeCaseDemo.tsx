import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface Scenario {
  scenario_name: string;
  description: string;
  category: string;
  priority: string;
  icon: string;
}

interface ScenarioStep {
  step: number;
  action: string;
  details?: any;
  conversation?: Array<{
    speaker: string;
    text: string;
  }>;
  outcome?: string;
  learnings?: string[];
}

interface ScenarioResult {
  scenario_name: string;
  description: string;
  steps: ScenarioStep[];
  business_impact: {
    customer_satisfaction: string;
    cost_impact: string;
    time_saved: string;
  };
  key_learnings: string[];
}

const EdgeCaseDemo: React.FC = () => {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingScenarios, setLoadingScenarios] = useState(true);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    loadScenarios();
  }, []);

  useEffect(() => {
    if (isPlaying && result && currentStep < result.steps.length) {
      const timeout = setTimeout(() => {
        setCurrentStep(prev => prev + 1);
      }, 2000);
      return () => clearTimeout(timeout);
    } else if (currentStep >= (result?.steps.length || 0)) {
      setIsPlaying(false);
    }
  }, [isPlaying, currentStep, result]);

  const loadScenarios = async () => {
    try {
      setLoadingScenarios(true);
      const response = await apiService.getEdgeCaseScenarios();
      setScenarios(response.scenarios || []);
    } catch (err) {
      console.error('Failed to load scenarios:', err);
    } finally {
      setLoadingScenarios(false);
    }
  };

  const runScenario = async (scenarioName: string) => {
    try {
      setLoading(true);
      setSelectedScenario(scenarioName);
      setCurrentStep(0);
      setResult(null);

      const response = await apiService.runEdgeCaseScenario(scenarioName);
      setResult(response.scenario);
      setIsPlaying(true);
    } catch (err) {
      console.error('Failed to run scenario:', err);
    } finally {
      setLoading(false);
    }
  };

  const resetDemo = () => {
    setResult(null);
    setSelectedScenario(null);
    setCurrentStep(0);
    setIsPlaying(false);
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-orange-500';
      case 'low':
        return 'bg-green-500';
      default:
        return 'bg-blue-500';
    }
  };

  if (loadingScenarios) {
    return (
      <div className="flex items-center justify-center min-h-screen glass-card/5">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading scenarios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl shadow-xl p-8 mb-6">
          <h1 className="text-3xl font-bold mb-2 flex items-center">
            <span className="mr-3">🎭</span>
            Edge Case Scenarios Demo
          </h1>
          <p className="text-blue-100">Demonstrating AI agent capabilities in challenging situations</p>
        </div>

        {!result ? (
          /* Scenario Selection */
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">Select a Scenario to Run</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {scenarios.map((scenario) => (
                <button
                  key={scenario.scenario_name}
                  onClick={() => runScenario(scenario.scenario_name)}
                  disabled={loading}
                  className="glass-card rounded-xl shadow-lg p-6 text-left hover:shadow-2xl transition-all transform hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="text-5xl">{scenario.icon}</div>
                    <span className={`${getPriorityColor(scenario.priority)} text-white text-xs px-3 py-1 rounded-full font-semibold`}>
                      {scenario.priority.toUpperCase()}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">
                    {scenario.scenario_name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                  </h3>
                  <p className="text-sm text-slate-300 mb-4">{scenario.description}</p>
                  <div className="inline-block bg-purple-100 text-purple-800 text-xs px-3 py-1 rounded-full font-medium">
                    {scenario.category}
                  </div>
                </button>
              ))}
            </div>

            {/* Info Box */}
            <div className="mt-8 glass-card rounded-xl shadow-md p-6">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
                <span className="mr-2">ℹ️</span>
                About Edge Case Scenarios
              </h3>
              <p className="text-slate-300 mb-4">
                These scenarios demonstrate how our AI agents handle complex, real-world situations that go beyond typical use cases.
                Each scenario showcases adaptive decision-making, multi-step reasoning, and customer-centric problem-solving.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-2xl mb-2">🤝</div>
                  <div className="text-xs text-slate-200 font-medium">Objection Handling</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-2xl mb-2">⚡</div>
                  <div className="text-xs text-slate-200 font-medium">Emergency Response</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <div className="text-2xl mb-2">🚗</div>
                  <div className="text-xs text-slate-200 font-medium">Fleet Management</div>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg text-center">
                  <div className="text-2xl mb-2">🔍</div>
                  <div className="text-xs text-slate-200 font-medium">Pattern Detection</div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Scenario Execution Display */
          <div>
            <div className="glass-card rounded-xl shadow-md p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-white">
                  {result.scenario_name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                </h2>
                <button
                  onClick={resetDemo}
                  className="glass-card/50 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors text-sm font-medium"
                >
                  ← Back to Scenarios
                </button>
              </div>
              <p className="text-slate-300">{result.description}</p>

              {/* Progress Bar */}
              <div className="mt-4">
                <div className="flex items-center justify-between text-sm text-slate-300 mb-2">
                  <span>Progress</span>
                  <span>{currentStep} / {result.steps.length} steps</span>
                </div>
                <div className="w-full glass-card/15 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(currentStep / result.steps.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Steps Display */}
            <div className="space-y-4 mb-6">
              {result.steps.slice(0, currentStep).map((step, index) => (
                <div
                  key={index}
                  className="glass-card rounded-xl shadow-md p-6 transform transition-all duration-500 animate-fade-in"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                      {step.step}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-white mb-2">{step.action}</h3>

                      {/* Details */}
                      {step.details && (
                        <div className="glass-card/5 rounded-lg p-4 mb-3">
                          {Object.entries(step.details).map(([key, value]) => (
                            <div key={key} className="text-sm mb-1">
                              <span className="font-semibold text-slate-200 capitalize">{key.replace('_', ' ')}:</span>
                              <span className="ml-2 text-slate-300">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Conversation */}
                      {step.conversation && (
                        <div className="space-y-2 mb-3">
                          {step.conversation.map((msg, msgIdx) => (
                            <div
                              key={msgIdx}
                              className={`flex ${msg.speaker === 'agent' ? 'justify-start' : 'justify-end'}`}
                            >
                              <div
                                className={`max-w-[80%] rounded-lg p-3 ${
                                  msg.speaker === 'agent'
                                    ? 'bg-blue-100 text-blue-900'
                                    : 'bg-green-100 text-green-900'
                                }`}
                              >
                                <div className="text-xs font-semibold mb-1">
                                  {msg.speaker === 'agent' ? '🤖 AI Agent' : '👤 Customer'}
                                </div>
                                <p className="text-sm">{msg.text}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Outcome */}
                      {step.outcome && (
                        <div className="bg-green-50 border-l-4 border-green-500 p-3 rounded-r-lg">
                          <div className="text-xs font-semibold text-green-800 mb-1">Outcome:</div>
                          <p className="text-sm text-green-700">{step.outcome}</p>
                        </div>
                      )}

                      {/* Learnings */}
                      {step.learnings && (
                        <div className="mt-3">
                          <div className="text-xs font-semibold text-purple-800 mb-2">Key Learnings:</div>
                          <ul className="space-y-1">
                            {step.learnings.map((learning, idx) => (
                              <li key={idx} className="text-sm text-slate-200 flex items-start">
                                <span className="text-purple-600 mr-2">•</span>
                                <span>{learning}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {/* Loading Next Step */}
              {isPlaying && currentStep < result.steps.length && (
                <div className="glass-card rounded-xl shadow-md p-6">
                  <div className="flex items-center gap-4">
                    <div className="flex-shrink-0">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                    <div className="text-slate-300">Processing next step...</div>
                  </div>
                </div>
              )}
            </div>

            {/* Business Impact & Learnings */}
            {currentStep >= result.steps.length && (
              <div className="space-y-6">
                {/* Business Impact */}
                <div className="bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-xl shadow-xl p-6">
                  <h3 className="text-2xl font-bold mb-4 flex items-center">
                    <span className="mr-2">📊</span>
                    Business Impact
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                      <div className="text-3xl font-bold mb-1">
                        {result.business_impact.customer_satisfaction}
                      </div>
                      <div className="text-sm text-green-100">Customer Satisfaction</div>
                    </div>
                    <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                      <div className="text-3xl font-bold mb-1">
                        {result.business_impact.cost_impact}
                      </div>
                      <div className="text-sm text-green-100">Cost Impact</div>
                    </div>
                    <div className="glass-card bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
                      <div className="text-3xl font-bold mb-1">
                        {result.business_impact.time_saved}
                      </div>
                      <div className="text-sm text-green-100">Time Saved</div>
                    </div>
                  </div>
                </div>

                {/* Key Learnings */}
                <div className="glass-card rounded-xl shadow-md p-6">
                  <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                    <span className="mr-2">💡</span>
                    Key Learnings
                  </h3>
                  <ul className="space-y-3">
                    {result.key_learnings.map((learning, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <span className="flex-shrink-0 w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </span>
                        <span className="text-slate-200">{learning}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-4 justify-center">
                  <button
                    onClick={() => {
                      setCurrentStep(0);
                      setIsPlaying(true);
                    }}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                  >
                    🔄 Replay Scenario
                  </button>
                  <button
                    onClick={resetDemo}
                    className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                  >
                    ← Try Another Scenario
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EdgeCaseDemo;
