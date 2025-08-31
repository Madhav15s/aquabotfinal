Write-Host "Starting IME Hub Maritime AI Assistant..." -ForegroundColor Green
Write-Host ""

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r backend/requirements.txt

Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Yellow
Set-Location backend
python main.py

Read-Host "Press Enter to continue..." 