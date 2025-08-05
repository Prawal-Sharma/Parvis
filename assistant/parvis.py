"""
Complete Parvis Assistant with Hot-word Detection
Phase 5: Integration of "Parvis" wake word with speech pipeline

This is the complete always-on assistant that:
1. Listens for "Parvis" wake word
2. Activates speech pipeline (STT → LLM → TTS)
3. Returns to wake word listening after conversation
"""

import asyncio
import logging
from typing import Optional
from pathlib import Path

from .hotword import create_hotword_detector, PORCUPINE_AVAILABLE
from .pipeline import SpeechPipeline, PipelineMode, ConversationTurn
from vision.pipeline import VisionPipeline

logger = logging.getLogger(__name__)


class ParvisAssistant:
    """Complete always-on Parvis assistant with wake word detection."""
    
    def __init__(self, 
                 pipeline_mode: PipelineMode = PipelineMode.SIMULATION,
                 use_mock_hotword: bool = False,
                 enable_vision: bool = True):
        """Initialize Parvis assistant.
        
        Args:
            pipeline_mode: Speech pipeline mode (hardware/simulation/text_only)
            use_mock_hotword: Use mock hot-word detection for testing
            enable_vision: Enable computer vision capabilities
        """
        self.pipeline_mode = pipeline_mode
        self.use_mock_hotword = use_mock_hotword
        self.enable_vision = enable_vision
        self.is_running = False
        
        # Initialize components
        self.speech_pipeline = SpeechPipeline(mode=pipeline_mode)
        self.hotword_detector = None
        self.vision_pipeline = None
        
        logger.info(f"Initializing Parvis Assistant")
        logger.info(f"  Pipeline mode: {pipeline_mode.value}")
        logger.info(f"  Hot-word mode: {'Mock' if use_mock_hotword else 'Real'}")
        logger.info(f"  Vision enabled: {enable_vision}")
    
    async def initialize(self) -> bool:
        """Initialize all assistant components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        logger.info("🚀 Initializing Parvis Assistant...")
        
        try:
            # Initialize speech pipeline
            logger.info("Initializing speech pipeline...")
            pipeline_ready = await self.speech_pipeline.initialize()
            if not pipeline_ready:
                logger.error("Failed to initialize speech pipeline")
                return False
            logger.info("✅ Speech pipeline ready")
            
            # Initialize hot-word detector
            logger.info("Initializing hot-word detector...")
            self.hotword_detector = create_hotword_detector(
                on_wake_word=self._on_parvis_detected,
                use_mock=self.use_mock_hotword
            )
            
            hotword_ready = self.hotword_detector.initialize()
            if not hotword_ready:
                logger.error("Failed to initialize hot-word detector")
                return False
            logger.info("✅ Hot-word detector ready")
            
            # Initialize vision pipeline if enabled
            if self.enable_vision:
                logger.info("Initializing vision pipeline...")
                self.vision_pipeline = VisionPipeline(
                    use_mock_camera=True,      # Default to mock for now
                    use_mock_detector=True,    # Default to mock for now
                    confidence_threshold=0.25
                )
                
                vision_ready = await self.vision_pipeline.initialize()
                if vision_ready:
                    logger.info("✅ Vision pipeline ready")
                else:
                    logger.warning("⚠️ Vision pipeline failed to initialize - continuing without vision")
                    self.vision_pipeline = None
            
            logger.info("🎉 Parvis Assistant initialization complete!")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def _on_parvis_detected(self):
        """Callback when 'Parvis' wake word is detected."""
        logger.info("🎯 'Parvis' wake word detected!")
        
        try:
            # Temporarily stop hot-word detection during conversation
            self.hotword_detector.stop_listening()
            
            # Activate speech pipeline for conversation
            await self._handle_conversation()
            
            # Resume hot-word detection
            if self.is_running:
                logger.info("🎤 Resuming wake word detection...")
                await self.hotword_detector.start_listening()
                
        except Exception as e:
            logger.error(f"Error handling wake word: {e}")
            # Resume listening even if there was an error
            if self.is_running:
                await self.hotword_detector.start_listening()
    
    async def _handle_conversation(self):
        """Handle a complete conversation after wake word detection."""
        logger.info("🗣️ Starting conversation...")
        
        try:
            if self.pipeline_mode == PipelineMode.HARDWARE:
                # Real hardware conversation
                turn = await self.speech_pipeline.process_voice_input(
                    audio_duration=5  # Listen for 5 seconds
                )
            else:
                # Simulation/test conversation with vision support
                test_inputs = [
                    "Hello Parvis!",
                    "How are you today?", 
                    "What can you help me with?",
                    "Tell me about yourself",
                    "What do you see?",
                    "Describe what's in front of you",
                    "Look around and tell me what's there"
                ]
                
                # Pick a random test input for variety
                import random
                test_input = random.choice(test_inputs)
                
                # Check if this is a vision request
                if self._is_vision_request(test_input):
                    await self._handle_vision_request(test_input)
                    return
                
                turn = await self.speech_pipeline.process_voice_input(
                    simulate_text=test_input
                )
            
            if turn.success:
                # Check if the user's input was a vision request
                if self._is_vision_request(turn.user_text or ""):
                    await self._handle_vision_request(turn.user_text)
                    return
                
                logger.info(f"✅ Conversation completed successfully:")
                logger.info(f"   User: {turn.user_text}")
                logger.info(f"   Parvis: {turn.assistant_text}")
                logger.info(f"   Response time: {turn.total_time:.2f}s")
            else:
                logger.error(f"❌ Conversation failed: {turn.error_message}")
                
        except Exception as e:
            logger.error(f"Error in conversation: {e}")
    
    def _is_vision_request(self, text: str) -> bool:
        """Check if user input is requesting vision functionality.
        
        Args:
            text: User input text
            
        Returns:
            True if this is a vision request
        """
        if not text:
            return False
            
        text_lower = text.lower()
        vision_keywords = [
            "what do you see", "what can you see", "describe what you see",
            "look around", "tell me what you see", "what's in front", 
            "describe the scene", "what's there", "look at", "vision",
            "camera", "image", "picture", "see anything"
        ]
        
        return any(keyword in text_lower for keyword in vision_keywords)
    
    async def _handle_vision_request(self, user_input: str):
        """Handle a vision-related request.
        
        Args:
            user_input: User's vision request
        """
        logger.info(f"👁️ Vision request detected: '{user_input}'")
        
        if not self.vision_pipeline:
            response = "I'm sorry, my vision system is not available right now."
            logger.warning("Vision request but no vision pipeline available")
        else:
            try:
                logger.info("📸 Processing vision request...")
                description = await self.vision_pipeline.describe_scene()
                
                # Add context based on user's request
                if "look around" in user_input.lower():
                    response = f"Looking around, {description.lower()}"
                elif "in front" in user_input.lower():
                    response = f"In front of me, {description.lower()}"
                else:
                    response = description
                
                logger.info(f"👁️ Vision response: '{response}'")
                
            except Exception as e:
                response = f"I'm sorry, I had trouble analyzing the scene. {str(e)}"
                logger.error(f"Vision request failed: {e}")
        
        # Simulate speaking the response (in real mode, this would use TTS)
        if self.pipeline_mode != PipelineMode.HARDWARE:
            logger.info(f"🔊 Parvis would say: '{response}'")
        
        # Update conversation stats
        logger.info(f"✅ Vision conversation completed:")
        logger.info(f"   User: {user_input}")
        logger.info(f"   Parvis: {response}")
    
    async def start(self):
        """Start the always-on Parvis assistant."""
        if not await self.initialize():
            logger.error("Failed to initialize Parvis assistant")
            return
        
        self.is_running = True
        
        logger.info("🎤 Parvis is now listening for wake word...")
        logger.info("Say 'Parvis' to activate the assistant")
        
        if self.use_mock_hotword:
            logger.info("🎭 Using mock mode - will simulate wake word every 15 seconds")
        
        try:
            # Start hot-word detection (this will run indefinitely)
            await self.hotword_detector.start_listening()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the Parvis assistant."""
        logger.info("🛑 Stopping Parvis assistant...")
        
        self.is_running = False
        
        if self.hotword_detector:
            self.hotword_detector.cleanup()
        
        if self.speech_pipeline:
            self.speech_pipeline.cleanup()
        
        if self.vision_pipeline:
            self.vision_pipeline.cleanup()
        
        logger.info("Parvis assistant stopped")
    
    def get_status(self) -> dict:
        """Get current status of the assistant.
        
        Returns:
            Dictionary with status information
        """
        status = {
            "is_running": self.is_running,
            "pipeline_mode": self.pipeline_mode.value,
            "hotword_mode": "mock" if self.use_mock_hotword else "real",
            "vision_enabled": self.enable_vision,
            "vision_available": self.vision_pipeline is not None,
            "porcupine_available": PORCUPINE_AVAILABLE
        }
        
        if hasattr(self.speech_pipeline, 'conversation_history'):
            stats = self.speech_pipeline.get_performance_stats()
            if "error" not in stats:
                status["performance"] = stats
        
        return status


