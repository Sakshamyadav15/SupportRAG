# Start FastAPI server with dual vector stores
$venvPython = ".\.venv\Scripts\python.exe"
Write-Host "Starting SupportRAG API..." -ForegroundColor Green
Write-Host "Features: Dual Vector Stores (FAQ + Tickets), FAISS IVF, Async" -ForegroundColor Cyan
Write-Host "API URL: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
& $venvPython -m uvicorn src.api.main:app --reload --host localhost --port 8000
