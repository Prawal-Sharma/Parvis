# Pi-Jarvis v1.0

**100% Offline Voice + Vision Assistant for Raspberry Pi 4**

## Quick Start

Pi-Jarvis is an always-on assistant that listens for "Parvis" [[memory:5211612]], processes your speech with local AI models, and responds entirely offline. It features intelligent intent recognition for timers, translations, time queries, weather info, and computer vision - all running as a production systemd service.

## Features

- 🎤 **Hot-word Detection**: "Parvis" activation using Porcupine [[memory:5211612]]
- 🗣️ **Speech-to-Text**: Real-time transcription with Whisper.cpp
- 🧠 **Local AI**: TinyLlama/Phi-3 models via llama.cpp/Ollama
- 🔊 **Text-to-Speech**: Fast response with eSpeak NG
- 👁️ **Computer Vision**: Object detection with YOLOv8-n
- ⚡ **Intent System**: Timers, translations, summaries, and more
- 🚀 **Auto-Start**: Systemd service for boot-time activation

## Hardware Requirements

- Raspberry Pi 4 (64-bit OS)
- USB microphone + speaker (or ReSpeaker 2-Mic HAT)
- Pi Camera v3
- 32GB+ micro-SD card
- Proper cooling (heatsink/fan)

## Project Structure

```
pi-jarvis/
├── assistant/       # Core Python application and intent routing
├── models/          # AI models and binaries (git-ignored)
├── vision/          # YOLO computer vision components
├── systemd/         # Service configuration files
└── README.md        # This file
```

## Development Status

✅ **Phase 1 COMPLETE**: Environment Setup  
✅ **Phase 2 COMPLETE**: Speech-to-Text (Whisper.cpp)  
✅ **Phase 3 COMPLETE**: Language Model (TinyLlama 1.1B)  
✅ **Phase 4 COMPLETE**: Complete Speech Pipeline  
✅ **Phase 5 COMPLETE**: Hot-word Detection ("Parvis")  
✅ **Phase 6 COMPLETE**: Computer Vision ("What do you see?")  
✅ **Phase 7 COMPLETE**: Intent System (timers, weather, time, translations)  
✅ **Phase 8 COMPLETE**: Production Deployment (systemd service)  
🏗️ **Current Phase**: Phase 9 - Documentation & Demo  
📋 **Next**: Complete documentation and create demonstration video

### ✅ Completed Components
- **System Dependencies**: All build tools, audio libraries, Python packages installed
- **Speech-to-Text**: Whisper.cpp built with ARM optimizations, tiny/small models ready
- **Language Model**: llama.cpp built, TinyLlama 1.1B (638MB) model downloaded and ready
- **Text-to-Speech**: eSpeak TTS engine installed and tested
- **Complete Speech Pipeline**: **STT → Intent → LLM → TTS integration working flawlessly**
- **"Parvis" Wake Word Detection**: **Always-on assistant with hot-word activation** [[memory:5211612]]
- **Computer Vision System**: **YOLOv8 object detection with "What do you see?" support**
- **Intent System**: **Smart intent recognition for timers, weather, time, translations**
- **Production Deployment**: **Systemd service with health monitoring and auto-restart**

### 🎯 Production-Ready AI Assistant Complete!
**MAJOR MILESTONE**: Full production voice + vision assistant operational! Say "Parvis" → Ask "Set a timer for 5 minutes" or "What do you see?" → Get intelligent responses → Continues listening. Complete offline AI assistant running as system service!

**Progress**: **8/9 phases complete (89%)**

See `PHASE_STATUS.md` for detailed phase breakdown and `PROJECT_REFERENCE.md` for technical specifications.

## Installation

### Quick Production Deployment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Prawal-Sharma/Parvis.git
   cd Parvis
   ```

2. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y build-essential cmake git portaudio19-dev espeak espeak-data python3-venv python3-pip ffmpeg
   ```

3. **Set up Python environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Install as system service**:
   ```bash
   ./systemd/install-service.sh
   ```

The installation script will:
- Set up the systemd service for auto-start on boot
- Configure health monitoring and log rotation
- Test the service installation
- Provide management commands

### Manual Testing (Without Hardware)

For development and testing without microphone/camera:
```bash
# Test intent system
python -m assistant.test_intents

# Run in simulation mode
python -m assistant.parvis simulation true
```

## Usage

### Service Management

Once installed, Pi-Jarvis runs automatically as a system service:

```bash
# Check service status
systemctl status pi-jarvis.service

# View live logs
journalctl -u pi-jarvis.service -f

# Restart service
sudo systemctl restart pi-jarvis.service

# Stop service
sudo systemctl stop pi-jarvis.service
```

### Voice Commands

Say **"Parvis"** [[memory:5211612]] to activate, then try:

**Timer Commands:**
- "Set a timer for 5 minutes"
- "Start a 30 second timer"
- "Remind me in 2 hours"

**Time & Date:**
- "What time is it?"
- "What's today's date?"

**Translations:**
- "How do you say hello in Spanish?"
- "Translate water to French"
- "What is goodbye in German?"

**Vision:**
- "What do you see?"
- "Describe what's in front of you"
- "Look around and tell me what's there"

**Weather:**
- "What's the weather like?" (explains offline limitation)

### Health Monitoring

Pi-Jarvis includes comprehensive monitoring:

```bash
# Manual health check
./systemd/health-check.sh

# View health logs
tail -f /var/log/pi-jarvis/health-check.log

# Weekly status report
./systemd/status-report.sh
```

### Hardware-Free Testing

Perfect for development without mic/camera hardware [[memory:5211615]]:

```bash
# Interactive intent testing
python -m assistant.test_intents

# Text-only conversation mode  
python -m assistant.main text

# Full pipeline simulation
python -m assistant.parvis simulation true
```

## Contributing

This project follows a phased development approach. See the PROJECT_REFERENCE.md for the complete roadmap and technical details.

## License

*To be determined*