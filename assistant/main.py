"""
Pi-Jarvis Main Application

Entry point for the Pi-Jarvis assistant system.
Coordinates all components: hot-word detection, STT, LLM, TTS, and vision.
"""

import asyncio
import logging
from typing import Optional
from pathlib import Path


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
    """Main Pi-Jarvis assistant class."""
    
    def __init__(self):
        """Initialize Pi-Jarvis assistant."""
        logger.info("Initializing Pi-Jarvis v1.0")
        self.is_running = False
        
    async def start(self):
        """Start the assistant services."""
        logger.info("Starting Pi-Jarvis assistant...")
        self.is_running = True
        
        # TODO: Initialize components in phases:
        # Phase 1: Environment setup
        # Phase 2: STT (Whisper.cpp)
        # Phase 3: LLM (TinyLlama/Phi-3)
        # Phase 4: STT -> LLM -> TTS loop
        # Phase 5: Hot-word detection (Porcupine)
        # Phase 6: Vision (YOLOv8)
        # Phase 7: Intent system
        
        try:
            while self.is_running:
                await asyncio.sleep(1)
                # Main event loop placeholder
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the assistant services."""
        logger.info("Stopping Pi-Jarvis assistant...")
        self.is_running = False


async def main():
    """Main entry point."""
    assistant = PiJarvis()
    await assistant.start()


if __name__ == "__main__":
    asyncio.run(main())