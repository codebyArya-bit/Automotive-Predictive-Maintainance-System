# Comprehensive color scheme fix for all frontend files

$replacements = @{
    "text-gray-900" = "text-white"
    "text-gray-800" = "text-white"
    "text-gray-700" = "text-slate-200"
    "text-gray-600" = "text-slate-300"
    "text-gray-500" = "text-slate-400"
    "text-gray-400" = "text-slate-400"
    "bg-gray-50" = "bg-white/5"
    "bg-gray-100" = "bg-white/10"
    "bg-gray-200" = "bg-white/15"
    "border-gray-300" = "border-white/20"
    "border-gray-200" = "border-white/10"
    "border-gray-100" = "border-white/5"
}

$files = Get-ChildItem -Path "src" -Include *.tsx,*.ts -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $modified = $false

    foreach ($key in $replacements.Keys) {
        if ($content -match [regex]::Escape($key)) {
            $content = $content -replace [regex]::Escape($key), $replacements[$key]
            $modified = $true
        }
    }

    if ($modified) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        Write-Host "Updated $($file.Name)" -ForegroundColor Green
    }
}

Write-Host "Batch update complete" -ForegroundColor Cyan
