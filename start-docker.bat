@echo off
REM Start FreshTrack with Docker Compose

echo.
echo ========================================
echo   Starting FreshTrack (Docker Compose)
echo ========================================
echo.

docker-compose up -d

if %errorlevel% equ 0 (
    echo.
    echo ✅ Services started!
    echo.
    echo Access your app at: http://localhost:8000
    echo.
    echo View logs: docker-compose logs -f
    echo Stop services: docker-compose down
    echo.
) else (
    echo.
    echo ❌ Failed to start services!
    echo.
)

pause
