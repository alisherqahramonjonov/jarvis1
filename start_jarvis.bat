@echo off
title JARVIS Holographic AI Assistant
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo     J.A.R.V.I.S HOLOGRAPHIC AI ASSISTANT (v3.0)
echo ========================================================
echo  [1] Futuristik Hologramma HUD Oynasi (Tavsiya etiladi)
echo  [2] Konsol / Terminal Rejimi
echo ========================================================
set /p choice="Rejimni tanlang [1/2, standart 1]: "

if "%choice%"=="2" (
    python main.py
) else (
    python app.py
)
pause
