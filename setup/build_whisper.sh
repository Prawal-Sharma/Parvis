#!/bin/bash
# Build Whisper.cpp for Raspberry Pi 4 with optimizations
# Phase 2: Speech-to-Text Implementation

set -e  # Exit on any error

echo "🎤 Pi-Jarvis Phase 2: Building Whisper.cpp"
echo "=========================================="

# Create models directory if it doesn't exist
mkdir -p models/whisper

# Clone Whisper.cpp repository
echo "📥 Cloning Whisper.cpp repository..."
if [ ! -d "models/whisper.cpp" ]; then
    cd models
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd ..
else
    echo "ℹ️  Whisper.cpp already cloned"
fi

# Build with Pi 4 optimizations
echo "🔧 Building Whisper.cpp with ARM optimizations..."
cd models/whisper.cpp

# Clean previous builds
make clean || true

# Build with ARM NEON and OpenBLAS optimizations for Pi 4
echo "Building with ARM NEON + OpenBLAS optimizations..."
GGML_OPENBLAS=1 make -j4

# Verify build
echo "✅ Verifying build..."
if [ -f "./main" ] && [ -f "./stream" ]; then
    echo "✅ Whisper.cpp built successfully!"
    ./main --help | head -10
else
    echo "❌ Build failed - binaries not found"
    exit 1
fi

cd ../..

echo ""
echo "🎯 Next: Download Whisper models"
echo "Run: ./setup/download_whisper_models.sh"