async def run_parvis_assistant(mode: str = "simulation", mock_hotword: bool = True):
    """Run the Parvis assistant with specified mode.
    
    Args:
        mode: Pipeline mode (hardware/simulation/text_only)
        mock_hotword: Use mock hot-word detection
    """
    # Convert mode string to enum
    if mode.lower() == "hardware":
        pipeline_mode = PipelineMode.HARDWARE
    elif mode.lower() == "text_only":
        pipeline_mode = PipelineMode.TEXT_ONLY
    else:
        pipeline_mode = PipelineMode.SIMULATION
    
    # Create and start assistant
    assistant = ParvisAssistant(
        pipeline_mode=pipeline_mode,
        use_mock_hotword=mock_hotword
    )
    
    try:
        await assistant.start()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Assistant failed: {e}")


if __name__ == "__main__":
    import sys
    
    # Simple command line parsing
    mode = "simulation"
    mock_hotword = True
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    
    if len(sys.argv) > 2:
        mock_hotword = sys.argv[2].lower() in ["true", "mock", "1"]
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🤖 Starting Parvis Assistant...")
    print(f"   Mode: {mode}")
    print(f"   Hot-word: {'Mock' if mock_hotword else 'Real'}")
    print("   Say 'Parvis' to activate (or wait for mock detection)")
    print("   Press Ctrl+C to stop")
    
    asyncio.run(run_parvis_assistant(mode, mock_hotword))