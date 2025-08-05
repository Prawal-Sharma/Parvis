# Pi-Jarvis v1.0

**100% Offline Voice + Vision Assistant for Raspberry Pi 4**

## Quick Start

Pi-Jarvis is an always-on assistant that listens for "Hey Pi", processes your speech with local AI models, and responds entirely offline. It can also describe what it sees through the camera using YOLO object detection.

## Features

- 🎤 **Hot-word Detection**: "Hey Pi" activation using Porcupine
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
🏗️ **Current Phase**: Phase 7 - Intent System  
📋 **Next**: Build smart intent recognition for timers, translations, utilities

### ✅ Completed Components
- **System Dependencies**: All build tools, audio libraries, Python packages installed
- **Speech-to-Text**: Whisper.cpp built with ARM optimizations, tiny/small models ready
- **Language Model**: llama.cpp built, TinyLlama 1.1B (638MB) model downloaded and ready
- **Text-to-Speech**: eSpeak TTS engine installed and tested
- **Complete Speech Pipeline**: **STT → LLM → TTS integration working flawlessly**
- **"Parvis" Wake Word Detection**: **Always-on assistant with hot-word activation**
- **Computer Vision System**: **YOLOv8 object detection with "What do you see?" support**

### 🎯 Complete Multi-Modal AI Assistant Ready!
**MAJOR MILESTONE**: Full voice + vision assistant operational! Say "Parvis" → Ask "What do you see?" → Get "I can see a book, a cup, and a stop sign" → Continues listening. Complete offline AI assistant ready for hardware!

**Progress**: **6/9 phases complete (67%)**

See `PHASE_STATUS.md` for detailed phase breakdown and `PROJECT_REFERENCE.md` for technical specifications.

## Installation

*Coming soon - installation instructions will be added as we progress through development phases.*

## Usage

*Coming soon - usage examples will be added once core functionality is implemented.*

## Contributing

This project follows a phased development approach. See the PROJECT_REFERENCE.md for the complete roadmap and technical details.

## License

*To be determined*