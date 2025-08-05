#!/bin/bash
# Pi-Jarvis Python Environment Setup Script
# Phase 1: Python Dependencies Installation

set -e  # Exit on any error

echo "🐍 Pi-Jarvis v1.0 - Python Environment Setup"
echo "============================================="

# Check if we're in the project directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the Pi-Jarvis project directory"
    exit 1
fi

# Create Python virtual environment
echo "📦 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and setuptools
echo "⬆️  Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📚 Installing Python dependencies..."
echo "This may take several minutes on Pi 4..."

# Install core dependencies first
pip install \
    numpy \
    pydantic \
    asyncio-mqtt

# Install audio dependencies
echo "🎤 Installing audio processing packages..."
pip install \
    pyaudio \
    scipy

# Install TTS
echo "🔊 Installing text-to-speech packages..."
pip install pyttsx3

# Install hot-word detection
echo "🎯 Installing Porcupine wake-word detection..."
pip install pvporcupine

# Install vision dependencies
echo "👁️ Installing computer vision packages..."
pip install \
    opencv-python \
    ultralytics \
    pillow

# Install development tools
echo "🛠️ Installing development tools..."
pip install \
    pytest \
    pytest-asyncio \
    black \
    flake8 \
    mypy

echo ""
echo "✅ Python environment setup complete!"
echo ""
echo "📋 Environment activated. To use Pi-Jarvis:"
echo "1. Always activate the environment first: source venv/bin/activate"
echo "2. Run the assistant: python -m assistant.main"
echo ""
echo "🧪 Next: Test your hardware components (see MANUAL_TASKS.md)"
echo "   - Test microphone: arecord -d 5 test.wav && aplay test.wav"
echo "   - Test speaker: espeak 'Hello Pi-Jarvis'"  
echo "   - Test camera: libcamera-still -o test.jpg"