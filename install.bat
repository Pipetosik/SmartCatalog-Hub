@echo off
chcp 65001 >nul
title SmartCatalog Hub - Установка и Запуск

echo ===================================================
echo       SmartCatalog Hub - Быстрая установка
echo ===================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не обнаружен в системе!
    echo Пожалуйста, установите Python 3.10+ с сайта https://www.python.org/
    echo Не забудьте поставить галочку "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

if not exist "venv" (
    echo [*] Создание виртуального окружения (venv)...
    python -m venv venv
)

echo [*] Активация окружения и установка зависимостей...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [*] Регистрация автозапуска и ярлыков...
python install_autostart.py

echo.
echo ===================================================
echo   Установка успешно завершена!
echo   Запуск SmartCatalog Hub...
echo ===================================================
echo.

python app.py
pause
