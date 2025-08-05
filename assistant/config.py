"""
Pi-Jarvis Configuration Management

Handles configuration settings for all components using Pydantic models.
"""

from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field


class AudioConfig(BaseModel):
    """Audio configuration settings."""
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    chunk_size: int = Field(default=1024, description="Audio buffer chunk size")
    channels: int = Field(default=1, description="Number of audio channels")
    device_index: Optional[int] = Field(default=None, description="Audio device index")


class HotwordConfig(BaseModel):
    """Porcupine hot-word detection configuration."""
    access_key: str = Field(default="", description="Porcupine access key (required for Phase 5)")
    keyword_paths: List[str] = Field(default=["parvis_linux.ppn"], description="Keyword model paths for 'Parvis'")
    sensitivity: float = Field(default=0.5, description="Detection sensitivity (0.0-1.0)")


class STTConfig(BaseModel):
    """Speech-to-Text configuration."""
    model_path: str = Field(default="models/ggml-tiny.bin", description="Whisper model path")
    language: str = Field(default="en", description="Target language")
    max_tokens: int = Field(default=500, description="Maximum tokens to generate")


class LLMConfig(BaseModel):
    """Language Model configuration."""
    model_path: str = Field(default="models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf", description="LLM model path")
    max_tokens: int = Field(default=256, description="Maximum response tokens")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    threads: int = Field(default=4, description="Number of CPU threads")


class TTSConfig(BaseModel):
    """Text-to-Speech configuration."""
    engine: str = Field(default="espeak", description="TTS engine (espeak/piper)")
    voice: str = Field(default="en", description="Voice selection")
    speed: int = Field(default=175, description="Speech speed (words per minute)")


class VisionConfig(BaseModel):
    """Computer Vision configuration."""
    model_name: str = Field(default="yolov8n.pt", description="YOLO model name")
    confidence_threshold: float = Field(default=0.5, description="Detection confidence threshold")
    camera_index: int = Field(default=0, description="Camera device index")
    image_size: int = Field(default=640, description="Input image size")


class PiJarvisConfig(BaseModel):
    """Main Pi-Jarvis configuration."""
    
    # Component configurations
    audio: AudioConfig = Field(default_factory=AudioConfig)
    hotword: HotwordConfig = Field(default_factory=HotwordConfig)
    stt: STTConfig = Field(default_factory=STTConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    vision: VisionConfig = Field(default_factory=VisionConfig)
    
    # General settings
    log_level: str = Field(default="INFO", description="Logging level")
    max_conversation_history: int = Field(default=10, description="Max conversation turns to remember")
    response_timeout: float = Field(default=30.0, description="Response timeout in seconds")
    
    # File paths
    models_dir: Path = Field(default=Path("models"), description="Models directory")
    logs_dir: Path = Field(default=Path("/var/log/pi-jarvis"), description="Logs directory")


# Global configuration instance
config = PiJarvisConfig()


def load_config(config_path: Optional[Path] = None) -> PiJarvisConfig:
    """Load configuration from file."""
    if config_path and config_path.exists():
        # TODO: Implement config file loading
        pass
    return config


def save_config(config_obj: PiJarvisConfig, config_path: Path):
    """Save configuration to file."""
    # TODO: Implement config file saving
    pass