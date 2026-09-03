#!/bin/bash

set -e

APP_NAME=appAdas

SRC_DIR="../appAdas"
VENV_DIR="../tools/pyEnv/sdvEnv"

# One level above buildScript
ROOT_DIR=".."

OUT_DIR="${ROOT_DIR}/out/executables/${APP_NAME}"
BUILD_DIR="${ROOT_DIR}/out/build"

mkdir -p "${OUT_DIR}"
mkdir -p "${BUILD_DIR}"

echo "Activating virtual environment..."
source "${VENV_DIR}/bin/activate"

echo "Building DMS..."
python -m PyInstaller \
  --clean \
  --onefile \
  --collect-all cv2 \
  --distpath "${OUT_DIR}" \
  --workpath "${BUILD_DIR}/dms" \
  --specpath "${BUILD_DIR}" \
  --add-data "../${SRC_DIR}/lib_haarcascade/haarcascade_frontalface_default.xml:." \
  --add-data "../${SRC_DIR}/lib_haarcascade/haarcascade_eye.xml:." \
  "${SRC_DIR}/dms/dmsApp.py"

echo "Building LDW..."
python -m PyInstaller \
  --clean \
  --onefile \
  --distpath "${OUT_DIR}" \
  --workpath "${BUILD_DIR}/ldw" \
  --specpath "${BUILD_DIR}" \
  "${SRC_DIR}/ldw/ldw_camera.py"

echo "Building FCW..."
python -m PyInstaller \
  --clean \
  --onefile \
  --distpath "${OUT_DIR}" \
  --workpath "${BUILD_DIR}/fcw" \
  --specpath "${BUILD_DIR}" \
  --add-data "../${SRC_DIR}/lib_haarcascade/haarcascade_frontalface_default.xml:." \
  --add-data "../${SRC_DIR}/lib_objDet/MobileNetSSD_deploy.prototxt:." \
  --add-data "../${SRC_DIR}/lib_objDet/MobileNetSSD_deploy.caffemodel:." \
  "${SRC_DIR}/fcw/fcw_object.py"

#deactivate

echo
echo "Build complete."
echo "Executables:"
echo "  ${OUT_DIR}"
echo
echo "Build artifacts:"
echo "  ${BUILD_DIR}"