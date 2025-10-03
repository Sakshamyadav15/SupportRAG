# Start Enhanced Streamlit frontend with dual vector store support
$venvPython = ".\.venv\Scripts\python.exe"
Write-Host "🎨 Starting Enhanced SupportRAG Frontend..." -ForegroundColor Green
Write-Host "✨ Features: Source Tracking, Resolution Status, Categories" -ForegroundColor Cyan
Write-Host "🔗 URL: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
& $venvPython -m streamlit run frontend\app_enhanced.py
