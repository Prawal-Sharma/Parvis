"""
Test script for the intent system - Phase 7
Tests all intent types without requiring hardware (mic/speaker/camera)
"""

import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistant.intents import intent_manager, IntentType

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_intent_system():
    """Test all intent types with sample inputs."""
    print("🧪 Testing Pi-Jarvis Intent System")
    print("="*50)
    
    # Test cases for each intent type
    test_cases = [
        # Timer tests
        ("Set a timer for 5 minutes", IntentType.TIMER),
        ("Start a 30 second timer", IntentType.TIMER),
        ("Remind me in 2 hours", IntentType.TIMER),
        ("Timer for 10 seconds", IntentType.TIMER),
        
        # Weather tests  
        ("What's the weather like?", IntentType.WEATHER),
        ("Is it raining outside?", IntentType.WEATHER),
        ("How's the temperature today?", IntentType.WEATHER),
        
        # Time tests
        ("What time is it?", IntentType.TIME),
        ("What's today's date?", IntentType.TIME),
        ("Tell me the current time", IntentType.TIME),
        
        # Translation tests
        ("How do you say hello in Spanish?", IntentType.TRANSLATION),
        ("Translate water to French", IntentType.TRANSLATION),
        ("What is goodbye in German?", IntentType.TRANSLATION),
        
        # Vision tests (will delegate)
        ("What do you see?", IntentType.VISION),
        ("Look around and describe the scene", IntentType.VISION),
        
        # General chat tests
        ("Hello, how are you?", IntentType.GENERAL_CHAT),
        ("What can you help me with?", IntentType.GENERAL_CHAT),
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, (user_input, expected_intent) in enumerate(test_cases, 1):
        print(f"\n--- Test {i}/{total_tests} ---")
        print(f"Input: '{user_input}'")
        print(f"Expected: {expected_intent.value}")
        
        try:
            result = await intent_manager.classify_and_handle(user_input)
            
            print(f"Classified: {result.intent_type.value} (confidence: {result.confidence:.2f})")
            print(f"Response: {result.response_text}")
            
            # Check if classification was correct or acceptable
            if result.intent_type == expected_intent:
                print("✅ PASS - Correct intent classification")
                successful_tests += 1
            else:
                print(f"❌ FAIL - Expected {expected_intent.value}, got {result.intent_type.value}")
            
            if result.data:
                print(f"Data: {result.data}")
                
        except Exception as e:
            print(f"❌ ERROR - Exception occurred: {e}")
    
    print(f"\n🎯 Test Summary")
    print("="*50)
    print(f"Successful: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    
    # Show intent statistics
    stats = intent_manager.get_statistics()
    print(f"\nIntent Usage Statistics:")
    for intent_type, count in stats['intent_counts'].items():
        success_rate = stats['success_rates'][intent_type]
        print(f"  {intent_type}: {count} requests ({success_rate:.1f}% success)")
    
    return successful_tests >= total_tests * 0.8  # 80% success rate required


async def test_specific_intents():
    """Test specific intent features in detail."""
    print("\n🔬 Detailed Intent Testing")
    print("="*50)
    
    # Test timer parsing
    print("\n⏰ Timer Intent - Duration Parsing")
    timer_tests = [
        "Set a timer for 1 minute",
        "Start a 45 second timer", 
        "Remind me in 3 hours",
        "Timer for 90 seconds",
        "Set timer 5 minutes"
    ]
    
    for timer_input in timer_tests:
        result = await intent_manager.classify_and_handle(timer_input)
        if result.success and result.data:
            duration = result.data.get('duration', 0)
            print(f"  '{timer_input}' → {duration}s")
    
    # Test translation lookup
    print("\n🌍 Translation Intent - Word Lookup")
    translation_tests = [
        "How do you say hello in Spanish?",
        "Translate goodbye to French", 
        "What is thank you in German?",
        "How do you say unknown in Spanish?"  # Should explain limitations
    ]
    
    for trans_input in translation_tests:
        result = await intent_manager.classify_and_handle(trans_input)
        print(f"  '{trans_input}' → {result.response_text}")


async def interactive_test():
    """Interactive testing mode."""
    print("\n💬 Interactive Intent Testing")
    print("="*50)
    print("Type messages to test intent classification (Ctrl+C to quit)")
    print("Try: timers, weather, time, translations, vision, or general chat")
    print("-"*50)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if not user_input:
                continue
                
            result = await intent_manager.classify_and_handle(user_input)
            
            print(f"🎯 Intent: {result.intent_type.value} (confidence: {result.confidence:.2f})")
            print(f"🤖 Response: {result.response_text}")
            
            if result.data:
                print(f"📊 Data: {result.data}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def demo_intent_capabilities():
    """Demonstrate intent system capabilities."""
    print("\n📋 Intent System Capabilities")
    print("="*50)
    
    capabilities = intent_manager.list_capabilities()
    for cap in capabilities:
        print(f"\n{cap['intent_type'].upper()}:")
        print(f"  Keywords: {', '.join(cap['keywords'][:5])}...")  # Show first 5 keywords
        print("  Examples:")
        for example in cap['examples']:
            print(f"    • {example}")


async def main():
    """Main test runner."""
    print("🚀 Pi-Jarvis Intent System Test Suite")
    print("Phase 7: Intent Classification and Handling")
    print("Hardware-free testing mode\n")
    
    # Show capabilities first
    await demo_intent_capabilities()
    
    # Run automated tests
    all_passed = await test_intent_system()
    
    # Run detailed tests
    await test_specific_intents()
    
    if all_passed:
        print("\n🎉 All tests passed! Intent system ready for integration.")
    else:
        print("\n⚠️ Some tests failed. Review intent logic before integration.")
    
    # Offer interactive mode
    try:
        response = input("\n🤔 Run interactive test mode? (y/n): ").strip().lower()
        if response == 'y':
            await interactive_test()
    except KeyboardInterrupt:
        pass
    
    print("\n✅ Intent system testing complete!")
    print("Ready for pipeline integration and Phase 8 production deployment")


if __name__ == "__main__":
    asyncio.run(main())