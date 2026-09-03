#!/bin/bash

# ==========================
# Configuration
# ==========================
SYSTEM_NAME="sdvSystem"
SRC_DIR="../systems"

# One level above buildScript
ROOT_DIR=".."
OUT_DIR="${ROOT_DIR}/out/executables/${SYSTEM_NAME}"

# Create output directory
mkdir -p "${OUT_DIR}"

# ==========================
# Build SDV System
# ==========================
echo "Building SDV System..."

g++ "${SRC_DIR}/sdvSystem.cpp" \
    -o "${OUT_DIR}/sdv_system"

# ==========================
# Build Status
# ==========================
if [ $? -eq 0 ]; then
    echo
    echo "Build completed successfully."
    echo "Executables generated in:"
    echo "${OUT_DIR}"
else
    echo
    echo "Build failed."
    exit 1
fi