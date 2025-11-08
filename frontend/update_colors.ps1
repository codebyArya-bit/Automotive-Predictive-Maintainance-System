# Batch update color scheme across all frontend pages and components

$files = @(
  "src\pages\VehicleList.tsx",
  "src\pages\VehicleDetail.tsx",
  "src\pages\Analytics.tsx",
  "src\pages\DemoAnalytics.tsx",
  "src\pages\MaintenanceList.tsx",
  "src\pages\AlertsList.tsx",
  "src\pages\ServiceHistory.tsx",
  "src\pages\ScheduleService.tsx",
  "src\pages\QualityMetrics.tsx",
  "src\pages\RecurringDefects.tsx",
  "src\pages\LogMonitor.tsx",
  "src\pages\SystemMaintenance.tsx",
  "src\pages\EdgeCaseDemo.tsx",
  "src\pages\DemoInterface.tsx",
  "src\components\VehicleForm.tsx",
  "src\components\MaintenanceForm.tsx",
  "src\components\NotificationBell.tsx",
  "src\components\NotificationPanel.tsx",
  "src\components\DemandForecastDashboard.tsx",
  "src\components\RCACAPAReport.tsx",
  "src\components\VoiceAgentSimulator.tsx"
)

$replacements = @{
  "text-gray-900" = "text-white"
  "text-gray-800" = "text-white"
  "text-gray-700" = "text-slate-200"
  "text-gray-600" = "text-slate-300"
  "text-gray-500" = "text-slate-300"
  "text-gray-400" = "text-slate-400"
  "bg-gray-50" = "bg-white/5"
  "bg-gray-100" = "bg-white/10"
  "bg-gray-200" = "bg-white/15"
  "text-blue-600" = "text-cyan-300"
  "text-blue-700" = "text-cyan-400"
  "text-green-600" = "text-emerald-300"
  "text-green-700" = "text-emerald-400"
  "text-purple-600" = "text-purple-300"
  "text-orange-600" = "text-orange-300"
  "text-red-600" = "text-rose-300"
  "border-gray-200" = "border-white/10"
  "border-gray-300" = "border-white/20"
  "hover:bg-gray-100" = "hover:bg-white/10"
  "hover:bg-gray-200" = "hover:bg-white/15"
  "hover:border-gray-300" = "hover:border-cyan-400/30"
}

foreach ($file in $files) {
  if (Test-Path $file) {
    Write-Host "Updating $file..."
    $content = Get-Content $file -Raw

    foreach ($key in $replacements.Keys) {
      $content = $content -replace [regex]::Escape($key), $replacements[$key]
    }

    Set-Content -Path $file -Value $content -NoNewline
    Write-Host "✓ Updated $file" -ForegroundColor Green
  } else {
    Write-Host "✗ File not found: $file" -ForegroundColor Yellow
  }
}

Write-Host "Color scheme update complete!" -ForegroundColor Cyan
