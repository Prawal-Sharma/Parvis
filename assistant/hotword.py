"""
Hot-word Detection for Pi-Jarvis
Phase 5: "Parvis" Wake Word Detection

Uses Porcupine for offline hot-word detection.
Only activates the assistant when "Parvis" is spoken.
"""

import logging
import time
import asyncio
from typing import Optional, Callable
from pathlib import Path

try:
    import pvporcupine
    import pyaudio
    import numpy as np
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False

from .config import config

logger = logging.getLogger(__name__)


class ParvisHotwordDetector:
    """Hot-word detector for 'Parvis' wake word."""
    
    def __init__(self, on_wake_word: Optional[Callable] = None):
        """Initialize the hot-word detector.
        
        Args:
            on_wake_word: Callback function to call when "Parvis" is detected
        """
        self.on_wake_word = on_wake_word
        self.is_listening = False
        self.porcupine = None
        self.audio_stream = None
        self.pa = None
        
        # Configuration
        self.access_key = config.hotword.access_key
        self.sensitivity = config.hotword.sensitivity
        self.keyword_paths = config.hotword.keyword_paths
        
        logger.info("Initializing Parvis hot-word detector")
    
    def initialize(self) -> bool:
        """Initialize Porcupine and audio stream.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if not PORCUPINE_AVAILABLE:
            logger.error("Porcupine not available - install pvporcupine")
            return False
        
        if not self.access_key:
            logger.error("Porcupine access key not provided")
            logger.info("Get your free access key from: https://console.picovoice.ai/")
            return False
        
        try:
            # Initialize Porcupine
            logger.info("Initializing Porcupine hot-word engine...")
            
            # Check if custom keyword files exist
            keyword_paths = []
            for keyword_path in self.keyword_paths:
                full_path = Path(keyword_path)
                if not full_path.exists():
                    # Try in models directory
                    full_path = Path("models") / keyword_path
                
                if full_path.exists():
                    keyword_paths.append(str(full_path))
                    logger.info(f"Found keyword file: {full_path}")
                else:
                    logger.warning(f"Keyword file not found: {keyword_path}")
            
            # Use built-in keywords if no custom files found
            if not keyword_paths:
                logger.info("Using Porcupine built-in keywords")
                # Try to find a close match or use available keywords
                available_keywords = pvporcupine.KEYWORDS
                logger.info(f"Available built-in keywords: {list(available_keywords.keys())}")
                
                # Use "picovoice" as closest to "Parvis" if no custom model
                if "picovoice" in available_keywords:
                    keywords = ["picovoice"]
                    logger.info("Using 'picovoice' as temporary wake word (closest to 'Parvis')")
                else:
                    # Fallback to first available keyword
                    keywords = [list(available_keywords.keys())[0]]
                    logger.info(f"Using '{keywords[0]}' as fallback wake word")
                
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keywords=keywords,
                    sensitivities=[self.sensitivity]
                )
            else:
                # Use custom keyword files
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keyword_paths=keyword_paths,
                    sensitivities=[self.sensitivity] * len(keyword_paths)
                )
            
            logger.info("✅ Porcupine initialized successfully")
            
            # Initialize PyAudio
            self.pa = pyaudio.PyAudio()
            
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
                input_device_index=None
            )
            
            logger.info("✅ Audio stream initialized")
            logger.info(f"Sample rate: {self.porcupine.sample_rate}")
            logger.info(f"Frame length: {self.porcupine.frame_length}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize hot-word detector: {e}")
            return False
    
    async def start_listening(self):
        """Start listening for the wake word."""
        if not self.porcupine or not self.audio_stream:
            logger.error("Hot-word detector not initialized")
            return
        
        self.is_listening = True
        logger.info("🎤 Listening for 'Parvis' wake word...")
        
        try:
            while self.is_listening:
                # Read audio data
                try:
                    pcm = self.audio_stream.read(
                        self.porcupine.frame_length,
                        exception_on_overflow=False
                    )
                    pcm = np.frombuffer(pcm, dtype=np.int16)
                    
                    # Process audio frame
                    keyword_index = self.porcupine.process(pcm)
                    
                    if keyword_index >= 0:
                        logger.info("🎯 Wake word 'Parvis' detected!")
                        
                        # Call the wake word callback
                        if self.on_wake_word:
                            if asyncio.iscoroutinefunction(self.on_wake_word):
                                await self.on_wake_word()
                            else:
                                self.on_wake_word()
                    
                    # Small delay to prevent excessive CPU usage
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    logger.error(f"Error processing audio frame: {e}")
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Error in wake word listening loop: {e}")
        finally:
            logger.info("Stopped listening for wake word")
    
    def stop_listening(self):
        """Stop listening for the wake word."""
        self.is_listening = False
        logger.info("Stopping wake word detection...")
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up hot-word detector...")
        
        self.stop_listening()
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
        
        if self.pa:
            self.pa.terminate()
            self.pa = None
        
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
        
        logger.info("Hot-word detector cleanup complete")


class MockHotwordDetector:
    """Mock hot-word detector for testing without Porcupine."""
    
    def __init__(self, on_wake_word: Optional[Callable] = None):
        """Initialize mock detector."""
        self.on_wake_word = on_wake_word
        self.is_listening = False
        logger.info("Initializing Mock hot-word detector (simulation mode)")
    
    def initialize(self) -> bool:
        """Mock initialization - always succeeds."""
        logger.info("✅ Mock hot-word detector initialized")
        return True
    
    async def start_listening(self):
        """Simulate wake word detection at intervals."""
        self.is_listening = True
        logger.info("🎭 Mock listening for 'Parvis' (will trigger every 10 seconds)...")
        
        try:
            while self.is_listening:
                await asyncio.sleep(10)  # Trigger every 10 seconds
                
                if self.is_listening:  # Check again in case we stopped
                    logger.info("🎯 Mock wake word 'Parvis' detected!")
                    
                    if self.on_wake_word:
                        if asyncio.iscoroutinefunction(self.on_wake_word):
                            await self.on_wake_word()
                        else:
                            self.on_wake_word()
                            
        except Exception as e:
            logger.error(f"Error in mock wake word loop: {e}")
    
    def stop_listening(self):
        """Stop mock listening."""
        self.is_listening = False
        logger.info("Stopping mock wake word detection...")
    
    def cleanup(self):
        """Mock cleanup."""
        self.stop_listening()
        logger.info("Mock hot-word detector cleanup complete")


# Factory function to create appropriate detector
def create_hotword_detector(on_wake_word: Optional[Callable] = None, 
                          use_mock: bool = False) -> "ParvisHotwordDetector":
    """Create a hot-word detector instance.
    
    Args:
        on_wake_word: Callback for when wake word is detected
        use_mock: Use mock detector instead of real Porcupine
        
    Returns:
        Hot-word detector instance
    """
    if use_mock or not PORCUPINE_AVAILABLE:
        return MockHotwordDetector(on_wake_word)
    else:
        return ParvisHotwordDetector(on_wake_word)