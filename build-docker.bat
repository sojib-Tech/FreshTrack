@echo off
REM Build Docker image for FreshTrack

echo.
echo ========================================
echo   Building FreshTrack Docker Image
echo ========================================
echo.

docker build -t sojib1233/freshtrack:latest .

if %errorlevel% equ 0 (
    echo.
    echo ✅ Build successful!
    echo.
    echo Next steps:
    echo 1. Start with Docker Compose: docker-compose up -d
    echo 2. Or push to Docker Hub: docker push sojib1233/freshtrack:latest
    echo.
) else (
    echo.
    echo ❌ Build failed!
    echo.
)

pause
