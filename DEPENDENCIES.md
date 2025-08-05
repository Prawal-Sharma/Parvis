# Pi-Jarvis Dependencies and Technology Stack

This document provides comprehensive information about all technologies, dependencies, and software components used in Pi-Jarvis.

## Technology Stack Overview

Pi-Jarvis is built using a carefully selected stack of open-source technologies optimized for offline operation on Raspberry Pi 4.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Pi-Jarvis Technology Stack                   │
├─────────────────────────────────────────────────────────────────┤
│  Application Layer                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Python    │  │   AsyncIO   │  │      Pydantic          │  │
│  │   3.11+     │  │   Runtime   │  │   Configuration        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  AI/ML Layer                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Whisper.cpp │  │ TinyLlama   │  │       YOLOv8-n         │  │
│  │     STT     │  │    LLM      │  │   Object Detection     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Audio/Video Layer                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Porcupine   │  │   eSpeak    │  │      Pi Camera         │  │
│  │  Hotword    │  │     TTS     │  │     Interface          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  System Layer                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Systemd   │  │    Linux    │  │    Raspberry Pi OS     │  │
│  │   Service   │  │   Kernel    │  │       64-bit           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Core AI/ML Technologies

### 1. Whisper.cpp - Speech-to-Text

**Purpose**: Real-time audio transcription
**Version**: Latest stable release
**License**: MIT License
**Why Chosen**: 
- Optimized C++ implementation of OpenAI Whisper
- ARM NEON optimizations for Raspberry Pi
- Multiple model sizes (tiny: 75MB, small: 466MB)
- No GPU requirements, CPU-optimized

**Key Features**:
- Real-time transcription capability
- Multiple language support
- Quantized models for memory efficiency
- Hardware acceleration via OpenBLAS

**Installation**:
```bash
# Built from source with Pi optimizations
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make GGML_OPENBLAS=1  # OpenBLAS acceleration
```

**Models Used**:
- **ggml-tiny.bin** (75MB): Fast, basic accuracy for testing
- **ggml-small.bin** (466MB): Better accuracy for production

### 2. TinyLlama - Large Language Model

**Purpose**: General conversation and text generation
**Version**: TinyLlama-1.1B-Chat-v1.0
**Quantization**: Q4_K_M (638MB)
**License**: Apache 2.0
**Why Chosen**:
- Optimized for resource-constrained devices
- Strong performance at 1.1B parameters
- Compatible with llama.cpp and Ollama
- Excellent instruction following

**Key Features**:
- Fast inference on CPU
- Low memory footprint with quantization
- Chat-optimized training
- Multi-turn conversation capability

**Backend Options**:
1. **llama.cpp**: Direct C++ implementation
2. **Ollama**: User-friendly model serving

**Performance**:
- Response time: <3 seconds on Pi 4
- Memory usage: ~300MB when loaded
- Context length: 2048 tokens

### 3. YOLOv8-n - Computer Vision

**Purpose**: Real-time object detection
**Version**: YOLOv8-nano
**Framework**: Ultralytics
**License**: AGPL-3.0
**Why Chosen**:
- Smallest YOLO model (6MB)
- Real-time inference on CPU
- 80+ object classes
- Excellent accuracy/speed tradeoff

**Key Features**:
- ~6 FPS on Raspberry Pi 4
- Pre-trained on COCO dataset
- Confidence-based filtering
- Bounding box detection

**Model Details**:
- Parameters: 3.2M
- Model size: 6.0MB
- Input resolution: 640x640
- Output: Object classes, confidence scores, bounding boxes

## Audio Technologies

### 1. Porcupine - Wake Word Detection

**Purpose**: Always-on "Parvis" wake word detection
**Provider**: Picovoice
**License**: Apache 2.0 (Free tier)
**Why Chosen**:
- Ultra-low CPU usage (~1%)
- High accuracy, low false positives
- Custom wake word support
- Cross-platform compatibility

**Key Features**:
- Real-time processing
- Configurable sensitivity
- Multiple wake word support
- Hardware-optimized algorithms

**Configuration**:
- Wake word: "Parvis"
- Sensitivity: 0.5 (configurable)
- Sample rate: 16kHz
- Frame length: 512 samples

### 2. eSpeak NG - Text-to-Speech

**Purpose**: Voice synthesis for responses
**Version**: Latest stable
**License**: GPL v3
**Why Chosen**:
- Lightweight and fast
- No network requirements
- Multiple voice options
- Excellent Pi 4 performance

**Key Features**:
- Multiple languages and voices
- Configurable speech rate
- SSML support
- Low latency synthesis

**Configuration**:
- Voice: English (default)
- Speed: 175 WPM
- Volume: Adjustable
- Output: Direct audio or file

