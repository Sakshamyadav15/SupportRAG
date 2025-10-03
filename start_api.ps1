# Start FastAPI server using the venv Python
$venvPython = ".\.venv\Scripts\python.exe"
& $venvPython -m uvicorn src.api.main:app --reload --host localhost --port 8000
