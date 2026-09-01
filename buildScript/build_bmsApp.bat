@echo off
setlocal

set APP_NAME=bmsApp
set SRC_DIR=..\bmsApp
set OUT_DIR=executables\%APP_NAME%

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo ======================================
echo Building %APP_NAME%
echo Output: %OUT_DIR%
echo ======================================

g++ "%SRC_DIR%\bms_status_service.cpp" -o "%OUT_DIR%\bms_status_service.exe" -lmatio
if errorlevel 1 goto :error

g++ "%SRC_DIR%\inspect_mat.cpp" -o "%OUT_DIR%\inspect_mat.exe" -lmatio
if errorlevel 1 goto :error

g++ "%SRC_DIR%\live_data_simulator.cpp" -o "%OUT_DIR%\live_data_simulator.exe"
if errorlevel 1 goto :error

g++ "%SRC_DIR%\live_soh_monitor.cpp" -o "%OUT_DIR%\live_soh_monitor.exe"
if errorlevel 1 goto :error

g++ "%SRC_DIR%\mat_to_csv_converter.cpp" -o "%OUT_DIR%\mat_to_csv_converter.exe" -lmatio
if errorlevel 1 goto :error

g++ "%SRC_DIR%\soh_calculator.cpp" -o "%OUT_DIR%\soh_calculator.exe"
if errorlevel 1 goto :error

echo.
echo Build Successful
echo Executables generated in:
echo %OUT_DIR%
goto :eof

:error
echo.
echo Build Failed!
exit /b 1