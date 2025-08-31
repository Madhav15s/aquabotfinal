@echo off
echo Starting IME Hub Maritime AI Assistant...
echo.
echo Installing dependencies...
pip install -r backend/requirements.txt
echo.
echo Starting backend server...
cd backend
python main.py
pause 