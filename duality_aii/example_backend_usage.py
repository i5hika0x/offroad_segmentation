#!/usr/bin/env python
"""
example_backend_usage.py - Example: How to use the ML wrapper directly

This shows how to use the ML wrapper module without the FastAPI server.
Useful if you want to integrate predict.py directly into another backend.

Usage:
    cd duality_aii
    python example_backend_usage.py
"""

from pathlib import Path
import json
from PIL import Image
from predict import SegmentationModel, predict


def example_1_basic_usage():
    """Example 1: Basic model loading and inference"""
    print("=" * 70)
    print("Example 1: Basic Model Loading and Inference")
    print("=" * 70)
    
    # Initialize model (done once at startup)
    checkpoint_path = Path(__file__).parent / "segmentation_head.pth"
    
    if not checkpoint_path.exists():
        print(f"❌ Model checkpoint not found: {checkpoint_path}")
        print("Please ensure segmentation_head.pth exists in duality_aii/")
        return
    
    model = SegmentationModel(
        checkpoint_path=str(checkpoint_path),
        device="cuda",  # or "cpu"
    )
    
    print(f"✓ Model loaded successfully")
    print(f"  Device: {model.device}")
    print(f"  Classes: {model.out_channels}")
    print(f"  Input size: {model.w}x{model.h}")
    print()


def example_2_run_inference():
    """Example 2: Run inference on an image"""
    print("=" * 70)
    print("Example 2: Running Inference")
    print("=" * 70)
    
    checkpoint_path = Path(__file__).parent / "segmentation_head.pth"
    model = SegmentationModel(checkpoint_path=str(checkpoint_path))
    
    # Load image
    image_path = Path(__file__).parent / "test_image.jpg"
    if not image_path.exists():
        print(f"⚠️  Test image not found: {image_path}")
        print("Skipping inference example...")
        return
    
    image = Image.open(image_path).convert("RGB")
    
    # Run inference
    result = predict(image, model)
    
    print(f"✓ Inference completed")
    print(f"  Image size: {result['coverage']}")
    print(f"  Classes detected: {result['num_classes']}")
    print(f"  Top 3 predictions:")
    
    for i, (class_name, percentage) in enumerate(result['coverage'][:3], 1):
        print(f"    {i}. {class_name}: {percentage:.1f}%")
    print()


def example_3_batch_inference():
    """Example 3: Process multiple images"""
    print("=" * 70)
    print("Example 3: Batch Inference")
    print("=" * 70)
    
    checkpoint_path = Path(__file__).parent / "segmentation_head.pth"
    model = SegmentationModel(checkpoint_path=str(checkpoint_path))
    
    # Get all JPEG files in a directory
    image_dir = Path(__file__).parent / "test_images"
    if not image_dir.exists():
        print(f"⚠️  Test images directory not found: {image_dir}")
        print("Skipping batch example...")
        return
    
    image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
    
    if not image_files:
        print(f"⚠️  No images found in: {image_dir}")
        return
    
    print(f"Found {len(image_files)} images")
    print()
    
    results = []
    for i, image_path in enumerate(image_files, 1):
        print(f"  [{i}/{len(image_files)}] Processing {image_path.name}...", end="", flush=True)
        
        try:
            image = Image.open(image_path).convert("RGB")
            result = predict(image, model)
            
            # Extract top class
            top_class = result['coverage'][0]
            results.append({
                "filename": image_path.name,
                "top_class": top_class[0],
                "top_class_percentage": top_class[1],
                "num_classes": result['num_classes'],
            })
            
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
    
    print()
    print("Summary:")
    for result in results:
        print(f"  {result['filename']:<30} → {result['top_class']} ({result['top_class_percentage']:.1f}%)")
    print()


def example_4_integration_pattern():
    """Example 4: Integration pattern for other backends"""
    print("=" * 70)
    print("Example 4: Backend Integration Pattern")
    print("=" * 70)
    
    print("""
When integrating predict.py into another service:

1. In your service's __init__.py or main.py:
   ──────────────────────────────────────────
   from predict import SegmentationModel
   
   # Load model once at startup (global)
   model = SegmentationModel(
       checkpoint_path="./segmentation_head.pth",
       device="cuda",
   )
   
   # Store in global state or dependency injection container
   app.ml_model = model


2. In your API endpoint:
   ──────────────────────
   from predict import predict
   
   @app.post("/predict")
   async def inference_endpoint(file: UploadFile):
       image = Image.open(io.BytesIO(await file.read()))
       
       # Use pre-loaded model
       result = predict(image, app.ml_model)
       
       return {
           "success": True,
           "mask": base64_encode(result['color_mask']),
           "overlay": base64_encode(result['overlay']),
           "class_distribution": result['class_distribution'],
           "coverage": result['coverage'],
       }


3. Response format (standard for all backends):
   ──────────────────────────────────────────
   {
       "success": true,
       "mask": "base64_encoded_png",
       "overlay": "base64_encoded_png",
       "class_distribution": {class_name: percentage, ...},
       "coverage": [[class_name, percentage], ...],
       "num_classes": 10,
       "image_width": 1920,
       "image_height": 1080
   }
    """)
    print()


def example_5_direct_python_usage():
    """Example 5: Using model in your own Python code"""
    print("=" * 70)
    print("Example 5: Direct Python Usage")
    print("=" * 70)
    
    print("""
You can use the ML wrapper in your Python code:

   from PIL import Image
   from predict import SegmentationModel, predict
   
   # Load model (expensive - do once)
   model = SegmentationModel("./segmentation_head.pth")
   
   # Run inference (cheap - reuse model)
   image = Image.open("photo.jpg")
   result = predict(image, model)
   
   # Access results
   print(f"Trees: {result['class_distribution']['Trees']:.1f}%")
   
   # Save visualizations
   import cv2
   cv2.imwrite("mask.png", result['color_mask'])
   cv2.imwrite("overlay.png", result['overlay'])
   
   # Get statistics
   for class_name, percentage in result['coverage']:
       print(f"{class_name}: {percentage:.2f}%")
    """)
    print()


def example_6_error_handling():
    """Example 6: Proper error handling"""
    print("=" * 70)
    print("Example 6: Error Handling")
    print("=" * 70)
    
    print("""
Always handle errors gracefully:

   try:
       model = SegmentationModel("./segmentation_head.pth")
   except FileNotFoundError as e:
       print(f"Model checkpoint not found: {e}")
       return {"error": "Model not available"}
   except torch.cuda.OutOfMemoryError as e:
       print(f"GPU out of memory, using CPU: {e}")
       model = SegmentationModel(
           "./segmentation_head.pth",
           device="cpu"
       )
   
   try:
       result = predict(image, model)
   except Exception as e:
       print(f"Prediction failed: {e}")
       return {"error": "Prediction failed", "details": str(e)}
    """)
    print()


if __name__ == "__main__":
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  ML Wrapper Usage Examples".center(68) + "║")
    print("║" + "  (duality_aii/predict.py)".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # Run examples
    example_1_basic_usage()
    example_2_run_inference()
    example_3_batch_inference()
    example_4_integration_pattern()
    example_5_direct_python_usage()
    example_6_error_handling()
    
    print("=" * 70)
    print("Examples Complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review API_CONTRACT.md for API specifications")
    print("2. Check INTEGRATION_GUIDE.md for setup instructions")
    print("3. Run the FastAPI server: python -m uvicorn inference_server:app")
    print("4. Connect the frontend to http://localhost:8000")
    print()
