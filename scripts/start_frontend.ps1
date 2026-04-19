# SupportRAG React Frontend Startup Script
# Starts the Vite dev server on port 8080

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SupportRAG React Frontend" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is available
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Node.js version: $(node --version)" -ForegroundColor Green
Write-Host "[INFO] npm version: $(npm --version)" -ForegroundColor Green

# Navigate to frontend directory
$frontendDir = Join-Path $PSScriptRoot "frontend"
Set-Location $frontendDir

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "[INFO] Installing dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "[INFO] Starting React frontend on http://localhost:8080" -ForegroundColor Green
Write-Host "[INFO] Make sure the API is running on http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host ""

npm run dev

