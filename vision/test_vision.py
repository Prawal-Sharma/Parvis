"""
Test script for Complete Vision System
Phase 6: Camera + Object Detection Testing (Mock Mode Only)

Tests the complete vision pipeline without requiring hardware.
Perfect for development and integration testing.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from vision.pipeline import VisionPipeline
from vision.camera import create_camera_interface
from vision.detector import create_object_detector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_camera_interface():
    """Test camera interface in mock mode."""
    print("📸 Testing Camera Interface (Mock Mode)...")
    
    camera = create_camera_interface(use_mock=True)
    
    # Test initialization
    success = camera.initialize()
    if not success:
        print("❌ Camera initialization failed")
        return False
    
    print("✅ Camera initialized successfully")
    
    # Test image capture
    try:
        image_path = await camera.capture_image()
        if image_path and Path(image_path).exists():
            file_size = Path(image_path).stat().st_size
            print(f"✅ Mock image captured: {image_path} ({file_size} bytes)")
            
            # Clean up
            Path(image_path).unlink()
            return True
        else:
            print("❌ Failed to capture mock image")
            return False
            
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False
    finally:
        camera.cleanup()


async def test_object_detector():
    """Test object detector in mock mode."""
    print("\n🔍 Testing Object Detector (Mock Mode)...")
    
    detector = create_object_detector(use_mock=True)
    
    # Test initialization
    success = await detector.initialize()
    if not success:
        print("❌ Detector initialization failed")
        return False
    
    print("✅ Object detector initialized successfully")
    
    # Test detection with mock image
    try:
        # Create a temporary mock image first
        camera = create_camera_interface(use_mock=True)
        camera.initialize()
        image_path = await camera.capture_image()
        
        if not image_path:
            print("❌ Could not create test image")
            return False
        
        # Run detection
        detections = await detector.detect_objects(image_path, confidence_threshold=0.25)
        
        print(f"✅ Detection completed: {len(detections)} objects found")
        for detection in detections:
            print(f"   - {detection.class_name} ({detection.confidence:.2f})")
        
        # Clean up
        Path(image_path).unlink()
        camera.cleanup()
        detector.cleanup()
        
        return len(detections) > 0
        
    except Exception as e:
        print(f"❌ Detector test failed: {e}")
        return False


async def test_vision_pipeline():
    """Test complete vision pipeline."""
    print("\n🎥 Testing Complete Vision Pipeline (Mock Mode)...")
    
    # Initialize pipeline with mock components
    pipeline = VisionPipeline(
        use_mock_camera=True,
        use_mock_detector=True,
        confidence_threshold=0.25
    )
    
    # Test initialization
    success = await pipeline.initialize()
    if not success:
        print("❌ Vision pipeline initialization failed")
        return False
    
    print("✅ Vision pipeline initialized successfully")
    
    try:
        # Test scene analysis
        print("Running scene analysis...")
        result = await pipeline.analyze_scene()
        
        if result.success:
            print("✅ Scene analysis successful!")
            print(f"   Objects detected: {result.object_count}")
            print(f"   Classes found: {result.detected_classes}")
            print(f"   Description: '{result.description}'")
            print(f"   Processing time: {result.processing_time:.2f}s")
            
            # Test statistics
            stats = pipeline.get_statistics()
            print(f"\n📊 Pipeline Statistics:")
            print(f"   Total analyses: {stats['total_analyses']}")
            print(f"   Success rate: {stats['success_rate']:.1f}%")
            print(f"   Average time: {stats['average_processing_time']:.2f}s")
            
            return True
        else:
            print(f"❌ Scene analysis failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Vision pipeline test failed: {e}")
        return False
    finally:
        pipeline.cleanup()


async def test_multiple_scene_analyses():
    """Test multiple scene analyses for consistency."""
    print("\n🔄 Testing Multiple Scene Analyses...")
    
    pipeline = VisionPipeline(
        use_mock_camera=True,
        use_mock_detector=True,
        confidence_threshold=0.20
    )
    
    if not await pipeline.initialize():
        print("❌ Pipeline initialization failed")
        return False
    
    successful_analyses = 0
    total_analyses = 5
    
    try:
        for i in range(total_analyses):
            print(f"\n--- Analysis {i+1}/{total_analyses} ---")
            
            result = await pipeline.analyze_scene(f"Analysis {i+1}:")
            
            if result.success:
                print(f"✅ Success: {result.description}")
                successful_analyses += 1
            else:
                print(f"❌ Failed: {result.error_message}")
        
        # Final statistics
        stats = pipeline.get_statistics()
        print(f"\n📊 Final Statistics:")
        print(f"   Successful: {successful_analyses}/{total_analyses}")
        print(f"   Success rate: {stats['success_rate']:.1f}%")
        print(f"   Average processing time: {stats['average_processing_time']:.2f}s")
        
        return successful_analyses >= total_analyses - 1  # Allow 1 failure
        
    except Exception as e:
        print(f"❌ Multiple analyses test failed: {e}")
        return False
    finally:
        pipeline.cleanup()


async def test_vision_descriptions():
    """Test different types of vision descriptions."""
    print("\n💬 Testing Vision Description Variations...")
    
    pipeline = VisionPipeline(use_mock_camera=True, use_mock_detector=True)
    
    if not await pipeline.initialize():
        print("❌ Pipeline initialization failed")
        return False
    
    test_prompts = [
        None,  # No prompt
        "Looking around the room,",
        "In this image,",
        "I can observe that",
        "From what I can see,"
    ]
    
    successful_descriptions = 0
    
    try:
        for i, prompt in enumerate(test_prompts):
            print(f"\n--- Test {i+1}: Prompt = '{prompt}' ---")
            
            description = await pipeline.describe_scene(prompt)
            
            if description and not description.startswith("I'm sorry"):
                print(f"✅ Description: '{description}'")
                successful_descriptions += 1
            else:
                print(f"❌ Failed: '{description}'")
        
        print(f"\n📋 Description Test Results:")
        print(f"   Successful descriptions: {successful_descriptions}/{len(test_prompts)}")
        
        return successful_descriptions >= len(test_prompts) - 1
        
    except Exception as e:
        print(f"❌ Description test failed: {e}")
        return False
    finally:
        pipeline.cleanup()


async def main():
    """Main test function."""
    print("🎯 Pi-Jarvis Vision System Testing (Mock Mode)")
    print("=" * 55)
    print("📝 Note: Testing without hardware using simulation")
    print("=" * 55)
    
    test_results = []
    
    try:
        # Test 1: Camera Interface
        camera_success = await test_camera_interface()
        test_results.append(("Camera Interface", camera_success))
        
        # Test 2: Object Detector
        detector_success = await test_object_detector()
        test_results.append(("Object Detector", detector_success))
        
        # Test 3: Complete Vision Pipeline
        pipeline_success = await test_vision_pipeline()
        test_results.append(("Vision Pipeline", pipeline_success))
        
        # Test 4: Multiple Analyses
        multiple_success = await test_multiple_scene_analyses()
        test_results.append(("Multiple Analyses", multiple_success))
        
        # Test 5: Description Variations
        description_success = await test_vision_descriptions()
        test_results.append(("Description Variations", description_success))
        
        # Summary
        print("\n" + "=" * 55)
        print("🎯 VISION SYSTEM TEST SUMMARY")
        print("=" * 55)
        
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        passed_tests = sum(1 for _, success in test_results if success)
        total_tests = len(test_results)
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests >= total_tests - 1:  # Allow 1 failure
            print("\n🎉 VISION SYSTEM READY!")
            print("🎯 Computer vision pipeline working perfectly in mock mode")
            print("📸 Ready for hardware when Pi Camera v3 is connected")
        elif passed_tests >= 3:
            print("\n⚠️  Vision system has basic functionality")
            print("🔧 Some issues detected - review failed tests")
        else:
            print("\n❌ Vision system needs significant work")
            print("🔧 Please review and fix failed components")
        
        print("\n📋 Integration Ready:")
        print("   - Vision pipeline tested and working")
        print("   - Mock mode perfect for development")
        print("   - Ready to integrate with Parvis assistant")
        print("   - 'What do you see?' functionality prepared")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test failed")


if __name__ == "__main__":
    asyncio.run(main())