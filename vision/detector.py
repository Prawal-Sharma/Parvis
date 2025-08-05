"""
YOLOv8 Object Detection for Pi-Jarvis
Phase 6: Computer Vision and Object Detection

Uses YOLOv8-nano for efficient object detection on Raspberry Pi 4.
Provides both real detection and mock results for testing.
"""

import logging
import time
import asyncio
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import json

try:
    from ultralytics import YOLO
    import cv2
    import numpy as np
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

from PIL import Image
import tempfile

logger = logging.getLogger(__name__)


class DetectionResult:
    """Represents a single object detection result."""
    
    def __init__(self, 
                 class_name: str, 
                 confidence: float, 
                 bbox: Tuple[int, int, int, int],
                 class_id: int = -1):
        """Initialize detection result.
        
        Args:
            class_name: Name of detected object class
            confidence: Detection confidence (0.0-1.0)
            bbox: Bounding box (x1, y1, x2, y2)
            class_id: Numeric class ID
        """
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.class_id = class_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'class_name': self.class_name,
            'confidence': self.confidence,
            'bbox': self.bbox,
            'class_id': self.class_id
        }
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.class_name} ({self.confidence:.2f})"


class YOLOv8Detector:
    """YOLOv8-nano object detector optimized for Raspberry Pi 4."""
    
    def __init__(self, model_name: str = "yolov8n.pt"):
        """Initialize YOLOv8 detector.
        
        Args:
            model_name: YOLOv8 model name (yolov8n.pt for nano)
        """
        self.model_name = model_name
        self.model = None
        self.is_initialized = False
        self.class_names = []
        
        logger.info(f"Initializing YOLOv8 detector with model: {model_name}")
    
    async def initialize(self) -> bool:
        """Initialize YOLOv8 model.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if not YOLO_AVAILABLE:
            logger.error("YOLOv8 not available - install with: pip install ultralytics")
            return False
        
        try:
            logger.info("Loading YOLOv8 model...")
            
            # Load model (will download if not present)
            self.model = YOLO(self.model_name)
            
            # Get class names
            self.class_names = list(self.model.names.values())
            
            logger.info(f"✅ YOLOv8 model loaded successfully")
            logger.info(f"Model supports {len(self.class_names)} object classes")
            logger.info(f"Sample classes: {self.class_names[:10]}...")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize YOLOv8: {e}")
            return False
    
    async def detect_objects(self, 
                           image_path: str, 
                           confidence_threshold: float = 0.25) -> List[DetectionResult]:
        """Detect objects in an image.
        
        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence for detections
            
        Returns:
            List of detection results
        """
        if not self.is_initialized or not self.model:
            logger.error("YOLOv8 detector not initialized")
            return []
        
        if not Path(image_path).exists():
            logger.error(f"Image file not found: {image_path}")
            return []
        
        try:
            logger.info(f"Running object detection on: {image_path}")
            start_time = time.time()
            
            # Run inference
            results = self.model(image_path, conf=confidence_threshold, verbose=False)
            
            detection_time = time.time() - start_time
            logger.info(f"Detection completed in {detection_time:.2f}s")
            
            # Parse results
            detections = []
            if results and len(results) > 0:
                result = results[0]  # First (and only) image
                
                if result.boxes is not None:
                    boxes = result.boxes
                    
                    for i in range(len(boxes.xyxy)):
                        # Extract detection data
                        bbox = boxes.xyxy[i].cpu().numpy().astype(int)  # [x1, y1, x2, y2]
                        confidence = float(boxes.conf[i].cpu().numpy())
                        class_id = int(boxes.cls[i].cpu().numpy())
                        class_name = self.class_names[class_id]
                        
                        detection = DetectionResult(
                            class_name=class_name,
                            confidence=confidence,
                            bbox=tuple(bbox),
                            class_id=class_id
                        )
                        detections.append(detection)
            
            logger.info(f"Found {len(detections)} objects:")
            for detection in detections:
                logger.info(f"  - {detection}")
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during object detection: {e}")
            return []
    
    def cleanup(self):
        """Clean up detector resources."""
        self.model = None
        self.is_initialized = False
        logger.info("YOLOv8 detector cleanup complete")


class MockObjectDetector:
    """Mock object detector for testing without YOLOv8/hardware."""
    
    def __init__(self, model_name: str = "mock_yolov8n"):
        """Initialize mock detector."""
        self.model_name = model_name
        self.is_initialized = False
        
        # Common COCO class names that YOLOv8 recognizes
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 
            'toothbrush'
        ]
        
        logger.info("Initializing Mock Object Detector")
    
    async def initialize(self) -> bool:
        """Mock initialization - always succeeds."""
        self.is_initialized = True
        logger.info("✅ Mock Object Detector initialized")
        logger.info(f"Mock model supports {len(self.class_names)} object classes")
        return True
    
    async def detect_objects(self, 
                           image_path: str, 
                           confidence_threshold: float = 0.25) -> List[DetectionResult]:
        """Generate mock detection results.
        
        Args:
            image_path: Path to image file (used for simulation)
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            List of mock detection results
        """
        if not self.is_initialized:
            logger.error("Mock detector not initialized")
            return []
        
        logger.info(f"Running mock object detection on: {image_path}")
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Generate realistic mock detections based on image name/type
        detections = []
        
        # Analyze image path for context clues
        image_name = Path(image_path).name.lower()
        
        if 'mock' in image_name:
            # For our mock images, return objects that match what we drew
            detections = [
                DetectionResult('book', 0.87, (100, 150, 200, 250), 75),
                DetectionResult('cup', 0.92, (300, 200, 380, 280), 41),
                DetectionResult('stop sign', 0.76, (450, 180, 550, 280), 11)  # Warning triangle as stop sign
            ]
        else:
            # For other images, generate random but realistic detections
            import random
            
            # Common indoor objects
            common_objects = [
                ('person', 0.85), ('chair', 0.78), ('laptop', 0.82), ('book', 0.76),
                ('cup', 0.89), ('bottle', 0.72), ('cell phone', 0.68), ('clock', 0.81),
                ('tv', 0.91), ('remote', 0.67), ('keyboard', 0.74), ('mouse', 0.79)
            ]
            
            # Select 2-4 random objects
            num_objects = random.randint(2, 4)
            selected_objects = random.sample(common_objects, min(num_objects, len(common_objects)))
            
            for obj_name, base_conf in selected_objects:
                # Add some randomness to confidence
                confidence = base_conf + random.uniform(-0.1, 0.1)
                confidence = max(confidence_threshold, min(0.95, confidence))
                
                # Generate random but reasonable bounding box
                x1 = random.randint(50, 300)
                y1 = random.randint(50, 200) 
                x2 = x1 + random.randint(80, 200)
                y2 = y1 + random.randint(60, 150)
                
                class_id = self.class_names.index(obj_name) if obj_name in self.class_names else 0
                
                detection = DetectionResult(obj_name, confidence, (x1, y1, x2, y2), class_id)
                detections.append(detection)
        
        logger.info(f"Mock detection found {len(detections)} objects:")
        for detection in detections:
            logger.info(f"  - {detection}")
        
        return detections
    
    def cleanup(self):
        """Mock cleanup."""
        self.is_initialized = False
        logger.info("Mock Object Detector cleanup complete")


def create_object_detector(use_mock: bool = False, 
                         model_name: str = "yolov8n.pt") -> "ObjectDetector":
    """Create appropriate object detector.
    
    Args:
        use_mock: Use mock detector for testing
        model_name: YOLOv8 model name
        
    Returns:
        Object detector instance
    """
    if use_mock or not YOLO_AVAILABLE:
        return MockObjectDetector(model_name)
    else:
        return YOLOv8Detector(model_name)


def format_detections_for_speech(detections: List[DetectionResult]) -> str:
    """Format detection results for text-to-speech output.
    
    Args:
        detections: List of detection results
        
    Returns:
        Human-readable description of detected objects
    """
    if not detections:
        return "I don't see any recognizable objects in the image."
    
    if len(detections) == 1:
        detection = detections[0]
        return f"I can see a {detection.class_name} with {detection.confidence:.0%} confidence."
    
    # Group by class name
    object_counts = {}
    for detection in detections:
        name = detection.class_name
        if name in object_counts:
            object_counts[name] += 1
        else:
            object_counts[name] = 1
    
    # Create description
    if len(object_counts) == 1:
        name, count = list(object_counts.items())[0]
        if count == 1:
            return f"I can see a {name}."
        else:
            return f"I can see {count} {name}s."
    
    # Multiple object types
    items = []
    for name, count in object_counts.items():
        if count == 1:
            items.append(f"a {name}")
        else:
            items.append(f"{count} {name}s")
    
    if len(items) == 2:
        return f"I can see {items[0]} and {items[1]}."
    else:
        return f"I can see {', '.join(items[:-1])}, and {items[-1]}."


# Global detector instance
object_detector = create_object_detector(use_mock=True)  # Default to mock for now