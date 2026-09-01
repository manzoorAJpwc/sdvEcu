@echo off
setlocal

set APP_NAME=adas
set SRC_DIR=..\adas
set VENV_DIR=%SRC_DIR%\.venv
set OUT_DIR=executables\%APP_NAME%

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

echo Building DMS...
pyinstaller --onefile ^
--distpath "%OUT_DIR%" ^
--add-data "%SRC_DIR%\camera_test\dms_python\haarcascade_frontalface_default.xml;." ^
--add-data "%SRC_DIR%\camera_test\dms_python\haarcascade_eye.xml;." ^
"%SRC_DIR%\camera_test\dms_python\dms_harr.py"

echo Building LDW...
pyinstaller --onefile ^
--distpath "%OUT_DIR%" ^
"%SRC_DIR%\ldw\ldw_camera.py"

echo Building FCW...
pyinstaller --onefile ^
--distpath "%OUT_DIR%" ^
--add-data "%SRC_DIR%\fcw\haarcascade_frontalface_default.xml;." ^
--add-data "%SRC_DIR%\fcw\MobileNetSSD_deploy.prototxt;." ^
--add-data "%SRC_DIR%\fcw\MobileNetSSD_deploy.caffemodel;." ^
"%SRC_DIR%\fcw\fcw_object.py"

call deactivate

echo.
echo Build complete.
echo Executables generated under:
echo %OUT_DIR%

endlocal