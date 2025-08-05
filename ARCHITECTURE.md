# Pi-Jarvis Architecture Documentation

## Overview

Pi-Jarvis is a production-ready, offline voice and vision AI assistant designed for Raspberry Pi 4. The system uses a modular, event-driven architecture that processes voice commands through an intelligent intent system before falling back to a large language model for general conversation.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Pi-Jarvis System                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────┐ │
│  │   Hotword   │    │   Speech     │    │     Intent          │ │
│  │  Detection  │───▶│   Pipeline   │───▶│   Classification    │ │
│  │ (Porcupine) │    │ (STT→LLM→TTS)│    │   & Handling        │ │
│  └─────────────┘    └──────────────┘    └─────────────────────┘ │
│         │                   │                      │            │
│         │                   │                      ▼            │
│         │                   │            ┌─────────────────────┐ │
│         │                   │            │   Intent Handlers   │ │
│         │                   │            │ • Timer             │ │
│         │                   │            │ • Weather           │ │
│         │                   │            │ • Time/Date         │ │
│         │                   │            │ • Translation       │ │
│         │                   │            │ • Vision Requests   │ │
│         │                   │            └─────────────────────┘ │
│         │                   │                      │            │
│         │                   ▼                      │            │
│  ┌─────────────┐    ┌──────────────┐              │            │
│  │   Vision    │◀───│   Language   │◀─────────────┘            │
│  │  Pipeline   │    │    Model     │                           │
│  │  (YOLOv8)   │    │ (TinyLlama)  │                           │
│  └─────────────┘    └──────────────┘                           │
├─────────────────────────────────────────────────────────────────┤
│                     System Services                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Health    │  │    Log      │  │      Production         │  │
│  │ Monitoring  │  │ Management  │  │   Systemd Service       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Hot-word Detection (`assistant/hotword.py`)

**Purpose**: Always-on wake word detection for "Parvis" activation.

**Technology**: Picovoice Porcupine (with mock mode for testing)

**Key Features**:
- Low CPU usage (~1%) when idle
- Configurable sensitivity
- Mock mode for hardware-free development
- Async operation with callback system

**Flow**:
1. Continuously listens for audio input
2. Processes audio through Porcupine engine
3. Triggers callback when "Parvis" is detected
4. Temporarily disables listening during conversation
5. Resumes listening after response completion

### 2. Speech Pipeline (`assistant/pipeline.py`)

**Purpose**: Orchestrates the complete voice conversation flow.

**Architecture**: STT → Intent Classification → LLM/Direct Response → TTS

**Key Features**:
- Multiple operation modes (hardware, simulation, text-only)
- Intent-first processing for optimal performance
- Graceful fallback to LLM for unknown requests
- Comprehensive error handling and logging
- Performance metrics collection

**Processing Flow**:
```
Audio Input → STT (Whisper) → Intent Manager → {
    Known Intent → Direct Response
    Vision Request → Vision Pipeline  
    Unknown/Chat → LLM (TinyLlama)
} → TTS (eSpeak) → Audio Output
```

### 3. Intent System (`assistant/intents.py`)

**Purpose**: Fast, accurate classification and handling of specific user requests.

**Architecture**: Plugin-based intent handlers with confidence scoring

**Intent Types**:
- **TimerIntent**: Natural language timer creation ("set timer for 5 minutes")
- **TimeIntent**: Current time and date queries
- **WeatherIntent**: Weather requests (explains offline limitation)
- **TranslationIntent**: Basic word translation (Spanish/French/German)
- **VisionIntent**: Delegates to vision pipeline
- **GeneralChatIntent**: Fallback to LLM

**Classification Process**:
1. **Keyword Matching**: Each intent defines trigger keywords
2. **Pattern Matching**: Regex patterns for structured extraction
3. **Confidence Scoring**: Weighted scoring based on matches
4. **Threshold Filtering**: Minimum confidence required (0.3)
5. **Handler Execution**: Best match processes the request

### 4. Vision Pipeline (`vision/pipeline.py`)

**Purpose**: Computer vision processing for scene understanding.

**Technology**: YOLOv8-n object detection with scene description

**Components**:
- **Camera Interface** (`vision/camera.py`): Pi Camera v3 integration
- **Object Detector** (`vision/detector.py`): YOLO model inference
- **Scene Description**: Natural language generation from detected objects

**Processing Flow**:
1. Image capture from Pi Camera (or mock image)
2. Object detection using YOLOv8-n model
3. Confidence filtering and object classification
4. Natural language description generation
5. Response formatting for voice output

### 5. Large Language Model (`assistant/llm.py`)

**Purpose**: General conversation and fallback processing.

**Technology**: TinyLlama 1.1B via llama.cpp or Ollama

**Features**:
- Auto-detection of available backends (Ollama → llama.cpp)
- Optimized for Raspberry Pi 4 ARM architecture
- Configurable response length and temperature
- Async processing with timeout handling

### 6. Speech-to-Text (`assistant/stt.py`)

**Purpose**: Real-time audio transcription.

**Technology**: Whisper.cpp with ARM NEON optimizations

**Models Available**:
- **Tiny** (75MB): Fast, basic accuracy
- **Small** (466MB): Better accuracy, moderate speed

**Features**:
- Hardware audio recording or simulation
- Configurable recording duration
- Language detection and processing
- Performance optimization for Pi 4

## Data Flow Architecture

### 1. Wake Word Activation Flow
```
Microphone → Porcupine → Wake Word Detected → Speech Pipeline Activation
```

