@echo off
chcp 65001 >nul
title AI Humanity - Launcher
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🤖 AI HUMANITY                            ║
echo ║                    Launcher v2.0                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: ═══════════════════════════════════════════════════════
:: МЕНЮ ВЫБОРА
:: ═══════════════════════════════════════════════════════

echo Выберите действие:
echo.
echo   [1] Запустить приложение (Python)
echo   [2] Собрать EXE файл (PyInstaller)
echo   [3] Запустить EXE (если уже собран)
echo   [4] Выход
echo.

set /p choice="Ваш выбор (1-4): "

if "%choice%"=="1" goto RUN_PYTHON
if "%choice%"=="2" goto BUILD_EXE
if "%choice%"=="3" goto RUN_EXE
if "%choice%"=="4" exit /b 0

echo Неверный выбор. Попробуйте снова.
pause
goto :eof

:: ═══════════════════════════════════════════════════════
:: ЗАПУСК PYTHON ВЕРСИИ
:: ═══════════════════════════════════════════════════════

:RUN_PYTHON
echo.
echo [INFO] Запуск Python версии...
echo.

:: Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не найден!
    echo Скачайте Python с https://www.python.org/downloads/
    echo Убедитесь, что отметили "Add Python to PATH" при установке.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% найден

:: Проверка/создание виртуального окружения
echo.
echo [INFO] Проверка виртуального окружения...

if not exist "venv" (
    echo [INFO] Создание виртуального окружения...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ОШИБКА] Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
    echo [OK] Виртуальное окружение создано
) else (
    echo [OK] Виртуальное окружение найдено
)

:: Активация venv
call venv\Scripts\activate.bat

:: Установка зависимостей
echo.
echo [INFO] Проверка зависимостей...

pip show PyQt6 >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Установка зависимостей (это может занять несколько минут)...
    pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ОШИБКА] Не удалось установить зависимости
        pause
        exit /b 1
    )
    echo [OK] Зависимости установлены
) else (
    echo [OK] Зависимости уже установлены
)

:: Проверка .env файла
echo.
if not exist ".env" (
    if exist ".env.example" (
        echo [ПРЕДУПРЕЖДЕНИЕ] Файл .env не найден!
        echo Создайте .env на основе .env.example и добавьте ваши API ключи
        echo.
        copy .env.example .env >nul 2>&1
        echo [INFO] Создан .env файл. Отредактируйте его перед запуском!
        notepad .env
        pause
    )
)

:: Запуск приложения
echo.
echo ═══════════════════════════════════════════════════════
echo                   ЗАПУСК AI HUMANITY
echo ═══════════════════════════════════════════════════════
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Приложение завершилось с ошибкой
    echo Проверьте логи выше для диагностики
)

pause
goto :eof

:: ═══════════════════════════════════════════════════════
:: СБОРКА EXE
:: ═══════════════════════════════════════════════════════

:BUILD_EXE
echo.
echo [INFO] Запуск сборки EXE...
echo.

if exist "build.bat" (
    call build.bat
) else (
    echo [ОШИБКА] Файл build.bat не найден!
)

pause
goto :eof

:: ═══════════════════════════════════════════════════════
:: ЗАПУСК EXE
:: ═══════════════════════════════════════════════════════

:RUN_EXE
echo.
if exist "dist\AI_Humanity.exe" (
    echo [INFO] Запуск AI_Humanity.exe...
    start "" "dist\AI_Humanity.exe"
) else (
    echo [ОШИБКА] EXE файл не найден!
    echo Сначала выполните сборку (опция 2)
    pause
)
goto :eof
