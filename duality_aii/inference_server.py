"""
FastAPI Inference Server - Offroad Semantic Segmentation
Temporary local API that simulates the future civic backend.

This server exposes a /predict endpoint that can be replaced with the civic backend
when it becomes available. The API contract is standardized for easy integration.

Usage:
    uvicorn inference_server:app --host 0.0.0.0 --port 8000

Environment Variables:
    MODEL_CHECKPOINT: Path to segmentation head checkpoint (default: ./segmentation_head.pth)
    CLASS_NAMES_JSON: Path to class names JSON (optional)
    DEVICE: torch device ('cpu' or 'cuda', default: auto)
    UPLOAD_DIR: Directory for uploading images (default: ./uploads)
    API_PORT: Port to run API on (default: 8000)
"""

import base64
import os
import io
from pathlib import Path
from typing import Optional, List

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image
import torch

from predict import SegmentationModel


# ============================================================================
# CONFIG
# ============================================================================

MODEL_CHECKPOINT = os.getenv("MODEL_CHECKPOINT", "./segmentation_head.pth")
CLASS_NAMES_JSON = os.getenv("CLASS_NAMES_JSON")
DEVICE = os.getenv("DEVICE")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
API_PORT = int(os.getenv("API_PORT", 8000))

# Create upload directory
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Offroad Segmentation API",
    description="ML inference API for semantic segmentation. Simulates future civic backend.",
    version="1.0.0",
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# GLOBAL MODEL (Loaded once at startup)
# ============================================================================

model: Optional[SegmentationModel] = None


@app.on_event("startup")
async def load_model():
    """Load model once at server startup."""
    global model
    
    try:
        print(f"Loading model from: {MODEL_CHECKPOINT}")
        print(f"Device: {DEVICE or 'auto'}")
        
        if not os.path.exists(MODEL_CHECKPOINT):
            raise FileNotFoundError(
                f"Model checkpoint not found: {MODEL_CHECKPOINT}\n"
                "Please set MODEL_CHECKPOINT environment variable or ensure checkpoint exists."
            )
        
        model = SegmentationModel(
            checkpoint_path=MODEL_CHECKPOINT,
            class_names_path=CLASS_NAMES_JSON,
            device=DEVICE,
        )
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        raise


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": model.device if model else None,
        "num_classes": model.out_channels if model else None,
        "class_names": model.class_names if model else None,
    }


# ============================================================================
# MAIN PREDICTION ENDPOINT
# ============================================================================

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    """
    Main prediction endpoint.
    
    Request:
        - file: Image file (PNG, JPG, etc.)
    
    Response:
        {
            "success": bool,
            "mask": str (base64-encoded PNG),
            "overlay": str (base64-encoded PNG),
            "class_distribution": {class_name: percentage, ...},
            "coverage": [[class_name, percentage], ...],
            "num_classes": int,
            "image_width": int,
            "image_height": int,
        }
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Read uploaded file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Store original dimensions
        orig_width, orig_height = image.size
        
        # Run inference
        result = model.predict(image)
        
        # Prepare response with base64-encoded images
        response = {
            "success": True,
            "mask": SegmentationModel.image_to_base64(result["color_mask"]),
            "overlay": SegmentationModel.image_to_base64(result["overlay"]),
            "class_distribution": result["class_distribution"],
            "coverage": result["coverage"],
            "num_classes": model.out_channels,
            "image_width": orig_width,
            "image_height": orig_height,
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": str(e),
            }
        )


# ============================================================================
# BATCH PREDICTION ENDPOINT
# ============================================================================

@app.post("/predict-batch")
async def predict_batch_endpoint(files: List[UploadFile] = File(...)):
    """
    Batch prediction endpoint for multiple images.
    
    Request:
        - files: Multiple image files
    
    Response:
        {
            "success": bool,
            "results": [
                {prediction result for each image}
            ],
            "total_images": int,
            "successful": int,
            "failed": int,
            "processing_time_ms": float,
        }
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    import time
    start_time = time.time()
    
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert("RGB")
            orig_width, orig_height = image.size
            
            result = model.predict(image)
            
            results.append({
                "filename": file.filename,
                "success": True,
                "mask": SegmentationModel.image_to_base64(result["color_mask"]),
                "overlay": SegmentationModel.image_to_base64(result["overlay"]),
                "class_distribution": result["class_distribution"],
                "coverage": result["coverage"],
                "image_width": orig_width,
                "image_height": orig_height,
            })
            successful += 1
        
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e),
            })
            failed += 1
    
    processing_time = (time.time() - start_time) * 1000
    
    return JSONResponse(content={
        "success": failed == 0,
        "results": results,
        "total_images": len(files),
        "successful": successful,
        "failed": failed,
        "processing_time_ms": processing_time,
    })


# ============================================================================
# METADATA ENDPOINT
# ============================================================================

@app.get("/metadata")
async def get_metadata():
    """Get model metadata and API information."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "api_version": "1.0.0",
        "model_type": "DINOv2 + ConvNeXt Segmentation Head",
        "num_classes": model.out_channels,
        "class_names": model.class_names,
        "device": model.device,
        "checkpoint_path": model.checkpoint_path,
        "input_height": model.h,
        "input_width": model.w,
        "supported_formats": ["PNG", "JPG", "JPEG", "BMP"],
        "api_endpoints": {
            "/health": "GET - Health check",
            "/metadata": "GET - Model metadata",
            "/predict": "POST - Single image prediction",
            "/predict-batch": "POST - Batch prediction",
        },
    }


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "name": "Offroad Segmentation API",
        "version": "1.0.0",
        "description": "ML inference API for offroad semantic segmentation",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


# ============================================================================
# STARTUP LOGGING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Offroad Segmentation API - Inference Server")
    print("=" * 60)
    print(f"Model checkpoint: {MODEL_CHECKPOINT}")
    print(f"Class names: {CLASS_NAMES_JSON or 'Using defaults'}")
    print(f"Device: {DEVICE or 'auto'}")
    print(f"Upload directory: {UPLOAD_DIR}")
    print("")
    print("Starting server...")
    print(f"API will be available at: http://localhost:{API_PORT}")
    print("Documentation at: http://localhost:{API_PORT}/docs")
    print("=" * 60)
    
    uvicorn.run(
        "inference_server:app",
        host="0.0.0.0",
        port=API_PORT,
        reload=False,
    )