### 3. PortAudio - Audio I/O

**Purpose**: Cross-platform audio input/output
**Version**: v19 stable
**License**: MIT-style license
**Why Chosen**:
- Reliable cross-platform audio
- Low-latency audio streaming
- USB microphone support
- Raspberry Pi optimized

**Features**:
- Real-time audio processing
- Multiple device support
- Configurable buffer sizes
- Hardware abstraction

## Python Framework and Libraries

### 1. Python 3.11+

**Purpose**: Main application runtime
**Version**: 3.11+ (recommended 3.11 for Pi OS)
**Why Chosen**:
- Excellent async/await support
- Strong typing with type hints
- Comprehensive standard library
- Active community and ecosystem

**Key Features Used**:
- AsyncIO for concurrent processing
- Type hints for code reliability
- Context managers for resource handling
- Exception handling and logging

### 2. Pydantic - Configuration Management

**Purpose**: Type-safe configuration and data validation
**Version**: Latest v2.x
**License**: MIT
**Why Chosen**:
- Runtime type validation
- Automatic documentation generation
- Environment variable integration
- Excellent developer experience

**Usage in Pi-Jarvis**:
```python
class STTConfig(BaseModel):
    model_path: str = Field(default="models/ggml-tiny.bin")
    language: str = Field(default="en")
    max_tokens: int = Field(default=500)
```

### 3. AsyncIO - Concurrent Processing

**Purpose**: Asynchronous programming framework
**Built-in**: Python standard library
**Why Chosen**:
- Non-blocking I/O operations
- Efficient resource utilization
- Perfect for I/O-bound tasks
- Native Python integration

**Usage Patterns**:
- Async speech pipeline processing
- Concurrent audio and vision processing
- Non-blocking file I/O
- Timer management

### 4. Additional Python Libraries

**Core Dependencies**:
```python
# Audio processing
pyaudio>=0.2.11          # Audio I/O interface
wave>=0.0.2              # WAV file handling

# Computer vision
ultralytics>=8.0.0       # YOLOv8 implementation  
opencv-python>=4.5.0     # Image processing
pillow>=9.0.0            # Image manipulation
numpy>=1.21.0            # Numerical computing

# HTTP and networking
requests>=2.28.0         # HTTP client for Ollama
httpx>=0.24.0           # Async HTTP client

# System integration
psutil>=5.9.0           # System monitoring
python-systemd>=234     # Systemd integration
```

**Development Dependencies**:
```python
# Testing
pytest>=7.0.0          # Testing framework
pytest-asyncio>=0.21.0 # Async testing support

# Code quality
black>=22.0.0           # Code formatting
flake8>=5.0.0          # Linting
mypy>=1.0.0            # Type checking

# Documentation
sphinx>=5.0.0          # Documentation generation
```

## System Technologies

### 1. Systemd - Service Management

**Purpose**: Production deployment and service management
**Built-in**: Linux system component
**Why Chosen**:
- Automatic startup on boot
- Process monitoring and restart
- Resource limit enforcement
- Logging integration

**Features Used**:
- Service dependencies (network, audio)
- Automatic restart policies
- Security sandboxing
- Resource limits (memory, CPU)
- Log management integration

### 2. Logrotate - Log Management

**Purpose**: Automated log rotation and cleanup
**Built-in**: Linux system component  
**Why Chosen**:
- Prevents disk space exhaustion
- Configurable retention policies
- Automatic compression
- Service integration

**Configuration**:
- Daily rotation
- 30-day retention
- Compression after 1 day
- Automatic cleanup

### 3. Cron - Task Scheduling

**Purpose**: Automated maintenance tasks
**Built-in**: Linux system component
**Why Chosen**:
- Reliable task scheduling
- System-level integration
- Simple configuration
- Log integration

**Scheduled Tasks**:
- Health checks: Every 5 minutes
- Daily maintenance: 2:30 AM
- Weekly reports: Sundays 9:00 AM

## Hardware Integration

### 1. Raspberry Pi Camera Interface

**Purpose**: Image capture for computer vision
**Technology**: Pi Camera v3 integration
**Interface**: CSI (Camera Serial Interface)
**Why Chosen**:
- Native Pi integration
- High-quality image sensor
- Hardware-accelerated processing
- Low latency capture

**Specifications**:
- Resolution: Up to 12MP
- Video: 1080p @ 30fps
- Interface: 15-pin CSI connector
- Autofocus: Yes (v3)

### 2. USB Audio Interface

**Purpose**: Microphone and speaker connectivity
**Standards**: USB Audio Class 1.0/2.0
**Why Chosen**:
- Plug-and-play compatibility
- Better audio quality than Pi audio
- USB power delivery
- Multiple device support

