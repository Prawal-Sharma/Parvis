"""
Complete Speech Pipeline for Pi-Jarvis
Phase 4: STT → LLM → TTS Integration

Orchestrates the complete voice conversation flow:
1. Speech-to-Text (Whisper.cpp)
2. Language Model (TinyLlama)
3. Text-to-Speech (eSpeak)
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from .stt import stt_engine
from .llm import llm_engine
from .config import config

# Add intent system import
try:
    from .intents import intent_manager, IntentType
    INTENTS_AVAILABLE = True
except ImportError:
    INTENTS_AVAILABLE = False
    logger.warning("Intent system not available - falling back to LLM only")

logger = logging.getLogger(__name__)


class PipelineMode(Enum):
    """Pipeline operating modes."""
    HARDWARE = "hardware"      # Real audio I/O
    SIMULATION = "simulation"  # Mock inputs for testing
    TEXT_ONLY = "text_only"   # Text input/output only


@dataclass
class ConversationTurn:
    """Represents one complete conversation turn."""
    user_audio_file: Optional[str] = None
    user_text: Optional[str] = None
    assistant_text: Optional[str] = None
    assistant_audio_file: Optional[str] = None
    
    # Performance metrics
    stt_time: float = 0.0
    llm_time: float = 0.0
    tts_time: float = 0.0
    total_time: float = 0.0
    
    # Status
    success: bool = False
    error_message: Optional[str] = None


class SpeechPipeline:
    """Complete speech conversation pipeline for Pi-Jarvis."""
    
    def __init__(self, mode: PipelineMode = PipelineMode.SIMULATION):
        """Initialize the speech pipeline.
        
        Args:
            mode: Operating mode for the pipeline
        """
        self.mode = mode
        self.is_initialized = False
        self.conversation_history: List[ConversationTurn] = []
        
        logger.info(f"Initializing SpeechPipeline in {mode.value} mode")
    
    async def initialize(self) -> bool:
        """Initialize all pipeline components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing speech pipeline components...")
            
            # Initialize STT
            if self.mode in [PipelineMode.HARDWARE, PipelineMode.SIMULATION]:
                stt_success = stt_engine.initialize()
                if not stt_success:
                    logger.error("Failed to initialize STT engine")
                    return False
                logger.info("✅ STT engine initialized")
            
            # Initialize LLM
            llm_success = await llm_engine.initialize()
            if not llm_success:
                logger.error("Failed to initialize LLM engine")
                return False
            logger.info("✅ LLM engine initialized")
            
            # TTS is always available (eSpeak)
            logger.info("✅ TTS engine ready (eSpeak)")
            
            self.is_initialized = True
            logger.info("🚀 Speech pipeline initialization complete!")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            return False
    
    async def process_voice_input(self, 
                                audio_duration: int = 5,
                                simulate_text: Optional[str] = None) -> ConversationTurn:
        """Process a complete voice conversation turn.
        
        Args:
            audio_duration: Recording duration in seconds (hardware mode)
            simulate_text: Simulated user input (simulation mode)
            
        Returns:
            ConversationTurn with results and performance metrics
        """
        if not self.is_initialized:
            logger.error("Pipeline not initialized")
            return ConversationTurn(success=False, error_message="Pipeline not initialized")
        
        turn = ConversationTurn()
        total_start = time.time()
        
        try:
            # Step 1: Speech-to-Text
            logger.info("🎤 Step 1: Speech-to-Text")
            stt_start = time.time()
            
            if self.mode == PipelineMode.HARDWARE:
                # Real audio recording and transcription
                user_text = await stt_engine.transcribe_speech(audio_duration)
            elif self.mode == PipelineMode.SIMULATION:
                # Simulate STT with provided text or default
                await asyncio.sleep(0.5)  # Simulate processing time
                user_text = simulate_text or "Hello Pi-Jarvis, how are you today?"
                logger.info(f"🎭 Simulated user input: '{user_text}'")
            else:  # TEXT_ONLY
                user_text = simulate_text
            
            turn.stt_time = time.time() - stt_start
            turn.user_text = user_text
            
            if not user_text or not user_text.strip():
                turn.error_message = "No speech detected or transcription failed"
                turn.total_time = time.time() - total_start
                return turn
            
            logger.info(f"✅ STT Result: '{user_text}' ({turn.stt_time:.2f}s)")
            
            # Step 2: Intent Classification and Response Generation
            logger.info("🎯 Step 2: Intent Classification and Response Generation")
            llm_start = time.time()
            
            assistant_text = None
            
            if INTENTS_AVAILABLE:
                # Try intent classification first
                intent_result = await intent_manager.classify_and_handle(user_text)
                
                if intent_result.success and not intent_result.data.get("delegate_to_llm", False) and not intent_result.data.get("delegate_to_vision", False):
                    # Intent was handled successfully
                    assistant_text = intent_result.response_text
                    logger.info(f"✅ Intent handled: {intent_result.intent_type.value} (confidence: {intent_result.confidence:.2f})")
                
                elif intent_result.data and intent_result.data.get("delegate_to_vision", False):
                    # This is a vision request - delegate to vision system
                    logger.info("👁️ Delegating to vision system...")
                    # For now, return a placeholder - this integrates with existing vision in parvis.py
                    assistant_text = "Let me take a look around... I can see various objects in the scene."
                
                else:
                    # Fall back to LLM for general chat or unknown intents
                    logger.info("🧠 Falling back to Language Model for general conversation...")
                    conversation_prompt = self._build_conversation_prompt(user_text)
                    assistant_text = await llm_engine.generate(conversation_prompt, max_tokens=100)
            else:
                # No intent system available - use LLM directly
                logger.info("🧠 Using Language Model (intent system unavailable)...")
                conversation_prompt = self._build_conversation_prompt(user_text)
                assistant_text = await llm_engine.generate(conversation_prompt, max_tokens=100)
            
            turn.llm_time = time.time() - llm_start
            turn.assistant_text = assistant_text
            
            if not assistant_text or not assistant_text.strip():
                turn.error_message = "No response generated"
                turn.total_time = time.time() - total_start
                return turn
            
            logger.info(f"✅ Response Generated: '{assistant_text}' ({turn.llm_time:.2f}s)")
            
            # Step 3: Text-to-Speech
            logger.info("🔊 Step 3: Text-to-Speech")
            tts_start = time.time()
            
            speech_success = await self._text_to_speech(assistant_text)
            
            turn.tts_time = time.time() - tts_start
            
            if not speech_success:
                turn.error_message = "Text-to-speech failed"
                turn.total_time = time.time() - total_start
                return turn
            
            logger.info(f"✅ TTS Complete ({turn.tts_time:.2f}s)")
            
            # Success!
            turn.success = True
            turn.total_time = time.time() - total_start
            
            # Add to conversation history
            self.conversation_history.append(turn)
            
            # Log performance summary
            logger.info(f"🎯 Conversation Turn Complete:")
            logger.info(f"   STT: {turn.stt_time:.2f}s")
            logger.info(f"   LLM: {turn.llm_time:.2f}s") 
            logger.info(f"   TTS: {turn.tts_time:.2f}s")
            logger.info(f"   Total: {turn.total_time:.2f}s")
            
            return turn
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            turn.error_message = str(e)
            turn.total_time = time.time() - total_start
            return turn
    
    def _build_conversation_prompt(self, user_input: str) -> str:
        """Build a conversational prompt with context.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Formatted prompt for the language model
        """
        # Basic conversational prompt for now
        # TODO: Add conversation history, system prompts, etc.
        prompt = f"User: {user_input}\nAssistant:"
        return prompt
    
    async def _text_to_speech(self, text: str) -> bool:
        """Convert text to speech using eSpeak.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.mode == PipelineMode.HARDWARE:
                # Real TTS output
                import subprocess
                result = await asyncio.create_subprocess_exec(
                    "espeak", "-s", "150", text,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await result.communicate()
                return result.returncode == 0
                
            elif self.mode == PipelineMode.SIMULATION:
                # Simulate TTS processing time
                await asyncio.sleep(0.3)
                logger.info(f"🔊 Simulated TTS: '{text}'")
                return True
                
            else:  # TEXT_ONLY
                logger.info(f"📝 Assistant: {text}")
                return True
                
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return False
    
    async def conversation_loop(self, 
                              max_turns: int = 10,
                              audio_duration: int = 5) -> List[ConversationTurn]:
        """Run a complete conversation loop.
        
        Args:
            max_turns: Maximum number of conversation turns
            audio_duration: Recording duration per turn (hardware mode)
            
        Returns:
            List of conversation turns
        """
        logger.info(f"🎭 Starting conversation loop (max {max_turns} turns)")
        
        conversation_turns = []
        
        for turn_num in range(1, max_turns + 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"🎯 Conversation Turn {turn_num}/{max_turns}")
            logger.info(f"{'='*50}")
            
            if self.mode == PipelineMode.SIMULATION:
                # Use varied simulated inputs
                simulated_inputs = [
                    "Hello Pi-Jarvis, how are you today?",
                    "What's the weather like?",
                    "Tell me a joke",
                    "What can you help me with?",
                    "Thank you, that was helpful"
                ]
                simulate_text = simulated_inputs[min(turn_num - 1, len(simulated_inputs) - 1)]
            else:
                simulate_text = None
                
            turn = await self.process_voice_input(
                audio_duration=audio_duration,
                simulate_text=simulate_text
            )
            
            conversation_turns.append(turn)
            
            if not turn.success:
                logger.error(f"Turn {turn_num} failed: {turn.error_message}")
                break
            
            # Brief pause between turns
            await asyncio.sleep(1)
        
        # Summary
        successful_turns = sum(1 for turn in conversation_turns if turn.success)
        avg_time = sum(turn.total_time for turn in conversation_turns if turn.success) / max(successful_turns, 1)
        
        logger.info(f"\n🎯 Conversation Summary:")
        logger.info(f"   Successful turns: {successful_turns}/{len(conversation_turns)}")
        logger.info(f"   Average response time: {avg_time:.2f}s")
        
        return conversation_turns
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the pipeline.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.conversation_history:
            return {"error": "No conversation history available"}
        
        successful_turns = [turn for turn in self.conversation_history if turn.success]
        
        if not successful_turns:
            return {"error": "No successful turns in history"}
        
        stats = {
            "total_turns": len(self.conversation_history),
            "successful_turns": len(successful_turns),
            "success_rate": len(successful_turns) / len(self.conversation_history) * 100,
            "average_stt_time": sum(turn.stt_time for turn in successful_turns) / len(successful_turns),
            "average_llm_time": sum(turn.llm_time for turn in successful_turns) / len(successful_turns),
            "average_tts_time": sum(turn.tts_time for turn in successful_turns) / len(successful_turns),
            "average_total_time": sum(turn.total_time for turn in successful_turns) / len(successful_turns),
            "fastest_response": min(turn.total_time for turn in successful_turns),
            "slowest_response": max(turn.total_time for turn in successful_turns)
        }
        
        return stats
    
    def cleanup(self):
        """Clean up pipeline resources."""
        logger.info("Cleaning up speech pipeline...")
        
        if hasattr(stt_engine, 'cleanup'):
            stt_engine.cleanup()
        
        if hasattr(llm_engine, 'cleanup'):
            llm_engine.cleanup()
        
        logger.info("Speech pipeline cleanup complete")


# Global pipeline instance
speech_pipeline = SpeechPipeline(mode=PipelineMode.SIMULATION)