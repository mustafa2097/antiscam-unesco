@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Anti Scam - Phone Access

echo.
echo ============================================================
echo   Anti Scam - Phone Access
echo ============================================================
echo.

set "LAN_IP="
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /r /c:"IPv4 Address"') do (
    set "candidate=%%a"
    set "candidate=!candidate: =!"
    echo !candidate! | findstr /r /c:"^192\.168\." /c:"^10\." /c:"^172\.1[6-9]\." /c:"^172\.2[0-9]\." /c:"^172\.3[0-1]\." >nul && (
        if not defined LAN_IP set "LAN_IP=!candidate!"
    )
)

if not defined LAN_IP (
    echo   Could not find a LAN IPv4. Make sure Wi-Fi is connected.
    pause
    exit /b 1
)

echo   Your PC IP:   !LAN_IP!
echo   Phone URL:    http://!LAN_IP!:5173
echo.
echo   Make sure the phone is on the SAME Wi-Fi.
echo   If Windows Firewall prompts, allow Node.js on Private networks.
echo.
echo ============================================================
echo   Starting frontend (Vite) exposed to the network...
echo ============================================================
echo.

cd /d "c:\Projects\frontend"
call npm run dev -- --host 0.0.0.0
