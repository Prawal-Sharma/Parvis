# Pi-Jarvis Testing Guide

This guide provides comprehensive instructions for testing all components of Pi-Jarvis, from individual modules to full system integration.

## Prerequisites

### Environment Setup

**Important**: Always activate the virtual environment before testing:

```bash
cd /home/raspberry/Desktop/Parvis
source venv/bin/activate
```

**Note**: If you see `ModuleNotFoundError: No module named 'pydantic'`, you forgot to activate the virtual environment!

### Verify Installation

```bash
# Check Python environment
which python
# Should show: /home/raspberry/Desktop/Parvis/venv/bin/python

# Verify key dependencies
python -c "import pydantic; print('✓ Pydantic available')"
python -c "import assistant.intents; print('✓ Intent system available')"
python -c "import vision.pipeline; print('✓ Vision system available')"
```

## Component Testing

### 1. Intent System Testing

The intent system is the core of Pi-Jarvis intelligence and can be thoroughly tested without any hardware.

#### Automated Intent Testing

```bash
# Run comprehensive test suite
python -m assistant.test_intents
```

**Expected Output**:
- All 17+ test cases should pass (100% success rate)
- Timer, weather, time, translation, and vision intents tested
- Performance statistics displayed
- Offers interactive testing mode

#### Interactive Intent Testing

```bash
# Start interactive testing
python -m assistant.test_intents
# When prompted, type 'y' for interactive mode
```

**Test These Commands**:
```
Timer Commands:
- "Set a timer for 5 minutes"
- "Start a 30 second timer" 
- "Remind me in 2 hours"

Time Queries:
- "What time is it?"
- "What's today's date?"
- "Tell me the current time"

Translations:
- "How do you say hello in Spanish?"
- "Translate water to French" 
- "What is goodbye in German?"

Vision Requests:
- "What do you see?"
- "Look around and describe the scene"
- "What's in front of you?"

Weather Queries:
- "What's the weather like?"
- "Is it raining outside?"

General Chat:
- "Hello, how are you?"
- "What can you help me with?"
```

#### Manual Intent Testing

```bash
# Test individual intent components
python -c "
import asyncio
from assistant.intents import intent_manager

async def test_intent(text):
    result = await intent_manager.classify_and_handle(text)
    print(f'Input: {text}')
    print(f'Intent: {result.intent_type.value}')
    print(f'Confidence: {result.confidence:.2f}')
    print(f'Response: {result.response_text}')
    print('---')

# Test multiple intents
asyncio.run(test_intent('Set timer 10 minutes'))
asyncio.run(test_intent('What time is it?'))
asyncio.run(test_intent('Translate hello to Spanish'))
"
```

### 2. Speech Pipeline Testing

#### Text-Only Pipeline Testing

```bash
# Test complete pipeline without audio hardware
python -m assistant.main text
```

**What This Tests**:
- Intent classification and handling
- LLM fallback for unknown requests
- Text-to-speech simulation
- Error handling and recovery

**Test Commands**:
```
Pipeline Test Commands:
- "Set a timer for 3 minutes"     # Should use timer intent
- "What's the time?"              # Should use time intent  
- "Tell me a joke"                # Should fallback to LLM
- "What do you see?"              # Should delegate to vision
- "How do you say water in French?" # Should use translation intent
```

#### Simulation Mode Testing

```bash
# Test with simulated audio and full pipeline
python -m assistant.main simulation
```

**What This Tests**:
- Complete STT → Intent → LLM → TTS pipeline
- Automatic conversation generation
- Performance timing and statistics
- Error handling across all components

#### Individual Pipeline Components

```bash
# Test STT component (simulation mode)
python -c "
import asyncio
from assistant.stt import stt_engine

async def test_stt():
    await stt_engine.initialize()
    # Test with simulated input
    result = await stt_engine.transcribe_speech(duration=5, simulate_text='Hello Parvis')
    print(f'STT Result: {result}')

asyncio.run(test_stt())
"

# Test LLM component
python -c "
import asyncio
from assistant.llm import llm_engine

async def test_llm():
    await llm_engine.initialize()
    response = await llm_engine.generate('Hello, how are you?', max_tokens=50)
    print(f'LLM Response: {response}')

asyncio.run(test_llm())
"
```

### 3. Vision System Testing

#### Automated Vision Testing

```bash
# Run vision system tests
python -m vision.test_vision
```

**Expected Output**:
- Mock camera image generation
- Object detection with confidence scores
- Scene description generation
- Performance timing (should be <2s total)

#### Manual Vision Testing

```bash
# Test vision pipeline directly
python -c "
import asyncio
from vision.pipeline import VisionPipeline

async def test_vision():
    pipeline = VisionPipeline(use_mock_camera=True, use_mock_detector=True)
    await pipeline.initialize()
    description = await pipeline.describe_scene()
    print(f'Scene Description: {description}')

asyncio.run(test_vision())
"
```

#### Camera Hardware Testing (if available)

