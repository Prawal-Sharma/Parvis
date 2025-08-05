"""
Language Model module for Pi-Jarvis

Handles text generation using llama.cpp or Ollama with TinyLlama/Phi-3 models.
"""

import asyncio
import logging
import subprocess
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
import time

from .config import config

logger = logging.getLogger(__name__)


class LLMEngine:
    """Base Language Model Engine for Pi-Jarvis."""
    
    def __init__(self):
        """Initialize LLM Engine."""
        self.backend = None
        self.is_initialized = False
        logger.info("Initializing LLM Engine")
    
    async def initialize(self) -> bool:
        """Initialize the LLM system (auto-detect backend)."""
        # Try Ollama first
        if await self._try_ollama():
            self.backend = OllamaLLM()
            logger.info("Using Ollama backend")
        # Fallback to llama.cpp
        elif self._try_llamacpp():
            self.backend = LlamaCppLLM()
            logger.info("Using llama.cpp backend")
        else:
            logger.error("No LLM backend available")
            return False
        
        self.is_initialized = await self.backend.initialize()
        return self.is_initialized
    
    async def _try_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'ollama', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            return proc.returncode == 0
        except FileNotFoundError:
            return False
    
    def _try_llamacpp(self) -> bool:
        """Check if llama.cpp is available."""
        llamacpp_binary = Path("models/llama.cpp/build/bin/llama-cli")
        return llamacpp_binary.exists()
    
    async def generate(self, prompt: str, max_tokens: int = 256) -> Optional[str]:
        """Generate text response."""
        if not self.is_initialized:
            logger.error("LLM not initialized")
            return None
        
        return await self.backend.generate(prompt, max_tokens)
    
    def cleanup(self):
        """Clean up resources."""
        if self.backend:
            self.backend.cleanup()


class OllamaLLM:
    """Ollama backend for Pi-Jarvis."""
    
    def __init__(self):
        """Initialize Ollama backend."""
        self.base_url = "http://localhost:11434"
        self.model_name = None
        logger.info("Initializing Ollama backend")
    
    async def initialize(self) -> bool:
        """Initialize Ollama backend."""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                logger.error("Ollama service not running")
                return False
            
            # Get available models
            models = response.json().get('models', [])
            if not models:
                logger.error("No models available in Ollama")
                return False
            
            # Choose model (prefer tinyllama, fallback to first available)
            for model in models:
                if 'tinyllama' in model['name'].lower():
                    self.model_name = model['name']
                    break
            else:
                self.model_name = models[0]['name']
            
            logger.info(f"Using Ollama model: {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            return False
    
    async def generate(self, prompt: str, max_tokens: int = 256) -> Optional[str]:
        """Generate text using Ollama."""
        try:
            # Prepare request
            data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": config.llm.temperature,
                    "top_p": 0.9,
                    "stop": ["Human:", "Assistant:", "\\n\\n"]
                }
            }
            
            logger.info(f"Generating response with Ollama model: {self.model_name}")
            start_time = time.time()
            
            # Make request
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama generation failed: {response.text}")
                return None
            
            result = response.json()
            generated_text = result.get('response', '').strip()
            
            elapsed = time.time() - start_time
            logger.info(f"Generated {len(generated_text)} characters in {elapsed:.2f}s")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return None
    
    def cleanup(self):
        """Clean up Ollama resources."""
        logger.info("Ollama cleanup complete")


class LlamaCppLLM:
    """llama.cpp backend for Pi-Jarvis."""
    
    def __init__(self):
        """Initialize llama.cpp backend."""
        self.binary_path = Path("models/llama.cpp/build/bin/llama-cli")
        self.model_path = None
        logger.info("Initializing llama.cpp backend")
    
    async def initialize(self) -> bool:
        """Initialize llama.cpp backend."""
        try:
            # Check if binary exists
            if not self.binary_path.exists():
                logger.error(f"llama.cpp binary not found: {self.binary_path}")
                return False
            
            # Find available model (prefer TinyLlama)
            model_candidates = [
                "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                "models/Phi-3-mini-4k-instruct-q4.gguf"
            ]
            
            for model_path in model_candidates:
                if Path(model_path).exists():
                    self.model_path = Path(model_path)
                    break
            
            if not self.model_path:
                logger.error("No compatible models found")
                return False
            
            logger.info(f"Using llama.cpp model: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize llama.cpp: {e}")
            return False
    
    async def generate(self, prompt: str, max_tokens: int = 256) -> Optional[str]:
        """Generate text using llama.cpp."""
        try:
            # Prepare command
            cmd = [
                str(self.binary_path),
                "-m", str(self.model_path),
                "-p", prompt,
                "-n", str(max_tokens),
                "--temp", str(config.llm.temperature),
                "-t", str(config.llm.threads),
                "--simple-io",
                "--log-disable"
            ]
            
            logger.info(f"Generating response with llama.cpp")
            start_time = time.time()
            
            # Run llama.cpp
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                logger.error(f"llama.cpp failed: {stderr.decode()}")
                return None
            
            # Extract generated text
            output = stdout.decode().strip()
            if output.startswith(prompt):
                output = output[len(prompt):].strip()
            
            elapsed = time.time() - start_time
            logger.info(f"Generated {len(output)} characters in {elapsed:.2f}s")
            
            return output
            
        except Exception as e:
            logger.error(f"Error generating with llama.cpp: {e}")
            return None
    
    def cleanup(self):
        """Clean up llama.cpp resources."""
        logger.info("llama.cpp cleanup complete")


# Global LLM instance
llm_engine = LLMEngine()