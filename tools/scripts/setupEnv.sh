#!/bin/bash

set -e

# SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="."

echo "======================================"
echo "Updating package lists"
echo "======================================"
sudo apt update

echo "======================================"
echo "Python Environment"
echo "======================================"
sudo apt install -y \
    python3 \
    python3-venv \
    python3-pip

echo "======================================"
echo "C/C++ Build Tools"
echo "======================================"
sudo apt install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config

echo "======================================"
echo "MAT File Support"
echo "======================================"
sudo apt install -y \
    libmatio-dev

echo "======================================"
echo "OpenCV Runtime Dependencies"
echo "======================================"
sudo apt install -y \
    libgl1 \
    libegl1 \
    ffmpeg \
    v4l-utils

echo "======================================"
echo "PyQt5 Runtime Dependencies"
echo "======================================"
sudo apt install -y \
    libfontconfig1 \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    libxcb-randr0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xkb1 \
    libx11-xcb1

echo "======================================"
echo "Activating sdvEnv"
echo "======================================"

source "${REPO_ROOT}/tools/pyEnv/sdvEnv/bin/activate"

echo "Virtual Environment:"
echo "$VIRTUAL_ENV"

echo "Python:"
which python

echo "Pip:"
which pip

echo "======================================"
echo "Upgrading pip"
echo "======================================"

pip install --upgrade pip

echo "======================================"
echo "Installing Python Packages"
echo "======================================"

pip install -r "${REPO_ROOT}/appAdas/requirements.txt"
pip install -r "${REPO_ROOT}/appEdge/requirements.txt"

echo "======================================"
echo "Installed Package Versions"
echo "======================================"

python --version
pip show pyinstaller | grep Version || true
pip show flask | grep Version || true
pip show PyQt5 | grep Version || true
pip show opencv-python | grep Version || true

echo "======================================"
echo "Environment Setup Complete"
echo "======================================"