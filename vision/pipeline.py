"""
Complete Vision Pipeline for Pi-Jarvis
Phase 6: Camera + Object Detection Integration

Orchestrates camera capture and object detection for "What do you see?" functionality.
Handles the complete flow: Capture → Detect → Describe → Cleanup
"""

import logging
import time
import asyncio
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import tempfile
import os

from .camera import create_camera_interface, MockCameraInterface, PiCameraInterface, UniversalCameraInterface
from .detector import create_object_detector, DetectionResult, format_detections_for_speech

logger = logging.getLogger(__name__)


class VisionResult:
    """Represents the complete result of a vision analysis."""
    
    def __init__(self, 
                 success: bool = False,
                 image_path: Optional[str] = None,
                 detections: Optional[List[DetectionResult]] = None,
                 description: str = "",
                 error_message: Optional[str] = None,
                 processing_time: float = 0.0):
        """Initialize vision result.
        
        Args:
            success: Whether the vision analysis succeeded
            image_path: Path to captured image
            detections: List of detected objects
            description: Human-readable description
            error_message: Error message if failed
            processing_time: Total processing time in seconds
        """
        self.success = success
        self.image_path = image_path
        self.detections = detections or []
        self.description = description
        self.error_message = error_message
        self.processing_time = processing_time
        
        # Derived metrics
        self.object_count = len(self.detections)
        self.detected_classes = list(set(d.class_name for d in self.detections))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'success': self.success,
            'image_path': self.image_path,
            'detections': [d.to_dict() for d in self.detections],
            'description': self.description,
            'error_message': self.error_message,
            'processing_time': self.processing_time,
            'object_count': self.object_count,
            'detected_classes': self.detected_classes
        }


