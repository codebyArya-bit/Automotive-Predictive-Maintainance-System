import React, { useState } from 'react';
import { Vehicle } from '../types';

interface VehicleFormProps {
  onSubmit: (vehicle: Omit<Vehicle, 'id' | 'created_at' | 'last_telemetry'>) => void;
  onCancel: () => void;
  initialData?: Partial<Vehicle>;
}

const VehicleForm: React.FC<VehicleFormProps> = ({ onSubmit, onCancel, initialData }) => {
  const [formData, setFormData] = useState({
    vin: initialData?.vin || '',
    make: initialData?.make || '',
    model: initialData?.model || '',
    year: initialData?.year || new Date().getFullYear(),
    license_plate: initialData?.license_plate || '',
    status: initialData?.status || 'active',
    mileage: initialData?.mileage || 0,
    owner: {
      id: initialData?.owner?.id || '',
      name: initialData?.owner?.name || '',
      email: initialData?.owner?.email || ''
    },
    location: {
      latitude: initialData?.location?.latitude || 0,
      longitude: initialData?.location?.longitude || 0,
      address: initialData?.location?.address || ''
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNestedInputChange = (parent: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [parent]: {
        ...(prev[parent as keyof typeof prev] as any),
        [field]: value
      }
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="glass-card border border-white/20 rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-white">
          {initialData ? 'Edit Vehicle' : 'Add New Vehicle'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Vehicle Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                VIN *
              </label>
              <input
                type="text"
                required
                value={formData.vin}
                onChange={(e) => handleInputChange('vin', e.target.value)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                placeholder="Enter VIN"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                License Plate *
              </label>
              <input
                type="text"
                required
                value={formData.license_plate}
                onChange={(e) => handleInputChange('license_plate', e.target.value)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                placeholder="Enter license plate"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Make *
              </label>
              <input
                type="text"
                required
                value={formData.make}
                onChange={(e) => handleInputChange('make', e.target.value)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                placeholder="e.g., Toyota"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Model *
              </label>
              <input
                type="text"
                required
                value={formData.model}
                onChange={(e) => handleInputChange('model', e.target.value)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                placeholder="e.g., Camry"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Year *
              </label>
              <input
                type="number"
                required
                min="1900"
                max={new Date().getFullYear() + 1}
                value={formData.year}
                onChange={(e) => handleInputChange('year', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => handleInputChange('status', e.target.value)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
              >
                <option value="active" className="bg-slate-800 text-white">Active</option>
                <option value="maintenance" className="bg-slate-800 text-white">Maintenance</option>
                <option value="inactive" className="bg-slate-800 text-white">Inactive</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-1">
                Mileage
              </label>
              <input
                type="number"
                min="0"
                value={formData.mileage}
                onChange={(e) => handleInputChange('mileage', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                placeholder="Current mileage"
              />
            </div>
          </div>

          {/* Owner Information */}
          <div className="border-t border-white/10 pt-4">
            <h3 className="text-lg font-semibold mb-3 text-white">Owner Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-1">
                  Owner Name
                </label>
                <input
                  type="text"
                  value={formData.owner.name}
                  onChange={(e) => handleNestedInputChange('owner', 'name', e.target.value)}
                  className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                  placeholder="Owner's full name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-1">
                  Owner Email
                </label>
                <input
                  type="email"
                  value={formData.owner.email}
                  onChange={(e) => handleNestedInputChange('owner', 'email', e.target.value)}
                  className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                  placeholder="owner@example.com"
                />
              </div>
            </div>
          </div>

          {/* Location Information */}
          <div className="border-t border-white/10 pt-4">
            <h3 className="text-lg font-semibold mb-3 text-white">Location</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-1">
                  Address
                </label>
                <input
                  type="text"
                  value={formData.location.address}
                  onChange={(e) => handleNestedInputChange('location', 'address', e.target.value)}
                  className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                  placeholder="Street address or location"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-200 mb-1">
                    Latitude
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={formData.location.latitude}
                    onChange={(e) => handleNestedInputChange('location', 'latitude', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                    placeholder="0.000000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-200 mb-1">
                    Longitude
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={formData.location.longitude}
                    onChange={(e) => handleNestedInputChange('location', 'longitude', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 bg-white/5 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60"
                    placeholder="0.000000"
                  />
                </div>
              </div>
            </div>
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
              {initialData ? 'Update Vehicle' : 'Add Vehicle'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default VehicleForm;