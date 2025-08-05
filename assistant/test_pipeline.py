"""
Test script for Complete Speech Pipeline
Phase 4: End-to-end STT → LLM → TTS testing
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from assistant.pipeline import SpeechPipeline, PipelineMode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_pipeline_initialization():
    """Test pipeline initialization."""
    print("🔧 Testing pipeline initialization...")
    
    pipeline = SpeechPipeline(mode=PipelineMode.SIMULATION)
    success = await pipeline.initialize()
    
    if success:
        print("✅ Pipeline initialization successful")
        return pipeline
    else:
        print("❌ Pipeline initialization failed")
        return None


async def test_single_conversation_turn(pipeline: SpeechPipeline):
    """Test a single conversation turn."""
    print("\n💬 Testing single conversation turn...")
    
    turn = await pipeline.process_voice_input(
        simulate_text="Hello Pi-Jarvis, how are you today?"
    )
    
    if turn.success:
        print("✅ Conversation turn successful!")
        print(f"   👤 User: {turn.user_text}")
        print(f"   🤖 Assistant: {turn.assistant_text}")
        print(f"   ⏱️  Timing: STT={turn.stt_time:.2f}s, LLM={turn.llm_time:.2f}s, TTS={turn.tts_time:.2f}s")
        print(f"   🎯 Total: {turn.total_time:.2f}s")
        return True
    else:
        print(f"❌ Conversation turn failed: {turn.error_message}")
        return False


async def test_multiple_conversation_turns(pipeline: SpeechPipeline):
    """Test multiple conversation turns."""
    print("\n🎭 Testing multiple conversation turns...")
    
    test_inputs = [
        "Hello, how are you?",
        "What's your name?",
        "What can you help me with?",
        "Tell me about artificial intelligence",
        "Thank you for your help"
    ]
    
    successful_turns = 0
    total_time = 0
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n--- Turn {i}/5 ---")
        print(f"👤 Simulated input: '{test_input}'")
        
        turn = await pipeline.process_voice_input(simulate_text=test_input)
        
        if turn.success:
            print(f"🤖 Response: '{turn.assistant_text}'")
            print(f"⏱️  Time: {turn.total_time:.2f}s")
            successful_turns += 1
            total_time += turn.total_time
        else:
            print(f"❌ Turn failed: {turn.error_message}")
    
    print(f"\n📊 Multi-turn Results:")
    print(f"   Successful: {successful_turns}/5 turns")
    print(f"   Average time: {total_time/max(successful_turns, 1):.2f}s per turn")
    
    return successful_turns >= 4  # At least 4/5 should succeed


async def test_conversation_loop(pipeline: SpeechPipeline):
    """Test the complete conversation loop."""
    print("\n🔄 Testing conversation loop...")
    
    conversation_turns = await pipeline.conversation_loop(max_turns=3)
    
    successful_turns = sum(1 for turn in conversation_turns if turn.success)
    
    print(f"\n📋 Conversation Loop Results:")
    print(f"   Completed turns: {len(conversation_turns)}")
    print(f"   Successful turns: {successful_turns}")
    
    if successful_turns >= 2:
        print("✅ Conversation loop working well")
        return True
    else:
        print("⚠️  Conversation loop had issues")
        return False


async def test_performance_monitoring(pipeline: SpeechPipeline):
    """Test performance monitoring and statistics."""
    print("\n📊 Testing performance monitoring...")
    
    # Run a few turns to generate data
    for i in range(3):
        await pipeline.process_voice_input(
            simulate_text=f"Test message number {i+1}"
        )
    
    stats = pipeline.get_performance_stats()
    
    if "error" not in stats:
        print("✅ Performance stats generated successfully:")
        print(f"   Success rate: {stats['success_rate']:.1f}%")
        print(f"   Average response time: {stats['average_total_time']:.2f}s")
        print(f"   LLM processing time: {stats['average_llm_time']:.2f}s")
        return True
    else:
        print(f"❌ Performance stats failed: {stats['error']}")
        return False


async def test_different_pipeline_modes():
    """Test different pipeline operating modes."""
    print("\n🔀 Testing different pipeline modes...")
    
    modes_to_test = [
        (PipelineMode.SIMULATION, "Simulation mode"),
        (PipelineMode.TEXT_ONLY, "Text-only mode")
    ]
    
    results = {}
    
    for mode, description in modes_to_test:
        print(f"\n--- Testing {description} ---")
        
        pipeline = SpeechPipeline(mode=mode)
        init_success = await pipeline.initialize()
        
        if init_success:
            turn = await pipeline.process_voice_input(
                simulate_text="Hello, this is a mode test"
            )
            results[mode] = turn.success
            print(f"✅ {description}: {'Working' if turn.success else 'Failed'}")
        else:
            results[mode] = False
            print(f"❌ {description}: Initialization failed")
        
        pipeline.cleanup()
    
    working_modes = sum(1 for success in results.values() if success)
    print(f"\n📋 Mode Testing Results: {working_modes}/{len(modes_to_test)} modes working")
    
    return working_modes >= 1


async def main():
    """Main test function."""
    print("🎯 Pi-Jarvis Complete Speech Pipeline Testing")
    print("=" * 55)
    print("📝 Note: Testing in SIMULATION mode (no hardware required)")
    print("=" * 55)
    
    test_results = []
    pipeline = None
    
    try:
        # Test 1: Pipeline Initialization
        pipeline = await test_pipeline_initialization()
        test_results.append(("Pipeline Initialization", pipeline is not None))
        
        if not pipeline:
            print("\n❌ Cannot proceed - pipeline initialization failed")
            return
        
        # Test 2: Single Conversation Turn
        single_turn_success = await test_single_conversation_turn(pipeline)
        test_results.append(("Single Conversation Turn", single_turn_success))
        
        # Test 3: Multiple Conversation Turns
        multi_turn_success = await test_multiple_conversation_turns(pipeline)
        test_results.append(("Multiple Conversation Turns", multi_turn_success))
        
        # Test 4: Conversation Loop
        loop_success = await test_conversation_loop(pipeline)
        test_results.append(("Conversation Loop", loop_success))
        
        # Test 5: Performance Monitoring
        perf_success = await test_performance_monitoring(pipeline)
        test_results.append(("Performance Monitoring", perf_success))
        
        # Test 6: Different Pipeline Modes
        modes_success = await test_different_pipeline_modes()
        test_results.append(("Pipeline Modes", modes_success))
        
        # Summary
        print("\n" + "=" * 55)
        print("🎯 COMPLETE SPEECH PIPELINE TEST SUMMARY")
        print("=" * 55)
        
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        passed_tests = sum(1 for _, success in test_results if success)
        total_tests = len(test_results)
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests >= 5:  # At least 5/6 tests should pass
            print("\n🎉 SPEECH PIPELINE READY FOR PHASE 5!")
            print("🎯 Next: Hot-word detection integration ('Hey Pi')")
        elif passed_tests >= 3:
            print("\n⚠️  Speech pipeline has basic functionality")
            print("🔧 Some issues detected - review failed tests")
        else:
            print("\n❌ Speech pipeline needs significant work")
            print("🔧 Please review and fix failed components")
        
        print("\n📋 When hardware is connected:")
        print("   - Change mode to PipelineMode.HARDWARE")
        print("   - Test with real microphone and speakers")
        print("   - Verify end-to-end voice conversation")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test failed")
    finally:
        if pipeline:
            pipeline.cleanup()


if __name__ == "__main__":
    asyncio.run(main())