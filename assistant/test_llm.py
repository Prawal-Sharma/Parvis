"""
Test script for Language Model functionality
Phase 3: LLM integration testing
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from assistant.llm import llm_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_llm_initialization():
    """Test LLM system initialization."""
    print("🔧 Testing LLM initialization...")
    
    success = await llm_engine.initialize()
    if success:
        print("✅ LLM initialization successful")
        print(f"   Backend: {type(llm_engine.backend).__name__}")
        return True
    else:
        print("❌ LLM initialization failed")
        return False


async def test_text_generation():
    """Test text generation with various prompts."""
    print("\n🧠 Testing text generation...")
    
    test_prompts = [
        "Hello, my name is",
        "The weather today is",
        "Pi-Jarvis is a voice assistant that",
        "Explain what a Raspberry Pi is in simple terms:",
        "What is 2 + 2?"
    ]
    
    results = []
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🧪 Test {i}/5: '{prompt}'")
        print("💭 Generating response...")
        
        start_time = time.time()
        response = await llm_engine.generate(prompt, max_tokens=50)
        elapsed = time.time() - start_time
        
        if response:
            print(f"✅ Response ({elapsed:.2f}s): {response}")
            results.append(True)
        else:
            print("❌ No response generated")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 Generation success rate: {success_rate:.0f}%")
    
    return success_rate >= 80  # At least 80% success rate


async def test_conversation():
    """Test conversational interaction."""
    print("\n💬 Testing conversational interaction...")
    
    conversation = [
        "Hi there!",
        "What's your purpose?",
        "Can you help me with tasks?"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n👤 Human: {message}")
        
        # Create a conversational prompt
        prompt = f"Human: {message}\nAssistant:"
        
        response = await llm_engine.generate(prompt, max_tokens=100)
        
        if response:
            print(f"🤖 Assistant: {response}")
        else:
            print("🤖 Assistant: [No response]")
    
    return True


async def benchmark_performance():
    """Benchmark LLM performance."""
    print("\n⚡ Benchmarking performance...")
    
    # Test different prompt lengths
    prompts = [
        "Hello",  # Short
        "Explain the concept of artificial intelligence",  # Medium
        "Write a detailed explanation of how voice assistants work and what makes them useful"  # Long
    ]
    
    for i, prompt in enumerate(prompts):
        length = ["Short", "Medium", "Long"][i]
        print(f"\n📏 {length} prompt ({len(prompt)} chars)")
        
        start_time = time.time()
        response = await llm_engine.generate(prompt, max_tokens=100)
        elapsed = time.time() - start_time
        
        if response:
            tokens_per_second = len(response.split()) / elapsed
            print(f"⏱️  Time: {elapsed:.2f}s")
            print(f"📊 Speed: ~{tokens_per_second:.1f} tokens/sec")
            print(f"📝 Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        else:
            print(f"❌ Failed in {elapsed:.2f}s")


async def main():
    """Main test function."""
    print("🧠 Pi-Jarvis Language Model Testing")
    print("====================================")
    
    try:
        # Test 1: Initialization
        init_success = await test_llm_initialization()
        if not init_success:
            print("\n❌ Cannot proceed - initialization failed")
            print("\n🔧 Troubleshooting:")
            print("1. Install LLM backend: ./setup/install_llm.sh")
            print("2. Download models: ./setup/download_llm_models.sh")
            print("3. For Ollama: sudo systemctl start ollama")
            return
        
        # Test 2: Basic text generation
        generation_success = await test_text_generation()
        
        # Test 3: Conversational interaction
        await test_conversation()
        
        # Test 4: Performance benchmark
        await benchmark_performance()
        
        print("\n🎯 LLM Testing Summary:")
        print("="*30)
        print("✅ System initialization: OK")
        if generation_success:
            print("✅ Text generation: OK")
        else:
            print("⚠️  Text generation: Issues detected")
        print("✅ Conversational flow: Tested")
        print("✅ Performance benchmark: Complete")
        
        print("\n🚀 Ready for Phase 4: Complete Speech Pipeline (STT → LLM → TTS)!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test failed")
    finally:
        llm_engine.cleanup()


if __name__ == "__main__":
    asyncio.run(main())