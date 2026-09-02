#!/bin/bash

set -e

APP_NAME="appBms"
SRC_DIR="../appBms"

# One level above buildScript
ROOT_DIR=".."

OUT_DIR="${ROOT_DIR}/out/executables/${APP_NAME}"
BUILD_DIR="${ROOT_DIR}/out/build"

mkdir -p "${OUT_DIR}"

echo "======================================"
echo "Building ${APP_NAME}"
echo "Output: ${OUT_DIR}"
echo "======================================"

g++ "${SRC_DIR}/bms_status_service.cpp" \
    -o "${OUT_DIR}/bms_status_service" \
    -lmatio

g++ "${SRC_DIR}/inspect_mat.cpp" \
    -o "${OUT_DIR}/inspect_mat" \
    -lmatio

g++ "${SRC_DIR}/live_data_simulator.cpp" \
    -o "${OUT_DIR}/live_data_simulator"

g++ "${SRC_DIR}/live_soh_monitor.cpp" \
    -o "${OUT_DIR}/live_soh_monitor"

g++ "${SRC_DIR}/mat_to_csv_converter.cpp" \
    -o "${OUT_DIR}/mat_to_csv_converter" \
    -lmatio

g++ "${SRC_DIR}/soh_calculator.cpp" \
    -o "${OUT_DIR}/soh_calculator"

echo
echo "Build Successful"
echo "Executables generated in:"
echo "${OUT_DIR}"