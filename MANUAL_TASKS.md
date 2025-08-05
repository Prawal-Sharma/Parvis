# Pi-Jarvis Manual Tasks & Testing Guide

**Things you'll need to do manually during development**

---

## 🔧 **Phase 1: Environment Setup**

### Manual Steps Required:
- [ ] **Run sudo commands** (I can't execute sudo through automation)
  ```bash
  sudo apt update && sudo apt install -y build-essential cmake git
  sudo apt install -y libopenblas-dev portaudio19-dev espeak espeak-data
  sudo apt install -y python3-venv python3-pip ffmpeg
  ```

### Hardware Testing:
- [ ] **Test USB microphone**: Plug in and verify recognition
  ```bash
  arecord -l  # List audio input devices
  arecord -d 5 test.wav  # Record 5-second test
  aplay test.wav  # Playback test
  ```
- [ ] **Test speaker/audio output**: Verify sound works
  ```bash
  speaker-test -t wav -c 2  # Test stereo output
  espeak "Hello Pi-Jarvis"  # Test TTS
  ```
- [ ] **Test Pi Camera**: Ensure camera is detected and working
  ```bash
  libcamera-still -o test.jpg  # Capture test image
  ```
- [ ] **Check permissions**: Verify user can access audio/video devices
  ```bash
  groups $USER  # Should include audio, video groups
  ```

### Manual Verification:
- [ ] Confirm all Python packages installed without errors
- [ ] Test that virtual environment activates properly
- [ ] Verify no missing system dependencies

---

## 🎤 **Phase 2: Speech-to-Text Demo**

### Manual Testing Required:
- [ ] **Voice quality testing**: Speak at different distances/volumes
- [ ] **Microphone positioning**: Find optimal placement for clarity  
- [ ] **Background noise testing**: Test in your actual environment
- [ ] **Accent/speech pattern testing**: Verify Whisper handles your voice well
- [ ] **Performance monitoring**: Watch CPU/temperature during transcription

### Manual Verification:
- [ ] Transcription accuracy > 90% for clear speech
- [ ] Latency < 2 seconds for 5-second audio clips
- [ ] No audio dropouts or glitches
- [ ] System remains stable under continuous use

---

## 🧠 **Phase 3: Language Model Demo**

### Manual Testing Required:
- [ ] **Response quality evaluation**: Test various question types
- [ ] **Context understanding**: Test follow-up questions
- [ ] **Performance monitoring**: Check CPU usage and temperature
- [ ] **Memory usage**: Ensure Pi doesn't run out of RAM

### Manual Verification:
- [ ] Responses are coherent and helpful
- [ ] Inference time < 3 seconds for simple queries
- [ ] No memory leaks during extended use
- [ ] Model loads successfully on boot

---

## 🔄 **Phase 4: Complete Speech Pipeline**

### Critical Manual Testing:
- [ ] **End-to-end conversation testing**: Full voice-to-voice interaction
- [ ] **Response timing**: Measure total pipeline latency
- [ ] **Audio quality**: Ensure TTS is clear and natural
- [ ] **Conversation flow**: Test back-and-forth dialogue
- [ ] **Error recovery**: Test behavior with unclear speech

### Manual Verification:
- [ ] Total response time < 5 seconds (ideally < 3)
- [ ] Clear, understandable TTS output
- [ ] No audio feedback loops or echo
- [ ] Graceful handling of speech recognition errors

---

## 🎯 **Phase 5: Hot-word Detection**

### Extensive Manual Testing Required:
- [ ] **"Hey Pi" training**: Test from different angles/distances
- [ ] **False positive testing**: Leave running for hours, monitor false triggers
- [ ] **Background noise testing**: TV, music, conversations nearby
- [ ] **Multiple voices**: Test with family members/friends if applicable
- [ ] **Edge case testing**: Whispering, shouting, accents

### Manual Verification:
- [ ] Reliable activation (>95% success rate)
- [ ] Low false positives (<1 per hour in normal environment)
- [ ] CPU usage stays around 1% when idle
- [ ] Quick response to wake word (<500ms)

---

## 👁️ **Phase 6: Vision Integration**

### Manual Testing Required:
- [ ] **Camera positioning**: Find optimal angle and height
- [ ] **Lighting testing**: Various lighting conditions (bright, dim, backlit)
- [ ] **Object detection accuracy**: Test with various household items
- [ ] **Distance testing**: Near and far object recognition
- [ ] **Scene complexity**: Simple vs. cluttered environments

### Manual Verification:
- [ ] Accurate object identification (>80% for common items)
- [ ] Reasonable processing speed (~6 FPS)
- [ ] Good scene descriptions in natural language
- [ ] No camera crashes or freezes

---

## 🎯 **Phase 7: Intent System**

### Manual Testing Required:
- [ ] **Voice command testing**: Try various phrasings for each intent
- [ ] **Timer functionality**: Set/cancel timers, test accuracy
- [ ] **Translation testing**: Test various language pairs
- [ ] **Weather/time queries**: Verify information accuracy
- [ ] **Intent classification**: Ensure system understands your requests

### Manual Verification:
- [ ] Intent recognition >90% accuracy
- [ ] All utility functions work as expected
- [ ] Graceful fallback for unrecognized intents
- [ ] Natural conversation flow maintained

---

## 🚀 **Phase 8: Production Deployment**

### Critical Manual Testing:
- [ ] **Reboot testing**: Full system restart, verify auto-start
- [ ] **Long-term stability**: Run for 24+ hours continuously
- [ ] **Error recovery**: Test behavior after crashes/errors
- [ ] **Service management**: Test start/stop/restart commands
- [ ] **Log monitoring**: Check logs for errors or warnings

### Manual Verification:
- [ ] Pi-Jarvis starts automatically after reboot
- [ ] System remains responsive under load
- [ ] Proper logging and error reporting
- [ ] Service can be controlled via systemctl

---

## 📹 **Phase 9: Documentation & Demo**

### Manual Creation Required:
- [ ] **Demo video recording**: Show voice and vision features
- [ ] **Performance benchmarking**: Document actual speeds/accuracy
- [ ] **User guide creation**: Step-by-step usage instructions
- [ ] **Troubleshooting guide**: Document common issues you encountered

---

## 🔍 **Ongoing Manual Monitoring**

### Throughout All Phases:
- [ ] **Temperature monitoring**: Keep Pi cool, watch for throttling
  ```bash
  vcgencmd measure_temp  # Check CPU temperature
  ```
- [ ] **Resource monitoring**: Watch CPU, memory, disk usage
  ```bash
  htop  # System monitor
  df -h  # Disk usage
  ```
- [ ] **Error log monitoring**: Check for crashes or issues
  ```bash
  journalctl -u pi-jarvis -f  # Follow service logs
  ```

---

## 🤝 **How We'll Work Together**

### My Role:
- Write all the code and configuration files
- Set up the development environment and structure
- Provide commands and scripts for you to run
- Debug issues based on your feedback
- Optimize performance based on your testing results

### Your Role:
- Execute sudo commands and system-level changes
- Test hardware functionality (audio, camera, etc.)
- Provide feedback on voice recognition accuracy
- Test real-world performance and usability
- Verify that everything works in your specific environment
- Record final demo and documentation

### Communication:
- **Before each phase**: I'll tell you exactly what manual steps are needed
- **During testing**: Report any issues, errors, or unexpected behavior
- **After testing**: Let me know results so I can optimize or fix problems

---

## 📋 **Quick Reference: When to Involve You**

| Phase | Manual Task | Why You Need to Do It |
|-------|-------------|----------------------|
| 1 | sudo commands | Security restrictions |
| 1 | Hardware testing | Physical device verification |
| 2-9 | Voice testing | Your voice/accent/environment |
| 2-9 | Performance validation | Real Pi 4 hardware testing |
| 5 | Wake word training | Your specific usage patterns |
| 6 | Camera setup | Physical positioning/lighting |
| 8 | Reboot testing | System-level verification |
| 9 | Demo creation | User experience documentation |

I'll always give you clear instructions and let you know exactly what to test and how to report results back to me!