# Fix remaining bg-white instances

$files = Get-ChildItem -Path "src" -Include *.tsx,*.ts -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $modified = $false

    # Replace bg-white with proper classes
    if ($content -match 'className="([^"]*)\sbg-white\s([^"]*)"') {
        $content = $content -replace 'className="([^"]*)bg-white([^"]*)"', 'className="$1glass-card$2"'
        $modified = $true
    }

    if ($content -match "className='([^']*)\sbg-white\s([^']*)'") {
        $content = $content -replace "className='([^']*)bg-white([^']*)'", "className='`$1glass-card`$2'"
        $modified = $true
    }

    # Also handle bg-white at start or end
    $content = $content -replace 'bg-white\s', 'glass-card '
    $content = $content -replace '\sbg-white"', ' glass-card"'
    $content = $content -replace "bg-white'", "glass-card'"

    if ($content -ne (Get-Content $file.FullName -Raw)) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        Write-Host "Fixed bg-white in $($file.Name)" -ForegroundColor Cyan
    }
}

Write-Host "Background fix complete" -ForegroundColor Green
