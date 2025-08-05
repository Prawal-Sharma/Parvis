#!/bin/bash
# Pi-Jarvis System Dependencies Installation Script
# Phase 1: Environment Setup

set -e  # Exit on any error

echo "🚀 Pi-Jarvis v1.0 - System Dependencies Installation"
echo "=================================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install build essentials
echo "🔧 Installing build tools..."
sudo apt install -y \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    pkg-config

# Install audio dependencies
echo "🎤 Installing audio dependencies..."
sudo apt install -y \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1-dev \
    pulseaudio \
    alsa-utils

# Install OpenBLAS for optimized math operations
echo "⚡ Installing OpenBLAS for Pi optimization..."
sudo apt install -y \
    libopenblas-dev \
    liblapack-dev \
    gfortran

# Install TTS engine
echo "🔊 Installing eSpeak TTS engine..."
sudo apt install -y \
    espeak \
    espeak-data \
    libespeak-dev

# Install multimedia tools
echo "📹 Installing multimedia dependencies..."
sudo apt install -y \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libavresample-dev

# Install Python development tools
echo "🐍 Installing Python development tools..."
sudo apt install -y \
    python3-dev \
    python3-venv \
    python3-pip \
    python3-setuptools \
    python3-wheel

# Install camera and OpenCV dependencies  
echo "👁️ Installing camera and vision dependencies..."
sudo apt install -y \
    libcamera-dev \
    libcamera-tools \
    python3-opencv \
    libopencv-dev

# Add user to required groups
echo "👤 Adding user to audio/video groups..."
sudo usermod -a -G audio,video,gpio,i2c,spi $USER

# Enable camera interface
echo "📷 Enabling camera interface..."
sudo raspi-config nonint do_camera 0

echo ""
echo "✅ System dependencies installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Reboot your Pi to apply group changes: sudo reboot"
echo "2. After reboot, run: source setup/setup_python_env.sh"
echo "3. Test hardware components as outlined in MANUAL_TASKS.md"
echo ""
echo "⚠️  IMPORTANT: You MUST reboot before proceeding to activate group changes!"