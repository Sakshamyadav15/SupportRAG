# Start Enhanced FastAPI server with dual vector stores
$venvPython = ".\.venv\Scripts\python.exe"
Write-Host "🚀 Starting Enhanced SupportRAG API..." -ForegroundColor Green
Write-Host "📚 Features: Dual Vector Stores (FAQ + Tickets)" -ForegroundColor Cyan
Write-Host "🔗 API URL: http://localhost:8000" -ForegroundColor Yellow
Write-Host "📖 Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
& $venvPython -m uvicorn src.api.main_enhanced:app --reload --host localhost --port 8000