```bash
# Test with real Pi Camera
python -c "
import asyncio
from vision.pipeline import VisionPipeline

async def test_real_camera():
    pipeline = VisionPipeline(use_mock_camera=False, use_mock_detector=True)
    try:
        await pipeline.initialize()
        description = await pipeline.describe_scene()
        print(f'Real Camera Description: {description}')
    except Exception as e:
        print(f'Camera not available: {e}')

asyncio.run(test_real_camera())
"
```

### 4. Hot-word Detection Testing

#### Mock Hot-word Testing

```bash
# Test hot-word detection in mock mode
python -c "
import asyncio
from assistant.hotword import create_hotword_detector

async def test_hotword():
    def on_wake_word():
        print('✓ Wake word detected!')
    
    detector = create_hotword_detector(on_wake_word, use_mock=True)
    detector.initialize()
    
    print('Starting mock hot-word detection...')
    # Run for 30 seconds to see multiple detections
    await detector.start_listening()

asyncio.run(test_hotword())
"
```

#### Porcupine Hardware Testing (if configured)

```bash
# Test with real Porcupine (requires access key)
python -c "
import asyncio
from assistant.hotword import create_hotword_detector, PORCUPINE_AVAILABLE

async def test_real_hotword():
    if not PORCUPINE_AVAILABLE:
        print('Porcupine not available - using mock mode')
        return
    
    def on_wake_word():
        print('✓ Real wake word detected!')
    
    detector = create_hotword_detector(on_wake_word, use_mock=False)
    if detector.initialize():
        print('Say \"Parvis\" to test...')
        await detector.start_listening()
    else:
        print('Failed to initialize Porcupine')

asyncio.run(test_real_hotword())
"
```

### 5. Complete System Integration Testing

#### Full Parvis Assistant Testing

```bash
# Test complete system in simulation mode
python -m assistant.parvis simulation true
```

**What This Tests**:
- Hot-word detection (mock mode)
- Complete conversation flow
- Intent classification and handling
- Vision integration
- All component interactions
- Error handling and recovery

**Expected Behavior**:
1. Service starts and initializes all components
2. Mock wake word detection triggers every 10-15 seconds
3. Random conversation scenarios execute
4. Intent classification works for various requests
5. Vision requests are processed
6. System returns to listening state

#### Production Service Testing

```bash
# Test the actual systemd service
sudo systemctl start pi-jarvis.service

# Monitor service status
systemctl status pi-jarvis.service

# Watch live logs
journalctl -u pi-jarvis.service -f

# Test service health
./systemd/health-check.sh

# Generate status report
./systemd/status-report.sh
```

## Performance Testing

### 1. Response Time Testing

```bash
# Benchmark intent response times
python -c "
import asyncio
import time
from assistant.intents import intent_manager

async def benchmark_intents():
    test_cases = [
        'Set a timer for 5 minutes',
        'What time is it?',
        'How do you say hello in Spanish?',
        'What do you see?'
    ]
    
    for text in test_cases:
        start = time.time()
        result = await intent_manager.classify_and_handle(text)
        elapsed = time.time() - start
        print(f'{text}: {elapsed:.3f}s ({result.intent_type.value})')

asyncio.run(benchmark_intents())
"
```

### 2. Memory Usage Testing

```bash
# Monitor memory usage during operation
python -c "
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    return memory_mb

print(f'Initial memory: {get_memory_usage():.1f}MB')

# Import and initialize components
from assistant.intents import intent_manager
print(f'After intents: {get_memory_usage():.1f}MB')

from assistant.llm import llm_engine
print(f'After LLM: {get_memory_usage():.1f}MB')

from vision.pipeline import VisionPipeline
print(f'After vision: {get_memory_usage():.1f}MB')
"
```

### 3. Stress Testing

```bash
# Test intent system under load
python -c "
import asyncio
import time
from assistant.intents import intent_manager

async def stress_test():
    test_commands = [
        'Set timer 1 minute', 'What time is it?', 'Hello in Spanish',
        'What do you see?', 'Current time', 'Timer 30 seconds'
    ] * 10  # 60 total requests
    
    start = time.time()
    tasks = [intent_manager.classify_and_handle(cmd) for cmd in test_commands]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    successful = sum(1 for r in results if r.success)
    print(f'Processed {len(results)} requests in {elapsed:.2f}s')
    print(f'Success rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)')
    print(f'Average: {elapsed/len(results)*1000:.1f}ms per request')

asyncio.run(stress_test())
"
```

## Error Testing

### 1. Component Failure Testing

```bash
# Test behavior when components fail
python -c "
import asyncio
from assistant.intents import intent_manager

async def test_error_handling():
    # Test with invalid input
    result = await intent_manager.classify_and_handle('')
    print(f'Empty input: {result.success}, {result.response_text}')
    
    # Test with nonsensical input
    result = await intent_manager.classify_and_handle('asdf qwerty zxcv')
    print(f'Nonsense input: {result.intent_type.value}, {result.response_text}')
    
    # Test with very long input
    long_text = 'test ' * 1000
    result = await intent_manager.classify_and_handle(long_text)
    print(f'Long input: {result.success}')

asyncio.run(test_error_handling())
"
```

