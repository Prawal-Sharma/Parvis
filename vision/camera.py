"""
Camera Interface for Pi-Jarvis
Phase 6: Pi Camera v3 Integration

Handles camera capture and image processing for vision analysis.
Supports both real Pi Camera and simulation modes.
"""

import logging
import time
import asyncio
from typing import Optional, Tuple, List
from pathlib import Path
import tempfile
import os

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    # Pi Camera specific imports
    from picamera2 import Picamera2
    import libcamera
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False

import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class PiCameraInterface:
    """Interface for Pi Camera v3 capture."""
    
    def __init__(self):
        """Initialize Pi Camera interface."""
        self.camera = None
        self.is_initialized = False
        logger.info("Initializing Pi Camera interface")
    
    def initialize(self) -> bool:
        """Initialize the Pi Camera.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if not PICAMERA_AVAILABLE:
            logger.error("picamera2 not available - install with: pip install picamera2")
            return False
        
        try:
            logger.info("Initializing Pi Camera v3...")
            self.camera = Picamera2()
            
            # Configure camera
            config = self.camera.create_still_configuration(
                main={"size": (1920, 1080)},  # Full HD
                lores={"size": (640, 480)},   # Lower resolution for processing
                display="lores"
            )
            self.camera.configure(config)
            
            # Start camera
            self.camera.start()
            time.sleep(2)  # Allow camera to warm up
            
            self.is_initialized = True
            logger.info("✅ Pi Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Pi Camera: {e}")
            return False
    
    async def capture_image(self, output_path: Optional[str] = None) -> Optional[str]:
        """Capture an image from the Pi Camera.
        
        Args:
            output_path: Path to save image (optional, creates temp file if None)
            
        Returns:
            Path to captured image file, None if failed
        """
        if not self.is_initialized or not self.camera:
            logger.error("Pi Camera not initialized")
            return None
        
        try:
            if output_path is None:
                # Create temporary file
                temp_fd, output_path = tempfile.mkstemp(suffix='.jpg', prefix='parvis_capture_')
                os.close(temp_fd)
            
            logger.info(f"Capturing image to: {output_path}")
            
            # Capture image
            self.camera.capture_file(output_path)
            
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ Image captured successfully ({file_size} bytes)")
                return output_path
            else:
                logger.error("❌ Image capture failed - file not created")
                return None
                
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return None
    
    def cleanup(self):
        """Clean up camera resources."""
        if self.camera:
            try:
                self.camera.stop()
                self.camera.close()
                logger.info("Pi Camera cleanup complete")
            except Exception as e:
                logger.error(f"Error during camera cleanup: {e}")
        
        self.camera = None
        self.is_initialized = False


class MockCameraInterface:
    """Mock camera interface for testing without hardware."""
    
    def __init__(self):
        """Initialize mock camera."""
        self.is_initialized = False
        logger.info("Initializing Mock Camera interface")
    
    def initialize(self) -> bool:
        """Mock initialization - always succeeds."""
        self.is_initialized = True
        logger.info("✅ Mock Camera initialized")
        return True
    
    async def capture_image(self, output_path: Optional[str] = None) -> Optional[str]:
        """Create a mock image for testing.
        
        Args:
            output_path: Path to save mock image
            
        Returns:
            Path to mock image file
        """
        try:
            if output_path is None:
                temp_fd, output_path = tempfile.mkstemp(suffix='.jpg', prefix='parvis_mock_')
                os.close(temp_fd)
            
            logger.info(f"Creating mock image: {output_path}")
            
            # Create a simple test image
            width, height = 640, 480
            image = Image.new('RGB', (width, height), color='lightblue')
            draw = ImageDraw.Draw(image)
            
            # Add some mock objects
            # Rectangle (could be a "book")
            draw.rectangle([100, 150, 200, 250], fill='brown', outline='black', width=2)
            draw.text((120, 200), "BOOK", fill='white')
            
            # Circle (could be a "cup")
            draw.ellipse([300, 200, 380, 280], fill='white', outline='black', width=2)
            draw.text((320, 240), "CUP", fill='black')
            
            # Triangle (could be a "warning sign")
            draw.polygon([(450, 280), (500, 180), (550, 280)], fill='yellow', outline='red')
            draw.text((480, 240), "⚠", fill='red')
            
            # Add timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            draw.text((10, 10), f"Mock Camera - {timestamp}", fill='black')
            draw.text((10, height-30), "Simulated Pi Camera v3 Image", fill='darkblue')
            
            # Save image
            image.save(output_path, 'JPEG', quality=85)
            
            # Simulate processing delay
            await asyncio.sleep(0.5)
            
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ Mock image created successfully ({file_size} bytes)")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating mock image: {e}")
            return None
    
    def cleanup(self):
        """Mock cleanup."""
        self.is_initialized = False
        logger.info("Mock Camera cleanup complete")


class UniversalCameraInterface:
    """Universal camera interface that works with any camera or webcam."""
    
    def __init__(self):
        """Initialize universal camera interface."""
        self.camera = None
        self.is_initialized = False
        logger.info("Initializing Universal Camera interface")
    
    def initialize(self) -> bool:
        """Initialize any available camera.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if not OPENCV_AVAILABLE:
            logger.error("OpenCV not available - install with: pip install opencv-python")
            return False
        
        try:
            logger.info("Searching for available cameras...")
            
            # Try different camera indices
            for camera_index in range(5):  # Try cameras 0-4
                try:
                    camera = cv2.VideoCapture(camera_index)
                    if camera.isOpened():
                        # Test capture
                        ret, frame = camera.read()
                        if ret and frame is not None:
                            logger.info(f"✅ Found working camera at index {camera_index}")
                            self.camera = camera
                            self.is_initialized = True
                            return True
                        else:
                            camera.release()
                    else:
                        camera.release()
                except Exception as e:
                    logger.debug(f"Camera {camera_index} failed: {e}")
                    continue
            
            logger.error("No working cameras found")
            return False
            
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            return False
    
    async def capture_image(self, output_path: Optional[str] = None) -> Optional[str]:
        """Capture image from any available camera.
        
        Args:
            output_path: Path to save image
            
        Returns:
            Path to captured image file
        """
        if not self.is_initialized or not self.camera:
            logger.error("Camera not initialized")
            return None
        
        try:
            if output_path is None:
                temp_fd, output_path = tempfile.mkstemp(suffix='.jpg', prefix='parvis_camera_')
                os.close(temp_fd)
            
            logger.info(f"Capturing image to: {output_path}")
            
            # Capture frame
            ret, frame = self.camera.read()
            if not ret or frame is None:
                logger.error("Failed to capture frame")
                return None
            
            # Save image
            success = cv2.imwrite(output_path, frame)
            if success:
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ Image captured successfully ({file_size} bytes)")
                return output_path
            else:
                logger.error("Failed to save captured image")
                return None
                
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return None
    
    def cleanup(self):
        """Clean up camera resources."""
        if self.camera:
            try:
                self.camera.release()
                logger.info("Universal Camera cleanup complete")
            except Exception as e:
                logger.error(f"Error during camera cleanup: {e}")
        
        self.camera = None
        self.is_initialized = False


def create_camera_interface(use_mock: bool = False, 
                          prefer_pi_camera: bool = True) -> "CameraInterface":
    """Create appropriate camera interface.
    
    Args:
        use_mock: Force mock camera for testing
        prefer_pi_camera: Prefer Pi Camera over generic cameras
        
    Returns:
        Camera interface instance
    """
    if use_mock:
        return MockCameraInterface()
    
    if prefer_pi_camera and PICAMERA_AVAILABLE:
        return PiCameraInterface()
    elif OPENCV_AVAILABLE:
        return UniversalCameraInterface()
    else:
        logger.warning("No camera libraries available, using mock camera")
        return MockCameraInterface()


# Global camera instance
camera_interface = create_camera_interface(use_mock=True)  # Default to mock for now