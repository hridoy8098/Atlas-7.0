# build_portable.ps1 — Create a portable Atlas 7.0 package
# Run: powershell -ExecutionPolicy Bypass .\build_portable.ps1
# Output: .\AtlasPortable\ folder — zip it and run anywhere

$ErrorActionPreference = "Stop"
$OUT = "AtlasPortable"
$DIST = "frontend\dist"

Write-Host "=== Building Atlas 7.0 Portable Package ===" -ForegroundColor Cyan

# 1. Verify frontend build
if (-not (Test-Path "$DIST\index.html")) {
    Write-Host "Building frontend..." -ForegroundColor Yellow
    Set-Location frontend
    npm run build
    Set-Location ..
}

# 2. Create portable directory
if (Test-Path $OUT) { Remove-Item -Recurse -Force $OUT }
New-Item -ItemType Directory -Path "$OUT\backend" -Force | Out-Null
New-Item -ItemType Directory -Path "$OUT\frontend\dist" -Force | Out-Null
New-Item -ItemType Directory -Path "$OUT\data" -Force | Out-Null
New-Item -ItemType Directory -Path "$OUT\logs" -Force | Out-Null

# 3. Copy files
Write-Host "Copying files..." -ForegroundColor Yellow
Copy-Item "main.py", "server.py", "config.py", "command_handler.py", "or_client.py", "run.py", "requirements.txt", "icon.ico" -Destination $OUT
Copy-Item "frontend\dist\index.html" -Destination "$OUT\frontend\dist\"
Copy-Item "frontend\dist\assets" -Destination "$OUT\frontend\dist\assets" -Recurse
Copy-Item "backend\*" -Destination "$OUT\backend" -Recurse -Exclude "__pycache__"
Copy-Item ".env" -Destination "$OUT\.env" -ErrorAction SilentlyContinue

# 4. Create launcher scripts
@"
@echo off
title Atlas 7.0
cd /d "%~dp0"
echo Starting Atlas 7.0...
echo Open http://localhost:8000 in your browser
echo Press Ctrl+C to stop
echo.
python main.py
pause
"@ | Set-Content "$OUT\Atlas.bat" -Encoding Ascii

@"
@echo off
title Atlas 7.0 (No Console)
cd /d "%~dp0"
start /min pythonw main.py
timeout /t 5 /nobreak >nul
start http://localhost:8000
"@ | Set-Content "$OUT\Atlas_Silent.bat" -Encoding Ascii

# 5. Create one-click install script for dependencies
@"
@echo off
echo Installing Atlas 7.0 dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Some packages failed to install.
    pause
)
echo Done!
pause
"@ | Set-Content "$OUT\install_deps.bat" -Encoding Ascii

Write-Host ""
Write-Host "=== Portable Package Created! ===" -ForegroundColor Green
Write-Host "Location: $OUT" -ForegroundColor Green
Write-Host ""
Write-Host "To use:"
Write-Host "  1. Install Python 3.13+ from python.org"
Write-Host "  2. Run install_deps.bat (one time)"
Write-Host "  3. Run Atlas.bat to start"
Write-Host ""
Write-Host "Total size: $(Get-ChildItem $OUT -Recurse | Measure-Object Length -Sum | Select-Object -ExpandProperty Sum) bytes" -ForegroundColor Cyan
