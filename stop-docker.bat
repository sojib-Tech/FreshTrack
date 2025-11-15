@echo off
REM Stop and remove all FreshTrack containers

echo.
echo ========================================
echo   Stopping FreshTrack
echo ========================================
echo.

docker-compose down

echo.
echo ✅ Services stopped!
echo.

pause