### 2. Voice Command Processing Flow
```
Audio Recording → Whisper STT → Intent Classification → {
    Timer Intent → Timer Creation → Response
    Time Intent → System Time → Response  
    Translation Intent → Dictionary Lookup → Response
    Vision Intent → Camera → YOLO → Description → Response
    Unknown Intent → TinyLlama LLM → Response
} → eSpeak TTS → Speaker Output → Resume Wake Word Listening
```

### 3. Vision Request Flow
```
"What do you see?" → Vision Pipeline → {
    Camera Capture → Image Processing → YOLO Inference → {
        Object Detection → Confidence Filtering → Scene Description
    }
} → Natural Language Response → TTS Output
```

## Configuration System (`assistant/config.py`)

**Purpose**: Centralized configuration management using Pydantic models.

**Configuration Sections**:
- **AudioConfig**: Sample rates, buffer sizes, device settings
- **HotwordConfig**: Porcupine access keys, sensitivity, keyword paths
- **STTConfig**: Whisper model paths, language settings
- **LLMConfig**: Model paths, generation parameters, threading
- **TTSConfig**: eSpeak voice settings, speed configuration
- **VisionConfig**: YOLO model settings, camera parameters

**Features**:
- Type validation and documentation
- Default value management
- Environment-specific overrides
- Runtime configuration updates

## Production Architecture

### 1. Systemd Service (`systemd/pi-jarvis.service`)

**Purpose**: Production deployment with automatic startup and monitoring.

**Features**:
- Auto-start on boot with dependency management
- Resource limits (memory, CPU, file handles)
- Security hardening (sandboxing, privilege restrictions)
- Automatic restart on failure with backoff
- Proper logging and monitoring integration

### 2. Health Monitoring (`systemd/health-check.sh`)

**Purpose**: Automated system health verification.

**Monitoring Points**:
- Service status and process health
- Memory usage with configurable limits
- CPU utilization monitoring
- Error rate analysis from logs
- Automatic restart triggers

### 3. Maintenance System

**Components**:
- **Daily Maintenance** (`systemd/maintenance.sh`): Log cleanup, disk space monitoring
- **Weekly Reports** (`systemd/status-report.sh`): Comprehensive system analysis
- **Log Rotation** (`systemd/pi-jarvis-logrotate`): Automated log management

## Performance Optimizations

### 1. Intent-First Processing
- **Bypass LLM**: Direct response for common requests (timers, time, translations)
- **Response Time**: <1s for intent-based responses vs 3-5s for LLM responses
- **Resource Usage**: Minimal CPU/memory for intent processing

### 2. Model Optimizations
- **Whisper.cpp**: ARM NEON + OpenBLAS optimizations
- **TinyLlama**: Q4_K_M quantization for memory efficiency
- **YOLOv8-n**: Nano model for real-time inference on Pi 4

### 3. Async Architecture
- **Non-blocking**: All I/O operations use asyncio
- **Concurrent Processing**: Multiple components can process simultaneously
- **Resource Management**: Efficient memory and CPU utilization

## Testing Architecture

### 1. Hardware-Free Testing
- **Mock Components**: Camera, microphone, speaker simulation
- **Simulation Modes**: Complete pipeline testing without hardware
- **Unit Testing**: Individual component validation

### 2. Integration Testing
- **Pipeline Testing**: End-to-end conversation flow validation
- **Intent Testing**: Comprehensive intent classification verification
- **Vision Testing**: Object detection and scene description validation

## Security Considerations

### 1. System Security
- **Sandboxing**: Systemd security features limit system access
- **Privilege Separation**: Service runs as non-privileged user
- **Resource Limits**: Memory and CPU constraints prevent abuse

### 2. Data Privacy
- **100% Offline**: No external network communication for AI processing
- **Local Processing**: All voice and vision data processed locally
- **No Data Retention**: Audio and images processed in real-time only

## Scalability and Extensibility

### 1. Adding New Intents
```python
class CustomIntent(Intent):
    def _get_keywords(self) -> List[str]:
        return ["custom", "keyword", "trigger"]
    
    def _get_patterns(self) -> List[str]:
        return [r"custom pattern (\w+)"]
    
    async def handle(self, user_text: str, context: Optional[Dict] = None) -> IntentResult:
        # Custom processing logic
        return IntentResult(...)
```

### 2. Model Upgrades
- **Whisper Models**: Support for medium/large models with more memory
- **LLM Models**: Support for Phi-3, Llama variants, custom fine-tuned models
- **Vision Models**: Upgradeable to YOLOv8s/m/l/x variants

### 3. Hardware Scaling
- **Pi 5 Support**: Higher performance processing
- **External Hardware**: USB accelerators, dedicated AI chips
- **Distributed Processing**: Network-based component distribution

## Error Handling and Resilience

### 1. Component Failures
- **Graceful Degradation**: System continues with reduced functionality
- **Automatic Recovery**: Service restart and component reinitialization
- **Fallback Mechanisms**: Mock modes when hardware unavailable

### 2. Resource Exhaustion
- **Memory Limits**: Automatic restart when limits exceeded
- **Disk Space**: Automated cleanup and log rotation
- **CPU Throttling**: Thermal management and load balancing

### 3. Model Loading Failures
- **Backup Models**: Fallback to smaller/alternative models
- **Error Reporting**: Clear diagnostic information
- **Service Continuity**: Partial functionality maintenance

This architecture provides a robust, scalable foundation for offline AI assistance while maintaining excellent performance on Raspberry Pi 4 hardware.