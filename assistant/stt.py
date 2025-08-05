"""
Speech-to-Text module for Pi-Jarvis using Whisper.cpp

Handles real-time speech transcription with optimized Whisper models.
"""

import asyncio
import logging
import subprocess
import tempfile
import wave
import os
from pathlib import Path
from typing import Optional, Dict, Any
import pyaudio

from .config import config

logger = logging.getLogger(__name__)


class WhisperSTT:
    """Speech-to-Text using Whisper.cpp for Pi-Jarvis."""
    
    def __init__(self, model_name: str = "tiny"):
        """Initialize Whisper STT.
        
        Args:
            model_name: Model to use ('tiny' or 'small')
        """
        self.model_name = model_name
        self.model_path = Path(f"models/ggml-{model_name}.bin")
        self.whisper_binary = Path("models/whisper.cpp/main")
        self.audio = None
        self.is_recording = False
        
        logger.info(f"Initializing WhisperSTT with model: {model_name}")
    
    def initialize(self) -> bool:
        """Initialize the STT system.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Check if model exists
            if not self.model_path.exists():
                logger.error(f"Model not found: {self.model_path}")
                return False
            
            # Check if Whisper binary exists
            if not self.whisper_binary.exists():
                logger.error(f"Whisper binary not found: {self.whisper_binary}")
                return False
            
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Test Whisper binary
            result = subprocess.run([str(self.whisper_binary), "--help"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                logger.error("Whisper binary test failed")
                return False
            
            logger.info("WhisperSTT initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WhisperSTT: {e}")
            return False
    
    def record_audio(self, duration: int = 5, sample_rate: int = 16000) -> Optional[str]:
        """Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Audio sample rate
            
        Returns:
            Path to recorded WAV file or None if failed
        """
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            logger.info(f"Recording {duration} seconds of audio...")
            
            # Record audio using arecord (more reliable than PyAudio for Pi)
            cmd = [
                "arecord",
                "-f", "S16_LE",  # 16-bit signed little endian
                "-r", str(sample_rate),  # Sample rate
                "-c", "1",  # Mono
                "-d", str(duration),  # Duration
                temp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Recording failed: {result.stderr}")
                os.unlink(temp_path)
                return None
            
            # Verify file was created and has content
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                logger.info(f"Audio recorded: {temp_path}")
                return temp_path
            else:
                logger.error("Recording failed - no audio data")
                return None
                
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None
    
    def transcribe_file(self, audio_file: str) -> Optional[str]:
        """Transcribe audio file using Whisper.cpp.
        
        Args:
            audio_file: Path to WAV audio file
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            if not os.path.exists(audio_file):
                logger.error(f"Audio file not found: {audio_file}")
                return None
            
            logger.info(f"Transcribing audio file: {audio_file}")
            
            # Run Whisper.cpp
            cmd = [
                str(self.whisper_binary),
                "-m", str(self.model_path),
                "-f", audio_file,
                "--output-txt",  # Output as text
                "--no-prints"    # Reduce verbose output
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Whisper transcription failed: {result.stderr}")
                return None
            
            # Read transcription result
            # Whisper.cpp creates a .txt file alongside the input
            txt_file = audio_file.replace(".wav", ".txt")
            if os.path.exists(txt_file):
                with open(txt_file, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                
                # Clean up temp files
                os.unlink(txt_file)
                
                logger.info(f"Transcription result: '{text}'")
                return text
            else:
                logger.error("Transcription output file not found")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Whisper transcription timed out")
            return None
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def transcribe_speech(self, duration: int = 5) -> Optional[str]:
        """Record and transcribe speech.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text or None if failed
        """
        # Record audio
        audio_file = self.record_audio(duration)
        if not audio_file:
            return None
        
        try:
            # Transcribe in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, self.transcribe_file, audio_file)
            return text
        finally:
            # Clean up audio file
            if audio_file and os.path.exists(audio_file):
                os.unlink(audio_file)
    
    def cleanup(self):
        """Clean up resources."""
        if self.audio:
            self.audio.terminate()
            logger.info("PyAudio terminated")


# Global STT instance
stt_engine = WhisperSTT(model_name="tiny")  # Start with tiny model for speed