"""
Test script for Hot-word Detection
Phase 5: "Parvis" wake word testing
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from assistant.hotword import create_hotword_detector, PORCUPINE_AVAILABLE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def on_wake_word_detected():
    """Callback when 'Parvis' wake word is detected."""
    print("\n🎯 WAKE WORD DETECTED: 'Parvis'!")
    print("   Assistant would now activate...")
    print("   (In full system: would start STT → LLM → TTS pipeline)")


async def test_hotword_initialization():
    """Test hot-word detector initialization."""
    print("🔧 Testing hot-word detector initialization...")
    
    # Test mock detector first
    print("\n--- Testing Mock Detector ---")
    mock_detector = create_hotword_detector(
        on_wake_word=on_wake_word_detected,
        use_mock=True
    )
    
    mock_success = mock_detector.initialize()
    if mock_success:
        print("✅ Mock hot-word detector initialized successfully")
    else:
        print("❌ Mock hot-word detector initialization failed")
    
    mock_detector.cleanup()
    
    # Test real detector if available
    if PORCUPINE_AVAILABLE:
        print("\n--- Testing Real Porcupine Detector ---")
        real_detector = create_hotword_detector(
            on_wake_word=on_wake_word_detected,
            use_mock=False
        )
        
        real_success = real_detector.initialize()
        if real_success:
            print("✅ Real hot-word detector initialized successfully")
        else:
            print("❌ Real hot-word detector initialization failed")
            print("   This is expected if no Porcupine access key is provided")
        
        real_detector.cleanup()
        return mock_success, real_success
    else:
        print("\n--- Real Porcupine Detector ---")
        print("⚠️  Porcupine not available (pvporcupine not installed)")
        return mock_success, False


async def test_mock_wake_word_detection():
    """Test mock wake word detection."""
    print("\n🎭 Testing mock wake word detection...")
    print("This will simulate 'Parvis' detection every 10 seconds")
    print("Press Ctrl+C to stop the test")
    
    detector = create_hotword_detector(
        on_wake_word=on_wake_word_detected,
        use_mock=True
    )
    
    if not detector.initialize():
        print("❌ Failed to initialize mock detector")
        return False
    
    try:
        # Start listening in background
        listen_task = asyncio.create_task(detector.start_listening())
        
        # Wait for some detections or user interrupt
        await asyncio.sleep(35)  # Run for 35 seconds (should get 3-4 detections)
        
        # Stop listening
        detector.stop_listening()
        await listen_task
        
        print("✅ Mock wake word detection test completed")
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        detector.stop_listening()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        detector.cleanup()


async def test_real_wake_word_detection():
    """Test real wake word detection (requires hardware and access key)."""
    print("\n🎤 Testing real wake word detection...")
    
    if not PORCUPINE_AVAILABLE:
        print("⚠️  Porcupine not available - skipping real detection test")
        return False
    
    detector = create_hotword_detector(
        on_wake_word=on_wake_word_detected,
        use_mock=False
    )
    
    if not detector.initialize():
        print("❌ Failed to initialize real detector")
        print("   Possible reasons:")
        print("   - No Porcupine access key provided")
        print("   - No microphone available")
        print("   - Audio system issues")
        return False
    
    print("🎤 Listening for 'Parvis' wake word...")
    print("Speak 'Parvis' to test detection (or similar built-in keyword)")
    print("Press Ctrl+C to stop")
    
    try:
        # Start listening
        await detector.start_listening()
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        detector.cleanup()


async def test_hotword_integration():
    """Test integration with speech pipeline."""
    print("\n🔗 Testing hot-word integration concept...")
    
    # This simulates how the hot-word would integrate with the speech pipeline
    class MockSpeechPipeline:
        def __init__(self):
            self.is_active = False
        
        async def activate_conversation(self):
            """Simulate activating the speech pipeline."""
            print("🚀 Speech pipeline activated!")
            print("   → Starting STT listening...")
            print("   → Ready for user speech input...")
            self.is_active = True
            
            # Simulate conversation
            await asyncio.sleep(2)
            print("   → Simulated conversation complete")
            self.is_active = False
            print("   → Returning to wake word listening...")
    
    pipeline = MockSpeechPipeline()
    
    async def on_parvis_detected():
        """Handler for when Parvis is detected."""
        print("\n🎯 'Parvis' detected - Activating conversation!")
        await pipeline.activate_conversation()
    
    # Test mock integration
    detector = create_hotword_detector(
        on_wake_word=on_parvis_detected,
        use_mock=True
    )
    
    if not detector.initialize():
        print("❌ Failed to initialize detector")
        return False
    
    print("🎭 Testing integration with mock wake word...")
    print("This simulates the complete flow: Wake word → Conversation → Back to listening")
    
    try:
        # Run for 25 seconds to see 2-3 activations
        listen_task = asyncio.create_task(detector.start_listening())
        await asyncio.sleep(25)
        
        detector.stop_listening()
        await listen_task
        
        print("✅ Integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    finally:
        detector.cleanup()


async def main():
    """Main test function."""
    print("🎯 Parvis Hot-word Detection Testing")
    print("=" * 45)
    print("📝 Testing 'Parvis' wake word detection")
    print("=" * 45)
    
    test_results = []
    
    try:
        # Test 1: Initialization
        mock_init, real_init = await test_hotword_initialization()
        test_results.append(("Mock Detector Initialization", mock_init))
        test_results.append(("Real Detector Initialization", real_init))
        
        # Test 2: Mock Wake Word Detection
        mock_detection = await test_mock_wake_word_detection()
        test_results.append(("Mock Wake Word Detection", mock_detection))
        
        # Test 3: Real Wake Word Detection (if available)
        if PORCUPINE_AVAILABLE and input("\nTest real wake word detection? (y/N): ").lower() == 'y':
            real_detection = await test_real_wake_word_detection()
            test_results.append(("Real Wake Word Detection", real_detection))
        
        # Test 4: Integration Test
        integration_test = await test_hotword_integration()
        test_results.append(("Pipeline Integration", integration_test))
        
        # Summary
        print("\n" + "=" * 45)
        print("🎯 HOT-WORD DETECTION TEST SUMMARY")
        print("=" * 45)
        
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        passed_tests = sum(1 for _, success in test_results if success)
        total_tests = len(test_results)
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests >= len(test_results) - 1:  # Allow 1 failure (real detector might fail)
            print("\n🎉 HOT-WORD DETECTION READY!")
            print("🎯 Next: Integrate with complete speech pipeline")
        else:
            print("\n⚠️  Some issues detected - review failed tests")
        
        print("\n📋 Setup Instructions:")
        print("1. Get Porcupine access key: https://console.picovoice.ai/")
        print("2. Add access key to assistant/config.py")
        print("3. Optional: Train custom 'Parvis' keyword model")
        print("4. Connect microphone for real testing")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test failed")


if __name__ == "__main__":
    asyncio.run(main())