**Compatible Devices**:
- USB microphones (Blue Yeti, Audio-Technica, etc.)
- USB speakers and DACs
- ReSpeaker HATs
- Generic USB audio adapters

### 3. OpenBLAS - Mathematical Acceleration

**Purpose**: Optimized linear algebra operations
**Version**: Latest stable
**License**: BSD 3-Clause
**Why Chosen**:
- ARM NEON optimizations
- Significant performance improvement
- Multi-threading support
- Whisper.cpp integration

**Performance Impact**:
- 2-3x faster matrix operations
- Reduced STT processing time
- Lower CPU usage
- Better energy efficiency

## Development Tools

### 1. Git - Version Control

**Purpose**: Source code management
**Built-in**: Most Linux distributions
**Features Used**:
- Branch-based development
- Commit history tracking
- Remote repository sync
- Tag-based releases

### 2. Virtual Environment

**Purpose**: Python dependency isolation
**Technology**: Python venv
**Why Chosen**:
- Dependency isolation
- Clean package management
- Development/production parity
- Easy deployment

**Structure**:
```
venv/
├── bin/           # Executables
├── lib/           # Python packages
├── include/       # Header files
└── pyvenv.cfg     # Configuration
```

### 3. Logging Framework

**Purpose**: Application monitoring and debugging
**Technology**: Python logging + systemd journal
**Features**:
- Multiple log levels
- Structured logging
- Automatic rotation
- System integration

**Log Destinations**:
- Application logs: `/home/raspberry/Desktop/Parvis/logs/`
- System logs: systemd journal
- Health logs: `/var/log/pi-jarvis/`

## Performance Optimizations

### 1. Model Quantization

**Whisper Models**:
- Format: GGML quantized format
- Precision: 16-bit → 8-bit/4-bit
- Size reduction: ~50-75%
- Performance: Minimal accuracy loss

**LLM Models**:
- Format: GGUF (latest llama.cpp format)
- Quantization: Q4_K_M (4-bit)
- Size: 1.1B params → 638MB
- Memory usage: ~300MB during inference

### 2. ARM NEON Optimizations

**Whisper.cpp**:
- SIMD instructions for matrix operations
- ARM64 specific optimizations
- Multi-core utilization
- Cache-friendly memory access

**Performance Improvements**:
- 2-3x faster inference
- Lower power consumption
- Better thermal characteristics
- Reduced processing latency

### 3. Async Architecture Benefits

**Concurrency**:
- Non-blocking I/O operations
- Parallel component processing
- Resource sharing efficiency
- Better user experience

**Resource Utilization**:
- Lower memory overhead vs threading
- Efficient CPU utilization
- Reduced context switching
- Better scalability

## Security Considerations

### 1. Dependency Security

**Practices**:
- Regular dependency updates
- Security vulnerability scanning
- Pinned version management
- Minimal dependency principle

**Tools**:
- `pip audit` for vulnerability checking
- Virtual environment isolation
- Regular security updates
- Dependency review process

### 2. System Security

**Systemd Hardening**:
- Service isolation
- Resource limits
- Filesystem restrictions
- Privilege dropping

**Network Security**:
- No external network dependencies
- Local-only processing
- Air-gapped operation capability
- Data privacy protection

## Installation Requirements

### 1. System Requirements

**Hardware**:
- Raspberry Pi 4 (4GB+ RAM recommended)
- 32GB+ micro-SD card (Class 10)
- USB microphone
- Speakers or headphones
- Pi Camera v3 (optional)

**Software**:
- Raspberry Pi OS 64-bit (Bookworm)
- Python 3.11+
- Git
- Build tools (cmake, gcc)

### 2. Dependency Installation

**System Packages**:
```bash
sudo apt update
sudo apt install -y \
    build-essential \
    cmake \
    git \
    portaudio19-dev \
    espeak \
    espeak-data \
    python3-venv \
    python3-pip \
    ffmpeg \
    libopenblas-dev
```

**Python Environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Storage Requirements

**Disk Space**:
- Base system: ~8GB
- Dependencies: ~2GB
- AI models: ~1.5GB
- Logs and data: ~500MB
- **Total**: ~12GB minimum

**Model Storage**:
```
models/
├── ggml-tiny.bin          # 75MB (Whisper tiny)
├── ggml-small.bin         # 466MB (Whisper small)  
├── tinyllama-chat.gguf    # 638MB (TinyLlama)
└── yolov8n.pt            # 6MB (YOLOv8-nano)
```

This comprehensive technology stack provides a robust, efficient, and maintainable foundation for offline AI assistance on Raspberry Pi 4 hardware.