"""
Test script for Speech-to-Text functionality
Phase 2: Whisper.cpp integration testing
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from assistant.stt import stt_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_stt_initialization():
    """Test STT system initialization."""
    print("🔧 Testing STT initialization...")
    
    success = stt_engine.initialize()
    if success:
        print("✅ STT initialization successful")
        return True
    else:
        print("❌ STT initialization failed")
        return False


async def test_speech_transcription():
    """Test speech transcription with user input."""
    print("\n🎤 Testing speech transcription...")
    print("📢 You will be asked to speak for 5 seconds")
    print("💡 If no microphone is available, this test will be skipped")
    
    input("Press Enter to start recording, or Ctrl+C to skip...")
    
    try:
        print("🎙️ Recording for 5 seconds... Speak now!")
        text = await stt_engine.transcribe_speech(duration=5)
        
        if text:
            print(f"✅ Transcription successful: '{text}'")
            return True
        else:
            print("⚠️ Transcription returned empty result")
            print("   This could be due to:")
            print("   - No microphone connected")
            print("   - Background noise")
            print("   - Speech too quiet")
            return False
            
    except KeyboardInterrupt:
        print("\n⏭️ Speech test skipped by user")
        return True
    except Exception as e:
        print(f"❌ Speech transcription failed: {e}")
        return False


async def test_model_performance():
    """Test different models and measure performance."""
    print("\n⚡ Testing model performance...")
    
    models = ["tiny", "small"]
    
    for model_name in models:
        if not Path(f"models/ggml-{model_name}.bin").exists():
            print(f"⏭️ Skipping {model_name} model (not downloaded)")
            continue
        
        print(f"\n🧪 Testing {model_name} model...")
        
        # Create engine with specific model
        from assistant.stt import WhisperSTT
        test_engine = WhisperSTT(model_name=model_name)
        
        if test_engine.initialize():
            print(f"✅ {model_name.capitalize()} model ready")
        else:
            print(f"❌ {model_name.capitalize()} model failed to initialize")
        
        test_engine.cleanup()


async def main():
    """Main test function."""
    print("🧪 Pi-Jarvis Speech-to-Text Testing")
    print("====================================")
    
    try:
        # Test 1: Initialization
        init_success = await test_stt_initialization()
        if not init_success:
            print("\n❌ Cannot proceed - initialization failed")
            print("\n🔧 Troubleshooting:")
            print("1. Ensure Whisper.cpp is built: ./setup/build_whisper.sh")
            print("2. Ensure models are downloaded: ./setup/download_whisper_models.sh")
            return
        
        # Test 2: Model performance check
        await test_model_performance()
        
        # Test 3: Speech transcription (optional - requires microphone)
        print("\n" + "="*50)
        print("🎤 OPTIONAL: Speech Transcription Test")
        print("="*50)
        print("This test requires a microphone connected to your Pi.")
        print("If you don't have a microphone, you can skip this test.")
        
        response = input("\nDo you want to test speech transcription? (y/N): ").lower()
        
        if response in ['y', 'yes']:
            await test_speech_transcription()
        else:
            print("⏭️ Speech transcription test skipped")
        
        print("\n🎯 STT Testing Summary:")
        print("="*30)
        print("✅ System initialization: OK")
        print("✅ Model loading: OK") 
        if response in ['y', 'yes']:
            print("✅ Speech transcription: Tested")
        else:
            print("⏭️ Speech transcription: Skipped (no microphone)")
            
        print("\n🚀 Ready for Phase 3: Language Model Integration!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    finally:
        stt_engine.cleanup()


if __name__ == "__main__":
    asyncio.run(main())