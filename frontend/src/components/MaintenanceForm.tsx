import React, { useState } from 'react';
import { MaintenanceRecord } from '../types';

interface MaintenanceFormProps {
  onSubmit: (maintenance: Omit<MaintenanceRecord, 'id' | 'created_at'>) => void;
  onCancel: () => void;
  vehicleId?: string;
  initialData?: Partial<MaintenanceRecord>;
}

const MaintenanceForm: React.FC<MaintenanceFormProps> = ({ 
  onSubmit, 
  onCancel, 
  vehicleId, 
  initialData 
}) => {
  const [formData, setFormData] = useState({
    vehicle_id: vehicleId || initialData?.vehicle_id || '',
    type: initialData?.type || 'scheduled' as 'scheduled' | 'predictive' | 'emergency',
    description: initialData?.description || '',
    cost: initialData?.cost || 0,
    status: initialData?.status || 'scheduled',
    priority: initialData?.priority || 'medium' as 'low' | 'medium' | 'high' | 'critical',
    scheduled_date: initialData?.scheduled_date || new Date().toISOString().split('T')[0],
    completed_date: initialData?.completed_date || '',
    technician: initialData?.technician || '',
    parts_used: initialData?.parts_used || [],
    notes: initialData?.notes || ''
  });

  const [newPart, setNewPart] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      scheduled_date: new Date(formData.scheduled_date).toISOString(),
      completed_date: formData.completed_date ? new Date(formData.completed_date).toISOString() : undefined
    });
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addPart = () => {
    if (newPart.trim()) {
      setFormData(prev => ({
        ...prev,
        parts_used: [...prev.parts_used, newPart.trim()]
      }));
      setNewPart('');
    }
  };

  const removePart = (index: number) => {
    setFormData(prev => ({
      ...prev,
      parts_used: prev.parts_used.filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="glass-card border border-white/20 rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-white">
          {initialData ? 'Edit Maintenance Record' : 'Add Maintenance Record'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Basic Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Vehicle ID *
              </label>
              <input
                type="text"
                required
                value={formData.vehicle_id}
                onChange={(e) => handleInputChange('vehicle_id', e.target.value)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="Enter vehicle ID"
                disabled={!!vehicleId}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Type *
              </label>
              <select
                required
                value={formData.type}
                onChange={(e) => handleInputChange('type', e.target.value)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
              >
                <option value="routine" className="bg-slate-800 text-white">Routine Maintenance</option>
                <option value="repair" className="bg-slate-800 text-white">Repair</option>
                <option value="inspection" className="bg-slate-800 text-white">Inspection</option>
                <option value="emergency" className="bg-slate-800 text-white">Emergency</option>
                <option value="recall" className="bg-slate-800 text-white">Recall</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-200 mb-1">
              Description *
            </label>
            <textarea
              required
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
              rows={3}
              placeholder="Describe the maintenance work..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Cost ($)
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={formData.cost}
                onChange={(e) => handleInputChange('cost', parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                placeholder="0.00"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => handleInputChange('status', e.target.value)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
              >
                <option value="scheduled" className="bg-slate-800 text-white">Scheduled</option>
                <option value="in_progress" className="bg-slate-800 text-white">In Progress</option>
                <option value="completed" className="bg-slate-800 text-white">Completed</option>
                <option value="cancelled" className="bg-slate-800 text-white">Cancelled</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Scheduled Date *
              </label>
              <input
                type="date"
                required
                value={formData.scheduled_date}
                onChange={(e) => handleInputChange('scheduled_date', e.target.value)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Completed Date
              </label>
              <input
                type="date"
                value={formData.completed_date}
                onChange={(e) => handleInputChange('completed_date', e.target.value)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-200 mb-1">
              Technician
            </label>
            <input
              type="text"
              value={formData.technician}
              onChange={(e) => handleInputChange('technician', e.target.value)}
              className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
              placeholder="Technician name"
            />
          </div>

          {/* Parts Used */}
          <div>
            <label className="block text-sm font-medium text-slate-200 mb-1">
              Parts Used
            </label>
            <div className="space-y-2">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newPart}
                  onChange={(e) => setNewPart(e.target.value)}
                  className="flex-1 px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                  placeholder="Enter part name"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addPart())}
                />
                <button
                  type="button"
                  onClick={addPart}
                  className="px-3 py-2 bg-gradient-to-r from-emerald-500 to-green-500 text-white rounded-xl hover:from-emerald-600 hover:to-green-600 focus:outline-none focus:ring-2 focus:ring-emerald-400/60 shadow-lg shadow-emerald-500/30 transition-all duration-200"
                >
                  Add
                </button>
              </div>

              {formData.parts_used.length > 0 && (
                <div className="border border-white/20 rounded-xl p-2 max-h-32 overflow-y-auto bg-white/5">
                  {formData.parts_used.map((part, index) => (
                    <div key={index} className="flex justify-between items-center py-1">
                      <span className="text-sm text-white">{part}</span>
                      <button
                        type="button"
                        onClick={() => removePart(index)}
                        className="text-rose-300 hover:text-rose-200 text-sm transition-colors"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-200 mb-1">
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
              rows={3}
              placeholder="Additional notes..."
            />
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-white/10">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-slate-300 border border-white/20 rounded-xl hover:bg-white/10 hover:border-white/30 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 transition-all duration-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-xl hover:from-cyan-600 hover:to-blue-600 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 shadow-lg shadow-cyan-500/30 transition-all duration-200"
            >
              {initialData ? 'Update Record' : 'Add Record'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MaintenanceForm;