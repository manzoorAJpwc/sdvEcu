@echo off

REM ==========================
REM Configuration
REM ==========================
set SYSTEM_NAME=sdvSystem
set SRC_DIR=../systems
set OUT_DIR=executables\%SYSTEM_NAME%

REM Create output directory
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

REM ==========================
REM Build SDV System
REM ==========================
echo Building SDV System...
g++ "%SRC_DIR%\sdvSystem.cpp" -o "%OUT_DIR%\sdv_system.exe"

REM ==========================
REM Build Status
REM ==========================
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully.
    echo Executables generated in:
    echo %OUT_DIR%
) else (
    echo.
    echo Build failed.
)