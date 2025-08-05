# Project: Pi-Jarvis v1.0 - Reference Document

**Voice + Vision Assistant - 100% Offline on Raspberry Pi 4**

## 🏁 1. Objective

Build an always-on assistant that:
- Listens for a hot-word ("Hey Pi"), converts speech to text, runs a small local language model for answers, and speaks back—entirely offline
- On demand, captures a camera frame and describes what it sees ("What do you see?") using YOLO object detection
- Provides basic utility intents (timers, translations, summaries, etc.)
- Boots automatically as a **systemd** service

*Note: Garden sensors and time-lapse come in v2—ignore for now but leave the architecture open for them.*

## 🧩 2. Mandatory Hardware

- **Raspberry Pi 4** (64-bit OS)
- Passive/fan heatsink case + 3A USB-C PSU
- USB microphone + small speaker *or* ReSpeaker 2-Mic HAT
- Pi Camera v3
- 32GB+ micro-SD

## 🔧 3. Software Stack (Must Use)

| Layer | Tool / Model | Notes |
|-------|-------------|-------|
| Hot-word | **Porcupine** (free keyword) | ~1% CPU idle |
| Speech-to-Text | **Whisper.cpp** tiny or small | Build with NEON + OpenBLAS |
| Language model | **TinyLlama 1.1B** *or* **Phi-3-mini 1.8B** quantised to Q4_K_M via **llama.cpp** *or* **Ollama** | |
| Vision | **YOLOv8-n** (ultralytics) | CPU ≈ 6 FPS; single-frame mode |
| Text-to-Speech | **eSpeak NG** (fallback Piper) | Fast, light |
| Glue code | **Python 3.11**, `asyncio`, `pydantic` for config | |
| Service mgmt | **systemd** units | |
| Dev workflow | **Cursor IDE Remote-SSH** into Pi; Claude writes code directly in the Pi workspace; Git for VCS | |

## 🗂️ 4. Directory Layout (Initial Scaffold)

```
pi-jarvis/
├─ assistant/         # Python glue + intent router
├─ models/            # .gguf, whisper binaries (git-ignored)
├─ vision/            # YOLO scripts & config
├─ systemd/           # assistant.service, vision.service
└─ README.md
```

## 🚀 5. High-Level Build Phases

1. **Environment** – install build-essentials, OpenBLAS, ffmpeg, pvporcupine
2. **STT demo** – compile Whisper.cpp; confirm real-time transcription
3. **LLM demo** – install llama.cpp *or* Ollama; load TinyLlama; benchmark
4. **STT ➜ LLM ➜ TTS loop** – single Python script; measure < 1s latency
5. **Hot-word gating** – Porcupine wakes the loop
6. **Vision function** – capture frame, run YOLOv8-n, return labels list
7. **Intent system** – map utterances ("set timer", "describe scene") to handlers
8. **Systemd packaging** – auto-start on boot, logs in journald
9. **Readme + demo GIF** – show voice & vision working offline

## 📋 Technical Requirements

### Performance Targets
- Hot-word detection: ~1% CPU idle
- STT + LLM + TTS loop: < 1s latency
- Vision processing: ~6 FPS (single-frame mode)
- Boot time: Auto-start with systemd

### Key Architecture Principles
- 100% offline operation
- Modular design for future expansion (v2 sensors/time-lapse)
- Efficient resource usage on Pi 4
- Robust error handling and logging
- Clean separation of concerns (STT, LLM, TTS, Vision, Intent routing)

### Development Standards
- Python 3.11+ with asyncio for concurrency
- Pydantic for configuration management
- Comprehensive logging via Python logging + journald
- Git version control with meaningful commits
- Code documentation and type hints
- Unit tests for critical components

## 🔄 Phase Implementation Strategy

Each phase should be:
1. **Implemented** - Working code with basic error handling
2. **Tested** - Manual testing to verify functionality
3. **Documented** - Comments and basic usage docs
4. **Committed** - Git commit with descriptive message
5. **Benchmarked** - Performance metrics where applicable

## 🎯 Success Criteria

**Phase 1-3**: Core components (STT, LLM) working individually
**Phase 4**: Full speech pipeline working end-to-end
**Phase 5**: Hot-word activation working
**Phase 6**: Vision integration complete
**Phase 7**: Intent routing and utility functions
**Phase 8**: Production systemd deployment
**Phase 9**: Complete documentation and demo

## 📝 Notes for Development

- Use absolute paths where possible for Pi compatibility
- Test on actual Pi 4 hardware throughout development
- Monitor CPU/memory usage at each phase
- Keep models directory git-ignored due to size
- Plan for graceful degradation if components fail
- Consider thermal throttling on Pi 4 under load