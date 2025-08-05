#!/bin/bash
# Download Whisper models for Pi-Jarvis
# Phase 2: Speech-to-Text Models

set -e  # Exit on any error

echo "📥 Pi-Jarvis Phase 2: Downloading Whisper Models"
echo "================================================"

# Ensure we're in the right directory
if [ ! -d "models/whisper.cpp" ]; then
    echo "❌ Error: Whisper.cpp not built yet. Run ./setup/build_whisper.sh first"
    exit 1
fi

cd models/whisper.cpp

# Download tiny model (fast, lower accuracy)
echo "📦 Downloading Whisper tiny model (~39MB)..."
if [ ! -f "models/ggml-tiny.bin" ]; then
    bash ./models/download-ggml-model.sh tiny
    echo "✅ Tiny model downloaded"
else
    echo "ℹ️  Tiny model already exists"
fi

# Download small model (better accuracy, slower)
echo "📦 Downloading Whisper small model (~244MB)..."
echo "This may take a few minutes..."
if [ ! -f "models/ggml-small.bin" ]; then
    bash ./models/download-ggml-model.sh small
    echo "✅ Small model downloaded"
else
    echo "ℹ️  Small model already exists"
fi

# List downloaded models
echo ""
echo "📋 Downloaded models:"
ls -lh models/ggml-*.bin

cd ../..

# Copy models to our main models directory for easy access
echo "📂 Copying models to main models directory..."
cp models/whisper.cpp/models/ggml-tiny.bin models/
cp models/whisper.cpp/models/ggml-small.bin models/
echo "✅ Models ready in models/ directory"

echo ""
echo "🎯 Models download complete!"
echo ""
echo "📊 Model comparison:"
echo "  • tiny:  ~39MB,  fast inference, lower accuracy"
echo "  • small: ~244MB, slower inference, better accuracy"
echo ""
echo "🚀 Next: Test speech-to-text functionality"
echo "Run: python -m assistant.test_stt"