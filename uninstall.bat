@echo off
chcp 65001 >nul
title SmartCatalog Hub - Чистое удаление службы

echo ===================================================
echo     SmartCatalog Hub - Удаление и Очистка
echo ===================================================
echo.

echo [*] Завершение фоновых процессов SmartCatalog...
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq SmartCatalog*" >nul 2>&1

echo [*] Удаление задачи автозапуска из Планировщика Windows...
schtasks /delete /tn "SmartCatalogHubService" /f >nul 2>&1

echo [*] Удаление ярлыков автозапуска...
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
if exist "%STARTUP_DIR%\SmartCatalog Hub.lnk" del /f /q "%STARTUP_DIR%\SmartCatalog Hub.lnk" >nul 2>&1

echo.
echo ===================================================
echo   Служба и автозапуск успешно удалены!
echo   Локальные файлы сохранены в текущей папке.
echo ===================================================
echo.
pause
