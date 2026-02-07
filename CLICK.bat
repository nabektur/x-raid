@echo off
chcp 65001 > nul
title X-Raid
color 0A

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не установлен в системе!
    echo Установите Python с сайта: https://www.python.org/
    pause
    exit /b 1
)

pip install --upgrade pip
pip install -r requirements.txt

python main.py

if errorlevel (
    echo.
    echo ========================================
    echo [ERROR] Произошла ошибка!
    pause
    exit /b 1
)