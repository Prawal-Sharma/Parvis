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

🏗️ **Current Phase**: Project Setup
📋 **Next**: Environment setup and dependency installation

See `PROJECT_REFERENCE.md` for detailed implementation plan and technical specifications.

## Installation

*Coming soon - installation instructions will be added as we progress through development phases.*

## Usage

*Coming soon - usage examples will be added once core functionality is implemented.*

## Contributing

This project follows a phased development approach. See the PROJECT_REFERENCE.md for the complete roadmap and technical details.

## License

*To be determined*