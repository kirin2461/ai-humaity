@echo off
setlocal enabledelayedexpansion

title AI Humanity - Launcher
color 0B

echo.
echo  ========================================
echo        AI HUMANITY - Launcher v2.1
echo  ========================================
echo.

:: Find Python
set PYTHON_CMD=

:: Try python3 first
where python3 >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python3
    goto :FOUND_PYTHON
)

:: Try python
where python >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python
    goto :FOUND_PYTHON
)

:: Try py launcher
where py >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=py
    goto :FOUND_PYTHON
)

:: Python not found
echo [ERROR] Python not found!
echo Please install Python from https://python.org
echo Make sure to check "Add Python to PATH" during installation.
pause
exit /b 1

:FOUND_PYTHON
echo [OK] Found Python: %PYTHON_CMD%
echo.

:MENU
echo  Select action:
echo.
echo   [1] Run application (Python)
echo   [2] Build EXE (PyInstaller)
echo   [3] Run EXE (if built)
echo   [4] Install dependencies
echo   [5] Exit
echo.

set /p choice="Your choice (1-5): "

if "%choice%"=="1" goto RUN_PYTHON
if "%choice%"=="2" goto BUILD_EXE
if "%choice%"=="3" goto RUN_EXE
if "%choice%"=="4" goto INSTALL_DEPS
if "%choice%"=="5" exit /b 0

echo Invalid choice. Try again.
pause
goto :MENU

:RUN_PYTHON
echo.
echo [INFO] Starting AI Humanity...
echo.
%PYTHON_CMD% main.py
if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed or error occurred.
    pause
)
goto :MENU

:BUILD_EXE
echo.
echo [INFO] Building EXE with PyInstaller...
echo.
%PYTHON_CMD% -m pip install pyinstaller --quiet
if exist build.bat (
    call build.bat
) else (
    %PYTHON_CMD% -m PyInstaller --onefile --windowed --name=AI_Humanity main.py
)
echo.
echo [INFO] Build complete! Check dist folder.
pause
goto :MENU

:RUN_EXE
echo.
if exist "dist\AI_Humanity.exe" (
    echo [INFO] Starting AI_Humanity.exe...
    start "" "dist\AI_Humanity.exe"
) else (
    echo [ERROR] EXE not found!
    echo Please build it first using option [2].
)
pause
goto :MENU

:INSTALL_DEPS
echo.
echo [INFO] Installing dependencies...
echo.
if exist requirements.txt (
    %PYTHON_CMD% -m pip install -r requirements.txt
    echo.
    echo [OK] Dependencies installed!
) else (
    echo [ERROR] requirements.txt not found!
)
pause
goto :MENU
