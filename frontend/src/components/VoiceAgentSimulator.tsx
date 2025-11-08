import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface Message {
  speaker: 'agent' | 'customer';
  text: string;
  timestamp?: string;
  emotion?: string;
}

interface VoiceCall {
  call_id: string;
  status: 'initiating' | 'ringing' | 'active' | 'completed' | 'failed';
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  vehicle_id: string;
  customer_id: string;
  conversation_script?: {
    priority: string;
    urgency_level: string;
    conversation: Message[];
    key_points: string[];
    expected_outcome: string;
  };
  duration?: number;
}

interface VoiceAgentSimulatorProps {
  vehicleId?: string;
  customerId?: string;
}

const VoiceAgentSimulator: React.FC<VoiceAgentSimulatorProps> = ({
  vehicleId = '7ALSE94T6W43T3254',
  customerId = 'user_customer_1'
}) => {
  const [call, setCall] = useState<VoiceCall | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isMuted, setIsMuted] = useState(false);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [ttsEnabled, setTtsEnabled] = useState(true);

  // Safe accessor for conversation messages to avoid undefined errors
  const conversationMessages: Message[] = call?.conversation_script?.conversation ?? [];

  // Priority colors and descriptions
  const priorityConfig = {
    P0: {
      color: 'bg-red-600',
      textColor: 'text-red-600',
      borderColor: 'border-red-500',
      label: 'CRITICAL EMERGENCY',
      description: 'Immediate response required'
    },
    P1: {
      color: 'bg-orange-600',
      textColor: 'text-orange-600',
      borderColor: 'border-orange-500',
      label: 'URGENT',
      description: 'High priority, quick response needed'
    },
    P2: {
      color: 'bg-blue-600',
      textColor: 'text-blue-600',
      borderColor: 'border-blue-500',
      label: 'ROUTINE',
      description: 'Standard service scheduling'
    },
    P3: {
      color: 'bg-green-600',
      textColor: 'text-green-600',
      borderColor: 'border-green-500',
      label: 'INFORMATIONAL',
      description: 'General updates and reminders'
    }
  };

  // Simulate call duration timer
  useEffect(() => {
    if (call?.status === 'active' && isPlaying) {
      const timer = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [call?.status, isPlaying]);

  // Auto-play messages
  useEffect(() => {
    if (isPlaying && conversationMessages.length > 0 && currentMessageIndex < conversationMessages.length) {
      const timeout = setTimeout(() => {
        setCurrentMessageIndex(prev => prev + 1);
      }, 3000); // 3 seconds per message
      return () => clearTimeout(timeout);
    } else if (currentMessageIndex >= conversationMessages.length) {
      setIsPlaying(false);
      if (call) {
        setCall({ ...call, status: 'completed' });
      }
    }
  }, [isPlaying, currentMessageIndex, conversationMessages.length]);

  // Web Speech API TTS for agent messages
  useEffect(() => {
    try {
      if (!ttsEnabled || isMuted || call?.status !== 'active') return;
      const synth = (window as any).speechSynthesis;
      if (!synth) return;
      const idx = currentMessageIndex - 1;
      const msg = conversationMessages[idx];
      if (!msg || msg.speaker !== 'agent') return;
      const utter = new SpeechSynthesisUtterance(msg.text);
      utter.rate = 1;
      utter.pitch = 1;
      utter.volume = 1;
      synth.cancel();
      synth.speak(utter);
    } catch (e) {
      // Silent fail to avoid disrupting UI
    }
  }, [currentMessageIndex, ttsEnabled, isMuted, call?.status, conversationMessages]);

  const initiateCall = async (priority: 'P0' | 'P1' | 'P2' | 'P3') => {
    try {
      setLoading(true);
      setError(null);
      setCurrentMessageIndex(0);
      setCallDuration(0);

      // Set call to initiating
      setCall({
        call_id: `call_${Date.now()}`,
        status: 'initiating',
        priority,
        vehicle_id: vehicleId,
        customer_id: customerId
      });

      // Simulate ringing
      setTimeout(() => {
        setCall(prev => prev ? { ...prev, status: 'ringing' } : null);
      }, 1000);

      // Call API
      const response = await apiService.initiateVoiceCall(vehicleId, customerId, priority);

      // Set call as active with conversation
      setTimeout(() => {
        setCall({
          call_id: response.call.call_id || `call_${Date.now()}`,
          status: 'active',
          priority,
          vehicle_id: vehicleId,
          customer_id: customerId,
          conversation_script: response.call.conversation_script
        });
        setIsPlaying(true);
      }, 2000);

    } catch (err: any) {
      setError(err.message || 'Failed to initiate call');
      setCall(null);
    } finally {
      setLoading(false);
    }
  };

  const endCall = () => {
    if (call) {
      setCall({ ...call, status: 'completed' });
      setIsPlaying(false);
    }
  };

  const resetCall = () => {
    setCall(null);
    setCurrentMessageIndex(0);
    setCallDuration(0);
    setIsPlaying(false);
    setIsMuted(false);
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const config = call ? priorityConfig[call.priority] : priorityConfig.P2;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="glass-card rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className={`${config.color} text-white p-6`}>
          <h2 className="text-2xl font-bold mb-2 flex items-center">
            <span className="mr-3">📞</span>
            AI Voice Agent Simulator
          </h2>
          <p className="text-sm opacity-90">Intelligent predictive customer engagement</p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 p-4 m-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {!call ? (
          // Priority Selection
          <div className="p-8">
            <h3 className="text-xl font-semibold text-white mb-6">Select Call Priority</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(priorityConfig).map(([priority, conf]) => (
                <button
                  key={priority}
                  onClick={() => initiateCall(priority as 'P0' | 'P1' | 'P2' | 'P3')}
                  disabled={loading}
                  className={`${conf.color} text-white p-6 rounded-xl hover:opacity-90 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  <div className="text-2xl font-bold mb-2">{priority}</div>
                  <div className="text-lg font-semibold mb-1">{conf.label}</div>
                  <div className="text-sm opacity-90">{conf.description}</div>
                </button>
              ))}
            </div>

            <div className="mt-8 glass-card/5 rounded-lg p-6">
              <h4 className="font-semibold text-white mb-3">Call Details</h4>
              <div className="text-sm text-slate-300 space-y-2">
                <p><strong>Vehicle ID:</strong> {vehicleId}</p>
                <p><strong>Customer ID:</strong> {customerId}</p>
              </div>
            </div>
          </div>
        ) : (
          // Active Call Interface
          <div className="p-8">
            {/* Call Status Header */}
            <div className={`border-2 ${config.borderColor} rounded-xl p-6 mb-6`}>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`${config.color} text-white px-4 py-1 rounded-full text-sm font-bold`}>
                      {call.priority}
                    </span>
                    <span className="text-slate-200 font-semibold capitalize">
                      {call.status.replace('_', ' ')}
                    </span>
                    {call.conversation_script?.urgency_level && (
                      <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-xs font-semibold">
                        Urgency: {call.conversation_script.urgency_level}
                      </span>
                    )}
                  </div>
                  <p className={`${config.textColor} font-semibold text-lg`}>
                    {config.label}
                  </p>
                </div>
                <div className="text-3xl">
                  {call.status === 'initiating' && '📞'}
                  {call.status === 'ringing' && '📲'}
                  {call.status === 'active' && '🎙️'}
                  {call.status === 'completed' && '✅'}
                </div>
              </div>

              {/* Call Duration */}
              {call.status === 'active' && (
                <div className="text-center py-4">
                  <div className="text-4xl font-mono font-bold text-white">
                    {formatDuration(callDuration)}
                  </div>
                  <div className="text-sm text-slate-400 mt-1">Call Duration</div>
                </div>
              )}

              {/* Audio Waveform Animation */}
              {call.status === 'active' && isPlaying && !isMuted && (
                <div className="flex items-center justify-center gap-1 h-16 mt-4">
                  {[...Array(20)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-2 ${config.color} rounded-full animate-pulse`}
                      style={{
                        height: `${Math.random() * 60 + 20}%`,
                        animationDelay: `${i * 0.05}s`
                      }}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Conversation Display */}
            {call.conversation_script && (
              <div className="glass-card/5 rounded-xl p-6 mb-6 min-h-[400px] max-h-[500px] overflow-y-auto">
                <h4 className="font-semibold text-white mb-4">Conversation</h4>
                <div className="space-y-4">
                  {conversationMessages
                    .slice(0, currentMessageIndex)
                    .map((message, index) => (
                      <div
                        key={index}
                        className={`flex ${message.speaker === 'agent' ? 'justify-start' : 'justify-end'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg p-4 ${
                            message.speaker === 'agent'
                              ? 'bg-blue-100 text-blue-900'
                              : 'bg-green-100 text-green-900'
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-sm">
                              {message.speaker === 'agent' ? '🤖 AI Agent' : '👤 Customer'}
                            </span>
                            {message.emotion && (
                              <span className="text-xs glass-card px-2 py-1 rounded">
                                {message.emotion}
                              </span>
                            )}
                          </div>
                          <p className="text-sm">{message.text}</p>
                        </div>
                      </div>
                    ))}

                  {/* Typing Indicator */}
                  {isPlaying && currentMessageIndex < conversationMessages.length && (
                    <div className="flex justify-start">
                      <div className="glass-card/15 rounded-lg p-4">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 glass-card/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 glass-card/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 glass-card/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  )}

                  {conversationMessages.length === 0 && (
                    <div className="text-sm text-slate-300">No conversation script available.</div>
                  )}
                </div>
              </div>
            )}

            {/* Key Points */}
            {call.conversation_script?.key_points && (
              <div className="bg-blue-50 rounded-xl p-6 mb-6">
                <h4 className="font-semibold text-blue-900 mb-3">Key Discussion Points</h4>
                <ul className="space-y-2">
                  {call.conversation_script.key_points.map((point, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm text-blue-800">
                      <span className="text-blue-600 mt-1">•</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Call Controls */}
            <div className="flex gap-4 justify-center">
              {call.status === 'active' && (
                <>
                  <button
                    onClick={() => setTtsEnabled(!ttsEnabled)}
                    className={`${ttsEnabled ? 'bg-purple-600' : 'bg-white/50'} text-white w-16 h-16 rounded-full hover:opacity-80 transition-opacity flex items-center justify-center text-2xl`}
                    title={ttsEnabled ? 'Disable TTS' : 'Enable TTS'}
                  >
                    {ttsEnabled ? '🗣️' : '🙊'}
                  </button>
                  <button
                    onClick={() => setIsMuted(!isMuted)}
                    className={`${isMuted ? 'bg-red-500' : 'bg-white/50'} text-white w-16 h-16 rounded-full hover:opacity-80 transition-opacity flex items-center justify-center text-2xl`}
                    title={isMuted ? 'Unmute' : 'Mute'}
                  >
                    {isMuted ? '🔇' : '🔊'}
                  </button>

                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="bg-blue-500 text-white w-16 h-16 rounded-full hover:opacity-80 transition-opacity flex items-center justify-center text-2xl"
                    title={isPlaying ? 'Pause' : 'Play'}
                  >
                    {isPlaying ? '⏸️' : '▶️'}
                  </button>

                  <button
                    onClick={endCall}
                    className="bg-red-600 text-white w-16 h-16 rounded-full hover:bg-red-700 transition-colors flex items-center justify-center text-2xl"
                    title="End Call"
                  >
                    📵
                  </button>
                </>
              )}

              {(call.status === 'completed' || call.status === 'failed') && (
                <button
                  onClick={resetCall}
                  className={`${config.color} text-white px-8 py-3 rounded-full hover:opacity-90 transition-opacity font-semibold`}
                >
                  Start New Call
                </button>
              )}
            </div>

            {/* Expected Outcome */}
            {call.status === 'completed' && call.conversation_script?.expected_outcome && (
              <div className="mt-6 bg-green-50 border-l-4 border-green-500 p-6 rounded-r-xl">
                <h4 className="font-semibold text-green-900 mb-2">Call Outcome</h4>
                <p className="text-sm text-green-800">{call.conversation_script.expected_outcome}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceAgentSimulator;