class VisionPipeline:
    """Complete vision pipeline for Pi-Jarvis computer vision."""
    
    def __init__(self, 
                 use_mock_camera: bool = False,
                 use_mock_detector: bool = False,
                 confidence_threshold: float = 0.25):
        """Initialize vision pipeline.
        
        Args:
            use_mock_camera: Use mock camera for testing
            use_mock_detector: Use mock object detector for testing
            confidence_threshold: Minimum detection confidence
        """
        self.use_mock_camera = use_mock_camera
        self.use_mock_detector = use_mock_detector
        self.confidence_threshold = confidence_threshold
        self.is_initialized = False
        
        # Components
        self.camera = None
        self.detector = None
        
        # Statistics
        self.analysis_count = 0
        self.total_processing_time = 0.0
        self.successful_analyses = 0
        
        logger.info("Initializing Vision Pipeline")
        logger.info(f"  Camera mode: {'Mock' if use_mock_camera else 'Real'}")
        logger.info(f"  Detector mode: {'Mock' if use_mock_detector else 'Real YOLOv8'}")
        logger.info(f"  Confidence threshold: {confidence_threshold}")
    
    async def initialize(self) -> bool:
        """Initialize camera and object detector.
        
        Returns:
            True if initialization successful, False otherwise
        """
        logger.info("🚀 Initializing Vision Pipeline...")
        
        try:
            # Initialize camera
            logger.info("Initializing camera interface...")
            self.camera = create_camera_interface(
                use_mock=self.use_mock_camera,
                prefer_pi_camera=True
            )
            
            camera_ready = self.camera.initialize()
            if not camera_ready:
                logger.error("Failed to initialize camera")
                return False
            logger.info("✅ Camera initialized")
            
            # Initialize object detector
            logger.info("Initializing object detector...")
            self.detector = create_object_detector(
                use_mock=self.use_mock_detector,
                model_name="yolov8n.pt"
            )
            
            detector_ready = await self.detector.initialize()
            if not detector_ready:
                logger.error("Failed to initialize object detector")
                return False
            logger.info("✅ Object detector initialized")
            
            self.is_initialized = True
            logger.info("🎉 Vision Pipeline initialization complete!")
            return True
            
        except Exception as e:
            logger.error(f"Vision pipeline initialization failed: {e}")
            return False
    
    async def analyze_scene(self, description_prompt: Optional[str] = None) -> VisionResult:
        """Analyze the current scene with camera and object detection.
        
        Args:
            description_prompt: Optional context for description generation
            
        Returns:
            VisionResult with analysis results
        """
        if not self.is_initialized:
            return VisionResult(
                success=False,
                error_message="Vision pipeline not initialized"
            )
        
        start_time = time.time()
        temp_image_path = None
        
        try:
            logger.info("🎥 Starting scene analysis...")
            
            # Step 1: Capture image
            logger.info("📸 Capturing image...")
            capture_start = time.time()
            
            temp_image_path = await self.camera.capture_image()
            if not temp_image_path:
                return VisionResult(
                    success=False,
                    error_message="Failed to capture image",
                    processing_time=time.time() - start_time
                )
            
            capture_time = time.time() - capture_start
            logger.info(f"✅ Image captured in {capture_time:.2f}s: {temp_image_path}")
            
            # Step 2: Object detection
            logger.info("🔍 Running object detection...")
            detection_start = time.time()
            
            detections = await self.detector.detect_objects(
                temp_image_path, 
                self.confidence_threshold
            )
            
            detection_time = time.time() - detection_start
            logger.info(f"✅ Object detection completed in {detection_time:.2f}s")
            
            # Step 3: Generate description
            logger.info("💬 Generating description...")
            description = format_detections_for_speech(detections)
            
            # Add context if provided
            if description_prompt:
                description = f"{description_prompt} {description}"
            
            total_time = time.time() - start_time
            
            # Create result
            result = VisionResult(
                success=True,
                image_path=temp_image_path,
                detections=detections,
                description=description,
                processing_time=total_time
            )
            
            # Update statistics
            self.analysis_count += 1
            self.successful_analyses += 1
            self.total_processing_time += total_time
            
            logger.info("🎯 Scene analysis complete!")
            logger.info(f"   Objects found: {len(detections)}")
            logger.info(f"   Description: '{description}'")
            logger.info(f"   Total time: {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during scene analysis: {e}")
            
            result = VisionResult(
                success=False,
                image_path=temp_image_path,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
            
            self.analysis_count += 1
            
            return result
    
    async def describe_scene(self, custom_prompt: Optional[str] = None) -> str:
        """Get a natural language description of the current scene.
        
        Args:
            custom_prompt: Optional custom prompt for description
            
        Returns:
            Natural language description of the scene
        """
        result = await self.analyze_scene(custom_prompt)
        
        if result.success:
            return result.description
        else:
            error_msg = result.error_message or "Unknown error"
            return f"I'm sorry, I couldn't analyze the scene. {error_msg}"
    
    def get_statistics(self) -> Dict:
        """Get vision pipeline statistics.
        
        Returns:
            Dictionary with performance statistics
        """
        if self.analysis_count == 0:
            return {
                "total_analyses": 0,
                "successful_analyses": 0,
                "success_rate": 0.0,
                "average_processing_time": 0.0
            }
        
        return {
            "total_analyses": self.analysis_count,
            "successful_analyses": self.successful_analyses,
            "success_rate": (self.successful_analyses / self.analysis_count) * 100,
            "average_processing_time": self.total_processing_time / self.analysis_count,
            "total_processing_time": self.total_processing_time
        }
    
    def cleanup_temp_files(self, keep_latest: bool = True):
        """Clean up temporary image files.
        
        Args:
            keep_latest: Keep the most recent image file
        """
        try:
            # Find temporary files created by our pipeline
            temp_dir = Path(tempfile.gettempdir())
            parvis_files = list(temp_dir.glob("parvis_*"))
            
            if not parvis_files:
                return
            
            if keep_latest and len(parvis_files) > 1:
                # Sort by modification time, keep the newest
                parvis_files.sort(key=lambda p: p.stat().st_mtime)
                files_to_delete = parvis_files[:-1]
            else:
                files_to_delete = parvis_files
            
            deleted_count = 0
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Could not delete temp file {file_path}: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} temporary image files")
                
        except Exception as e:
            logger.warning(f"Error during temp file cleanup: {e}")
    
    def cleanup(self):
        """Clean up vision pipeline resources."""
        logger.info("Cleaning up Vision Pipeline...")
        
        if self.camera:
            self.camera.cleanup()
            self.camera = None
        
        if self.detector:
            self.detector.cleanup()
            self.detector = None
        
        # Clean up temporary files
        self.cleanup_temp_files(keep_latest=False)
        
        self.is_initialized = False
        logger.info("Vision Pipeline cleanup complete")


# Global vision pipeline instance
vision_pipeline = VisionPipeline(
    use_mock_camera=True,     # Default to mock for testing
    use_mock_detector=True,   # Default to mock for testing
    confidence_threshold=0.25
)