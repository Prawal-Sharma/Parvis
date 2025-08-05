#!/bin/bash
# Fix FFmpeg dependency conflicts on Raspberry Pi OS

echo "🔧 Fixing FFmpeg dependency conflicts..."
echo "======================================="

# Remove problematic package that's causing conflicts
echo "Removing conflicting libavresample-dev package..."
sudo apt remove --purge libavresample-dev -y || true

# Install core FFmpeg without the problematic libavresample
echo "Installing essential FFmpeg packages..."
sudo apt install -y \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev

# Verify essential packages are installed
echo ""
echo "✅ Verifying essential packages..."
echo "FFmpeg version:"
ffmpeg -version | head -1

echo ""
echo "Essential development packages:"
dpkg -l | grep -E "(build-essential|cmake|portaudio|espeak|libopenblas|python3-dev)" | awk '{print $2, $3}'

echo ""
echo "🎯 Dependency fix complete!"
echo "The libavresample-dev conflict is resolved - this was not critical for Pi-Jarvis"