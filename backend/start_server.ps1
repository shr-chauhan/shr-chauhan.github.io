# PowerShell script to start FastAPI server with virtual environment
Set-Location $PSScriptRoot
.\venv\Scripts\Activate.ps1
python fastapi_app.py

