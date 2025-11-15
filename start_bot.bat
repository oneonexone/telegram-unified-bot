@echo off
chcp 65001 >nul
title Telegram Bot - Auto Start
color 0C

REM Переходим в папку скрипта
cd /d "%~dp0"

echo ========================================
echo 🤖 Telegram Unified Bot
echo ========================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo Установите Python 3.7 или выше
    pause
    exit /b 1
)

REM Проверяем config.json
if not exist "config.json" (
    echo ❌ Файл config.json не найден!
    echo Создайте его на основе config_example.json
    pause
    exit /b 1
)

REM Проверяем session
if not exist "session.session" (
    echo ⚠️  Первая авторизация! Запускается interactive mode...
    python bot.py
    echo.
    echo ✅ Авторизация завершена!
    echo.
)

REM Запускаем бота
echo 🚀 Запуск бота...
echo.
python unified_bot.py --config config.json

REM Если бот упал, перезапускаем
echo.
echo ⚠️  Бот завершился. Перезапуск через 10 секунд...
timeout /t 10 /nobreak
goto :eof


