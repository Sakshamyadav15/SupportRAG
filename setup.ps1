# SupportRAG Setup Script for Windows
# Run this script to set up the project automatically

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          SupportRAG - Automated Setup Script              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/7] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(9|1[0-9])") {
    Write-Host "✓ Python version OK: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3.9+ required. Found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`n[2/7] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Gray
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n[3/7] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "`n[4/7] Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Setup environment file
Write-Host "`n[5/7] Setting up environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host ".env file already exists" -ForegroundColor Gray
} else {
    Copy-Item .env.example .env
    Write-Host "✓ Created .env file from template" -ForegroundColor Green
    Write-Host "⚠ IMPORTANT: Edit .env and add your API key!" -ForegroundColor Yellow
}

# Create necessary directories
Write-Host "`n[6/7] Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "data/vector_store" | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green

# Initialize vector database
Write-Host "`n[7/7] Initializing vector database..." -ForegroundColor Yellow
Write-Host "This will download the embedding model (~100MB)..." -ForegroundColor Gray

$env_check = python -c "from src.config import settings; exit(0 if settings.gemini_api_key or settings.openai_api_key else 1)"
if ($LASTEXITCODE -eq 0) {
    python scripts/init_vectordb.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Vector database initialized" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to initialize vector database" -ForegroundColor Red
        Write-Host "You can run 'python scripts/init_vectordb.py' manually later" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Skipping database initialization (API key not configured)" -ForegroundColor Yellow
    Write-Host "Please add your API key to .env and run:" -ForegroundColor Yellow
    Write-Host "  python scripts/init_vectordb.py" -ForegroundColor Cyan
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    Setup Complete!                         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Green
Write-Host "1. Edit .env file and add your API key:" -ForegroundColor White
Write-Host "   notepad .env" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Initialize the vector database (if not done):" -ForegroundColor White
Write-Host "   python scripts\init_vectordb.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Start the API server (Terminal 1):" -ForegroundColor White
Write-Host "   uvicorn src.api.main:app --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Start the frontend (Terminal 2):" -ForegroundColor White
Write-Host "   streamlit run frontend\app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Open your browser:" -ForegroundColor White
Write-Host "   http://localhost:8501" -ForegroundColor Cyan
Write-Host ""

Write-Host "For more help, see: docs\QUICKSTART.md" -ForegroundColor Gray
Write-Host ""
