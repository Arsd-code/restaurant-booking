@echo off
echo ========================================
echo Restaurant Booker - Quick Deploy
echo ========================================
echo.

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting server...
echo.
echo Server will be available at: http://localhost:5000
echo Admin panel: http://localhost:5000/admin
echo Login: admin@restaurant.com / admin123
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python run_server.py

pause 