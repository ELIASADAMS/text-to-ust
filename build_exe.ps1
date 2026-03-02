# Build script for Hiro UST Generator EXE
# This script handles dependency installation and builds the EXE

param(
    [switch]$Clean,
    [switch]$NoIcon
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommandPath
$VenvPath = Join-Path $ProjectRoot ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Hiro UST Generator - EXE Build" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if venv is activated
if (-not (Test-Path $PythonExe)) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please activate the virtual environment first:" -ForegroundColor Yellow
    Write-Host ".\.venv\Scripts\Activate.ps1"
    exit 1
}

# Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
& $PythonExe -m pip install --upgrade pip -q
& $PythonExe -m pip install -r requirements.txt -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dependencies installed!" -ForegroundColor Green

# Clean previous builds if requested
if ($Clean) {
    Write-Host "`n🗑️  Cleaning previous builds..." -ForegroundColor Yellow
    Remove-Item -Path (Join-Path $ProjectRoot "dist") -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path (Join-Path $ProjectRoot "build") -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Cleaned!" -ForegroundColor Green
}

# Build EXE
Write-Host "`n🔨 Building EXE..." -ForegroundColor Yellow
& $PythonExe build_exe.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Build completed successfully!" -ForegroundColor Green
    Write-Host "`n📍 EXE location: .\dist\Hiro_UST_Generator.exe" -ForegroundColor Cyan
    Write-Host "`n💡 Tips:" -ForegroundColor Cyan
    Write-Host "   • The EXE is standalone and includes all dependencies" -ForegroundColor White
    Write-Host "   • You can copy it to any Windows machine" -ForegroundColor White
    Write-Host "   • No Python installation required on target machines" -ForegroundColor White
} else {
    Write-Host "`n❌ Build failed!" -ForegroundColor Red
    exit 1
}

