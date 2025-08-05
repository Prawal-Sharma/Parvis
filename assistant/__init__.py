"""
Pi-Jarvis Assistant Core Module

This module contains the main assistant application that coordinates:
- Hot-word detection (Porcupine)
- Speech-to-text (Whisper.cpp)
- Language model inference (TinyLlama/Phi-3)
- Text-to-speech (eSpeak NG)
- Intent routing and handling
"""

__version__ = "1.0.0"
__author__ = "Pi-Jarvis Development Team"