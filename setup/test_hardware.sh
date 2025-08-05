#!/bin/bash
# Pi-Jarvis Hardware Testing Script
# Phase 1: Verify all hardware components work

echo "🧪 Pi-Jarvis v1.0 - Hardware Testing"
echo "====================================="

# Check audio input devices
echo "🎤 Checking audio input devices..."
arecord -l
echo ""

# Check audio output devices  
echo "🔊 Checking audio output devices..."
aplay -l
echo ""

# Test microphone recording
echo "🎙️ Testing microphone (5-second recording)..."
echo "Speak now..."
arecord -d 5 -f cd -t wav test_input.wav
echo "✅ Recording complete: test_input.wav"
echo ""

# Test audio playback
echo "🔊 Testing audio playback..."
if [ -f "test_input.wav" ]; then
    echo "Playing back your recording..."
    aplay test_input.wav
    echo "✅ Playback complete"
else
    echo "⚠️ No recording found, testing with system sound..."
    speaker-test -t wav -c 2 -l 1
fi
echo ""

# Test TTS
echo "🗣️ Testing text-to-speech..."
espeak "Hello, Pi-Jarvis system test complete"
echo "✅ TTS test complete"
echo ""

# Test camera
echo "📷 Testing camera..."
if command -v libcamera-still &> /dev/null; then
    libcamera-still -o test_camera.jpg --timeout 2000
    if [ -f "test_camera.jpg" ]; then
        echo "✅ Camera test complete: test_camera.jpg"
        ls -lh test_camera.jpg
    else
        echo "❌ Camera test failed - no image captured"
    fi
else
    echo "⚠️ libcamera-still not found, trying raspistill..."
    if command -v raspistill &> /dev/null; then
        raspistill -o test_camera.jpg -t 2000
        if [ -f "test_camera.jpg" ]; then
            echo "✅ Camera test complete: test_camera.jpg"
            ls -lh test_camera.jpg
        else
            echo "❌ Camera test failed - no image captured"
        fi
    else
        echo "❌ No camera capture tools found"
    fi
fi
echo ""

# Check system resources
echo "💾 System resource check..."
echo "CPU Temperature: $(vcgencmd measure_temp)"
echo "Memory usage:"
free -h
echo ""
echo "Disk usage:"
df -h
echo ""

# Check user groups
echo "👤 User group memberships:"
groups $USER
echo ""

# Summary
echo "📋 Hardware Test Summary:"
echo "========================"
echo "Audio input devices: $(arecord -l | grep -c 'card')"
echo "Audio output devices: $(aplay -l | grep -c 'card')"
echo "Test files created:"
ls -la test_*.wav test_*.jpg 2>/dev/null || echo "No test files found"
echo ""
echo "✅ Hardware testing complete!"
echo ""
echo "📖 Review results above and check MANUAL_TASKS.md for verification steps"