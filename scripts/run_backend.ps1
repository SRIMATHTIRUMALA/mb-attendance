# Start Backend Server (FastAPI with Uvicorn)
$env:PYTHONPATH = "backend"
$env:TIMEZONE = "Asia/Kolkata"
Write-Host "Starting MB Solar Hub Backend Server on http://localhost:8000..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --port 8000
