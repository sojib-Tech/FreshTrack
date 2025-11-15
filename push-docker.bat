@echo off
REM Push FreshTrack image to Docker Hub

echo.
echo ========================================
echo   Pushing to Docker Hub
echo ========================================
echo.

echo Step 1: Logging in to Docker Hub...
docker login

if %errorlevel% equ 0 (
    echo.
    echo Step 2: Pushing image...
    docker push sojib1233/freshtrack:latest
    
    if %errorlevel% equ 0 (
        echo.
        echo ✅ Push successful!
        echo.
        echo View on Docker Hub: https://hub.docker.com/r/sojib1233/freshtrack
        echo.
    ) else (
        echo.
        echo ❌ Push failed!
        echo.
    )
) else (
    echo.
    echo ❌ Login failed!
    echo.
)

pause