### 2. Resource Exhaustion Testing

```bash
# Test memory limits
python -c "
import gc
from assistant.intents import intent_manager

# Force garbage collection
gc.collect()

# Monitor memory during heavy usage
import psutil
import os
process = psutil.Process(os.getpid())

print(f'Memory before: {process.memory_info().rss / 1024 / 1024:.1f}MB')

# Create many concurrent tasks
import asyncio
async def memory_test():
    tasks = []
    for i in range(100):
        task = intent_manager.classify_and_handle(f'Set timer {i} minutes')
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    print(f'Completed {len(results)} tasks')

asyncio.run(memory_test())
print(f'Memory after: {process.memory_info().rss / 1024 / 1024:.1f}MB')
"
```

## Hardware Testing (Optional)

### 1. Audio Hardware Testing

```bash
# Test microphone input (if available)
python -c "
import pyaudio
import wave

def test_microphone():
    try:
        p = pyaudio.PyAudio()
        print('Available audio devices:')
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f'  {i}: {info[\"name\"]} (inputs: {info[\"maxInputChannels\"]})')
        
        # Test recording
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, 
                       input=True, frames_per_buffer=1024)
        print('✓ Microphone available')
        stream.close()
        p.terminate()
    except Exception as e:
        print(f'Microphone not available: {e}')

test_microphone()
"
```

### 2. Camera Hardware Testing

```bash
# Test Pi Camera (if available)
python -c "
try:
    from picamera2 import Picamera2
    camera = Picamera2()
    camera.start()
    camera.capture_file('/tmp/test_camera.jpg')
    camera.stop()
    print('✓ Pi Camera working')
except Exception as e:
    print(f'Camera not available: {e}')
"
```

## Continuous Integration Testing

### 1. Automated Test Suite

Create a comprehensive test script:

```bash
# Create test runner script
cat > test_all.sh << 'EOF'
#!/bin/bash
set -e

echo "🧪 Pi-Jarvis Comprehensive Test Suite"
echo "===================================="

# Activate virtual environment
source venv/bin/activate

echo "✓ Virtual environment activated"

# Test intent system
echo "Testing intent system..."
python -m assistant.test_intents --automated

# Test individual components
echo "Testing speech pipeline..."
python -c "
import asyncio
from assistant.pipeline import SpeechPipeline, PipelineMode

async def test():
    pipeline = SpeechPipeline(mode=PipelineMode.SIMULATION)
    await pipeline.initialize()
    turn = await pipeline.process_voice_input(simulate_text='Test message')
    assert turn.success, f'Pipeline test failed: {turn.error_message}'
    print('✓ Speech pipeline working')

asyncio.run(test())
"

# Test vision system
echo "Testing vision system..."
python -c "
import asyncio
from vision.pipeline import VisionPipeline

async def test():
    pipeline = VisionPipeline(use_mock_camera=True, use_mock_detector=True)
    await pipeline.initialize()
    result = await pipeline.describe_scene()
    assert result, 'Vision pipeline failed'
    print('✓ Vision system working')

asyncio.run(test())
"

echo "🎉 All tests passed!"
EOF

chmod +x test_all.sh
```

### 2. Run Complete Test Suite

```bash
# Execute full test suite
./test_all.sh
```

## Troubleshooting Common Issues

### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'pydantic'`
**Solution**: Activate virtual environment: `source venv/bin/activate`

### 2. Permission Errors

**Problem**: Permission denied accessing audio/camera
**Solution**: Add user to audio/video groups:
```bash
sudo usermod -a -G audio,video $USER
# Logout and login again
```

### 3. Service Testing Issues

**Problem**: Service fails to start
**Solution**: Check logs and configuration:
```bash
journalctl -u pi-jarvis.service --no-pager -n 50
sudo systemctl status pi-jarvis.service
```

### 4. Memory Issues

**Problem**: Out of memory errors
**Solution**: Check system resources:
```bash
free -h
df -h
./systemd/health-check.sh
```

### 5. Performance Issues

**Problem**: Slow response times
**Solution**: Check CPU usage and temperature:
```bash
htop
vcgencmd measure_temp
./systemd/status-report.sh
```

## Testing Best Practices

### 1. Test Environment Setup
- Always use virtual environment
- Test in clean environment periodically
- Document hardware configurations
- Use version control for test data

### 2. Test Coverage
- Test all intent types
- Test error conditions
- Test resource limits
- Test hardware fallbacks

### 3. Performance Monitoring
- Track response times
- Monitor memory usage
- Check system stability
- Validate accuracy metrics

### 4. Regression Testing
- Test after any code changes
- Validate service after updates
- Check backwards compatibility
- Document breaking changes

This comprehensive testing guide ensures Pi-Jarvis reliability and performance across all deployment scenarios.