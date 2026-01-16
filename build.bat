@echo off
chcp 65001 >nul
title AI Humanity - Build EXE
color 0A

echo ========================================
echo    AI Humanity - Сборка EXE файла
echo ========================================
echo.

:: Проверка Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.10+ с python.org
    pause
    exit /b 1
)

echo [1/5] Проверка Python...
python --version
echo.

:: Проверка/создание виртуального окружения
if not exist "venv" (
    echo [2/5] Создание виртуального окружения...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ОШИБКА] Не удалось создать venv
        pause
        exit /b 1
    )
) else (
    echo [2/5] Виртуальное окружение найдено
)
echo.

:: Активация venv
call venv\Scripts\activate.bat

:: Установка зависимостей
echo [3/5] Установка зависимостей...
pip install --upgrade pip >nul 2>nul
pip install -r requirements.txt >nul 2>nul
pip install pyinstaller >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] Не удалось установить зависимости
    pause
    exit /b 1
)
echo Зависимости установлены
echo.

:: Создание директории для сборки
if not exist "dist" mkdir dist
if not exist "build" mkdir build

:: Сборка EXE
echo [4/5] Сборка EXE файла...
echo Это может занять несколько минут...
echo.

pyinstaller --noconfirm --onefile --windowed ^
    --name "AI_Humanity" ^
    --icon "assets\icon.ico" ^
    --add-data "config;config" ^
    --add-data "core;core" ^
    --add-data "gui;gui" ^
    --add-data "modules;modules" ^
    --add-data ".env.example;." ^
    --hidden-import "PyQt6" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "openai" ^
    --hidden-import "TTS" ^
    --hidden-import "torch" ^
    --collect-all "TTS" ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ОШИБКА] Сборка не удалась!
    echo Проверьте логи выше для диагностики
    pause
    exit /b 1
)

echo.
echo [5/5] Сборка завершена!
echo.
echo ========================================
echo    EXE файл создан: dist\AI_Humanity.exe
echo ========================================
echo.

:: Копируем конфигурацию рядом с exe
if exist "dist\AI_Humanity.exe" (
    copy ".env.example" "dist\.env.example" >nul 2>nul
    echo Скопирован .env.example в dist\
)

echo.
echo Для запуска выполните: dist\AI_Humanity.exe
echo Не забудьте создать .env файл с вашими API ключами!
echo.

pause
