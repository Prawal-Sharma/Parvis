"""
Pi-Jarvis Main Application

Entry point for the Pi-Jarvis assistant system.
Coordinates all components: hot-word detection, STT, LLM, TTS, and vision.
"""

import asyncio
import logging
from typing import Optional
from pathlib import Path

from .pipeline import SpeechPipeline, PipelineMode, ConversationTurn


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/pi-jarvis.log')
    ]
)

logger = logging.getLogger(__name__)


class PiJarvis:
    """Main Pi-Jarvis assistant class with complete speech pipeline."""
    
    def __init__(self, mode: PipelineMode = PipelineMode.SIMULATION):
        """Initialize Pi-Jarvis assistant.
        
        Args:
            mode: Pipeline mode (hardware, simulation, or text_only)
        """
        logger.info("Initializing Pi-Jarvis v1.0")
        self.mode = mode
        self.is_running = False
        self.speech_pipeline = SpeechPipeline(mode=mode)
        
    async def start(self):
        """Start the assistant services."""
        logger.info(f"Starting Pi-Jarvis assistant in {self.mode.value} mode...")
        
        # Initialize the complete speech pipeline
        pipeline_ready = await self.speech_pipeline.initialize()
        if not pipeline_ready:
            logger.error("Failed to initialize speech pipeline")
            return
        
        logger.info("🚀 Pi-Jarvis is ready for voice conversations!")
        
        self.is_running = True
        
        try:
            if self.mode == PipelineMode.SIMULATION:
                # Run demo conversation in simulation mode
                await self._run_demo_conversation()
            elif self.mode == PipelineMode.TEXT_ONLY:
                # Run text-only conversation loop
                await self._run_text_conversation()
            else:
                # Hardware mode - wait for voice input
                await self._run_voice_conversation()
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await self.stop()
    
    async def _run_demo_conversation(self):
        """Run a demonstration conversation in simulation mode."""
        logger.info("🎭 Running demonstration conversation...")
        
        conversation_turns = await self.speech_pipeline.conversation_loop(
            max_turns=5,
            audio_duration=5
        )
        
        # Show performance summary
        stats = self.speech_pipeline.get_performance_stats()
        logger.info("📊 Demo conversation complete!")
        logger.info(f"   Success rate: {stats.get('success_rate', 0):.1f}%")
        logger.info(f"   Average response time: {stats.get('average_total_time', 0):.2f}s")
    
    async def _run_text_conversation(self):
        """Run text-only conversation mode."""
        logger.info("💬 Text conversation mode - type your messages")
        print("\n" + "="*50)
        print("🤖 Pi-Jarvis Text Mode")
        print("="*50)
        print("Type your messages below (Ctrl+C to quit)")
        print("-"*50)
        
        while self.is_running:
            try:
                user_input = input("\n👤 You: ").strip()
                if not user_input:
                    continue
                
                print("🤖 Pi-Jarvis is thinking...")
                turn = await self.speech_pipeline.process_voice_input(
                    simulate_text=user_input
                )
                
                if turn.success:
                    print(f"🤖 Pi-Jarvis: {turn.assistant_text}")
                    print(f"⏱️  Response time: {turn.total_time:.2f}s")
                else:
                    print(f"❌ Error: {turn.error_message}")
                    
            except EOFError:
                break
    
    async def _run_voice_conversation(self):
        """Run voice conversation mode (requires hardware)."""
        logger.info("🎤 Voice conversation mode - speak to Pi-Jarvis")
        print("\n" + "="*50)
        print("🎤 Pi-Jarvis Voice Mode")
        print("="*50)
        print("Speak after each prompt (Ctrl+C to quit)")
        print("-"*50)
        
        turn_count = 0
        while self.is_running:
            turn_count += 1
            print(f"\n--- Turn {turn_count} ---")
            print("🎤 Listening... (5 seconds)")
            
            turn = await self.speech_pipeline.process_voice_input(audio_duration=5)
            
            if turn.success:
                print(f"👤 You said: {turn.user_text}")
                print(f"🤖 Pi-Jarvis: {turn.assistant_text}")
                print(f"⏱️  Response time: {turn.total_time:.2f}s")
            else:
                print(f"❌ Error: {turn.error_message}")
                
            # Brief pause between turns
            await asyncio.sleep(2)
    
    async def stop(self):
        """Stop the assistant services."""
        logger.info("Stopping Pi-Jarvis assistant...")
        self.is_running = False
        
        if hasattr(self, 'speech_pipeline'):
            self.speech_pipeline.cleanup()
        
        logger.info("Pi-Jarvis stopped")


async def main():
    """Main entry point with mode selection."""
    import sys
    
    # Simple command line argument parsing
    mode = PipelineMode.SIMULATION  # Default
    
    if len(sys.argv) > 1:
        mode_arg = sys.argv[1].lower()
        if mode_arg == "hardware":
            mode = PipelineMode.HARDWARE
        elif mode_arg == "text":
            mode = PipelineMode.TEXT_ONLY
        elif mode_arg == "simulation":
            mode = PipelineMode.SIMULATION
        else:
            print(f"Unknown mode: {mode_arg}")
            print("Usage: python -m assistant.main [hardware|text|simulation]")
            return
    
    assistant = PiJarvis(mode=mode)
    await assistant.start()


if __name__ == "__main__":
    asyncio.run(main())