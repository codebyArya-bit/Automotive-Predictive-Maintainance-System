#!/bin/bash

# Batch update color scheme across all frontend pages and components

FILES=(
  "src/pages/VehicleList.tsx"
  "src/pages/VehicleDetail.tsx"
  "src/pages/Analytics.tsx"
  "src/pages/DemoAnalytics.tsx"
  "src/pages/MaintenanceList.tsx"
  "src/pages/AlertsList.tsx"
  "src/pages/ServiceHistory.tsx"
  "src/pages/ScheduleService.tsx"
  "src/pages/QualityMetrics.tsx"
  "src/pages/RecurringDefects.tsx"
  "src/pages/LogMonitor.tsx"
  "src/pages/SystemMaintenance.tsx"
  "src/pages/EdgeCaseDemo.tsx"
  "src/pages/DemoInterface.tsx"
  "src/components/VehicleForm.tsx"
  "src/components/MaintenanceForm.tsx"
  "src/components/NotificationBell.tsx"
  "src/components/NotificationPanel.tsx"
  "src/components/DemandForecastDashboard.tsx"
  "src/components/RCACAPAReport.tsx"
  "src/components/VoiceAgentSimulator.tsx"
)

for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "Updating $file..."

    # Text colors
    sed -i 's/text-gray-900/text-white/g' "$file"
    sed -i 's/text-gray-800/text-white/g' "$file"
    sed -i 's/text-gray-700/text-slate-200/g' "$file"
    sed -i 's/text-gray-600/text-slate-300/g' "$file"
    sed -i 's/text-gray-500/text-slate-300/g' "$file"
    sed -i 's/text-gray-400/text-slate-400/g' "$file"

    # Background colors
    sed -i 's/bg-gray-50/bg-white\/5/g' "$file"
    sed -i 's/bg-gray-100/bg-white\/10/g' "$file"
    sed -i 's/bg-gray-200/bg-white\/15/g' "$file"

    # Accent colors (from dark to light)
    sed -i 's/text-blue-600/text-cyan-300/g' "$file"
    sed -i 's/text-blue-700/text-cyan-400/g' "$file"
    sed -i 's/text-green-600/text-emerald-300/g' "$file"
    sed -i 's/text-green-700/text-emerald-400/g' "$file"
    sed -i 's/text-purple-600/text-purple-300/g' "$file"
    sed -i 's/text-orange-600/text-orange-300/g' "$file"
    sed -i 's/text-red-600/text-rose-300/g' "$file"

    # Borders
    sed -i 's/border-gray-200/border-white\/10/g' "$file"
    sed -i 's/border-gray-300/border-white\/20/g' "$file"

    # Hover states
    sed -i 's/hover:bg-gray-100/hover:bg-white\/10/g' "$file"
    sed -i 's/hover:bg-gray-200/hover:bg-white\/15/g' "$file"
    sed -i 's/hover:border-gray-300/hover:border-cyan-400\/30/g' "$file"

    echo "✓ Updated $file"
  fi
done

echo "Color scheme update complete!"
