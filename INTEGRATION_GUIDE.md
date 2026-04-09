# Integration Guide - ML Model & Frontend Setup

## Quick Start

This guide will help you:
1. Run the ML model locally
2. Start the inference API server
3. Connect the frontend
4. Prepare for civic backend integration

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Backend Setup (ML Model & API)](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Testing](#testing)
- [Switching to civic Backend](#switching-to-civic-backend)
- [Example Workflows](#example-workflows)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Backend Requirements
- Python 3.8+
- CUDA 11.8+ (optional, for GPU acceleration)
- ~2GB VRAM (GPU) or ~1GB RAM (CPU)
- PyTorch

### Frontend Requirements
- Node.js 16+
- npm or yarn

### Files Needed
- `segmentation_head.pth` - Pre-trained model checkpoint
- `class_names.json` - (Optional) Class name mappings

---

## Backend Setup

### Step 1: Create Python Environment

```bash
cd duality_aii

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate
```

### Step 2: Install Dependencies

Update `requirements.txt` with FastAPI:

```bash
# Install existing requirements
pip install -r requirements_frontend.txt

# Add new dependencies
pip install fastapi uvicorn python-multipart
```

**Full requirements list:**
```
torch
torchvision
fastapi
uvicorn[standard]
python-multipart
opencv-python
pillow
numpy
```

### Step 3: Configure Environment

Create `.env.local` in `duality_aii/`:

```bash
# Copy from template
cp .env.example .env.local

# Edit .env.local and set:
# MODEL_CHECKPOINT=./segmentation_head.pth
# DEVICE=cuda  (or cpu)
# API_PORT=8000
```

### Step 4: Verify Model Files

```bash
ls -la segmentation_head.pth
ls -la class_names.json  # Optional
```

### Step 5: Start Inference Server

```bash
# From duality_aii directory with venv activated
python -m uvicorn inference_server:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

### Step 6: Test Backend

```bash
# Check health
curl http://localhost:8000/health

# Get metadata
curl http://localhost:8000/metadata

# Test prediction (requires test_image.jpg)
curl -X POST http://localhost:8000/predict \
  -F "file=@test_image.jpg"
```

---

## Frontend Setup

### Step 1: Install Dependencies

```bash
cd frontend_da

# Install npm packages
npm install
```

### Step 2: Configure API URL

Create `.env.local` in `frontend_da/`:

```bash
# Copy from template
cp .env.example .env.local

# Verify it contains:
# VITE_API_BASE=http://localhost:8000
# VITE_API_TIMEOUT=60000
```

### Step 3: Start Development Server

```bash
# From frontend_da directory
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  build xxxxx

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### Step 4: Open in Browser

Visit: http://localhost:5173

---

## Testing

### Test Checklist

- [ ] **Backend Health Check**
  ```bash
  curl http://localhost:8000/health
  # Should return status: "healthy"
  ```

- [ ] **Frontend Loads**
  - Visit http://localhost:5173
  - Check browser console for errors
  - Should see upload panel

- [ ] **Single Image Prediction**
  - Upload an image in frontend
  - Should see segmentation mask
  - Should see class distribution

- [ ] **Batch Prediction**
  - Upload multiple images
  - All should process successfully

### API Integration Test

```javascript
// In browser console
const response = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  body: new FormData(document.querySelector('form')),
});

const result = await response.json();
console.log(result);
```

---

## Switching to civic Backend

When the civic backend is integrated, **no code changes needed**! Just update configuration.

### For Backend Developer (civic team):

1. **Implement API endpoints**:
   - `GET /health` - Health check
   - `GET /metadata` - Model metadata
   - `POST /predict` - Single image prediction
   - `POST /predict-batch` - Batch prediction

2. **Response format** (must match contract):
   ```json
   {
     "success": true,
     "mask": "base64_encoded_png",
     "overlay": "base64_encoded_png",
     "class_distribution": {...},
     "coverage": [...],
     "num_classes": 10,
     "image_width": 1920,
     "image_height": 1080
   }
   ```

3. **Error handling**:
   - Return proper HTTP status codes
   - Include error messages in response

### For Frontend Developer (you):

1. **Update environment variable**:
   ```bash
   # .env.local
   VITE_API_BASE=https://civic-api.example.com/api/v1
   ```

2. **Optionally add authentication**:
   ```javascript
   // In segmentationAPI.js
   const apiClient = axios.create({
     baseURL: API_BASE,
     timeout: API_TIMEOUT,
     headers: {
       'Authorization': `Bearer ${import.meta.env.VITE_API_KEY}`
     }
   });
   ```

3. **Test with new backend**:
   ```bash
   npm run dev
   # Upload image - should work with civic backend transparently
   ```

---

## Example Workflows

### Workflow 1: Backend Testing (cURL)

```bash
#!/bin/bash

# Start server in another terminal first
# python -m uvicorn inference_server:app --port 8000

# Health check
echo "=== Health Check ==="
curl http://localhost:8000/health | jq

# Get metadata
echo "=== Metadata ==="
curl http://localhost:8000/metadata | jq

# Predict single image
echo "=== Single Prediction ==="
curl -X POST http://localhost:8000/predict \
  -F "file=@test_image.jpg" | jq

# Batch prediction
echo "=== Batch Prediction ==="
curl -X POST http://localhost:8000/predict-batch \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" | jq
```

### Workflow 2: Backend Testing (Python)

```python
#!/usr/bin/env python
"""
test_api.py - Test the inference API

Usage:
    python test_api.py
"""

import requests
import base64
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health...")
    response = requests.get(f"{API_BASE}/health")
    print(response.json())
    print()

def test_metadata():
    """Test metadata endpoint"""
    print("Testing /metadata...")
    response = requests.get(f"{API_BASE}/metadata")
    data = response.json()
    print(f"Model: {data['model_type']}")
    print(f"Classes: {len(data['class_names'])}")
    print(f"Device: {data['device']}")
    print()

def test_predict(image_path):
    """Test single prediction"""
    print(f"Testing /predict with {image_path}...")
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE}/predict", files=files)
    
    result = response.json()
    
    if result['success']:
        print(f"✓ Prediction successful")
        print(f"  Image size: {result['image_width']}x{result['image_height']}")
        print(f"  Classes: {result['num_classes']}")
        print(f"  Top 3 classes:")
        for class_name, percentage in result['coverage'][:3]:
            print(f"    - {class_name}: {percentage:.1f}%")
    else:
        print(f"✗ Prediction failed: {result['error']}")
    print()

def test_batch_predict(image_paths):
    """Test batch prediction"""
    print(f"Testing /predict-batch with {len(image_paths)} images...")
    
    files = []
    for path in image_paths:
        files.append(('files', open(path, 'rb')))
    
    response = requests.post(f"{API_BASE}/predict-batch", files=files)
    result = response.json()
    
    print(f"✓ Batch prediction complete")
    print(f"  Total: {result['total_images']}")
    print(f"  Successful: {result['successful']}")
    print(f"  Failed: {result['failed']}")
    print(f"  Time: {result['processing_time_ms']:.0f}ms")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Inference API Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_metadata()
        
        # Test with sample images (adjust paths as needed)
        test_predict("test_image.jpg")
        test_batch_predict(["test_image.jpg"])
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the API server is running on http://localhost:8000")
```

Run it:
```bash
python test_api.py
```

### Workflow 3: Frontend Integration Example

```javascript
// In Demo.jsx or your component

import { predict, predictBatch, getMetadata } from '@/api/segmentationAPI';

async function handleImageUpload(imageFile) {
  try {
    // Show loading state
    setLoading(true);
    setError(null);

    // Run prediction
    const result = await predict(imageFile);

    // Display results
    setMaskImage(result.mask);
    setOverlayImage(result.overlay);
    setClassDistribution(result.class_distribution);
    setCoverage(result.coverage);

    setLoading(false);
  } catch (error) {
    setError(error.message);
    setLoading(false);
  }
}

async function handleBatchUpload(imageFiles) {
  try {
    setLoading(true);
    setError(null);

    const result = await predictBatch(imageFiles);

    if (!result.success) {
      setWarning(`Failed to process ${result.failed} images`);
    }

    setBatchResults(result.results);
    setLoading(false);
  } catch (error) {
    setError(error.message);
    setLoading(false);
  }
}

// Component usage
function UploaderComponent() {
  return (
    <div>
      <input 
        type="file" 
        accept="image/*" 
        onChange={(e) => handleImageUpload(e.target.files[0])}
      />
      {loading && <p>Processing...</p>}
      {error && <p style={{color: 'red'}}>{error}</p>}
      {maskImage && <img src={maskImage} alt="Mask" />}
    </div>
  );
}
```

---

## Troubleshooting

### Backend Issues

**Problem:** "Model not found"
```
Solution:
1. Check MODEL_CHECKPOINT path in .env.local
2. Verify segmentation_head.pth exists
3. Use absolute path in .env.local
```

**Problem:** "Out of memory"
```
Solution:
1. Set DEVICE=cpu in .env.local
2. Reduce batch size
3. Check available GPU memory: nvidia-smi
```

**Problem:** "Port already in use"
```
Solution:
# Change port in .env.local
API_PORT=8001

# Or kill existing process (macOS/Linux)
lsof -ti:8000 | xargs kill -9
```

### Frontend Issues

**Problem:** "API connection refused"
```
Solution:
1. Verify backend is running: curl http://localhost:8000/health
2. Check VITE_API_BASE in .env.local
3. Check browser console for exact error
```

**Problem:** "CORS error"
```
Solution:
Backend has CORS enabled. If still failing:
1. Check browser console for CORS error
2. Verify API_BASE URL matches
3. Try http://localhost:8000 (not 127.0.0.1)
```

**Problem:** Images not loading
```
Solution:
1. Check if base64 encoding worked
2. Verify image format is PNG
3. Check Network tab in DevTools
```

### General Issues

**Check logs:**
```bash
# Backend - Check inference_server.py output
# Frontend - Check browser console (F12)
# Network - Check browser Network tab

# Test connectivity
curl http://localhost:8000/health
```

**Reset everything:**
```bash
# Backend
cd duality_aii
rm -rf __pycache__ .*.pyc uploads
kill %1  # Kill uvicorn

# Frontend
cd frontend_da
rm -rf node_modules
npm install
npm run dev
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT SETUP (Local)                        │
└─────────────────────────────────────────────────────────────────┘

    Browser (http://localhost:5173)
            │
            │ HTTP Requests
            │ (JSON + FormData)
            ▼
    ┌───────────────────────┐
    │   React Frontend      │
    │   - Demo Component    │
    │   - Upload Panel      │
    │   - Visualization     │
    └─────────┬─────────────┘
              │
              │ VITE_API_BASE = http://localhost:8000
              │
              ▼
    ┌─────────────────────────────┐
    │   FastAPI Server            │
    │   (inference_server.py)      │
    │   - /predict                │
    │   - /predict-batch          │
    │   - /health                 │
    │   - /metadata               │
    └─────────┬───────────────────┘
              │
              │ Loads model once at startup
              │
              ▼
    ┌─────────────────────────────┐
    │   ML Model (predict.py)      │
    │   - DINOv2 Backbone         │
    │   - ConvNeXt Head           │
    │   - Inference Logic         │
    └─────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│             FUTURE SETUP (with civic Backend)                   │
└─────────────────────────────────────────────────────────────────┘

    Browser (http://localhost:5173 or https://app.example.com)
            │
            │ HTTP Requests (SAME FORMAT & API)
            │ NO CODE CHANGES IN FRONTEND
            ▼
    ┌───────────────────────┐
    │   React Frontend      │
    │   (unchanged)         │
    └─────────┬─────────────┘
              │
              │ VITE_API_BASE = https://civic-api.example.com
              │ (just change environment variable!)
              │
              ▼
    ┌──────────────────────────┐
    │   civic Backend          │
    │   (to be implemented)    │
    │   - /predict             │
    │   - /predict-batch       │
    │   - /health              │
    │   - /metadata            │
    └──────────────────────────┘
```

---

## Next Steps

1. **For ML Engineers (you now):**
   - ✓ Created ML wrapper module
   - ✓ Created FastAPI server
   - Set up local testing
   - Prepare demo data

2. **For Backend Engineers (civic team):**
   - Implement endpoints matching API contract
   - Test with frontend
   - Deploy to production

3. **For DevOps:**
   - Containerize inference server (Docker)
   - Set up monitoring
   - Configure auto-scaling

---

## Support

- **API Issues:** Check http://localhost:8000/docs (FastAPI Swagger UI)
- **Questions:** Refer to API_CONTRACT.md for detailed specifications
- **Debugging:** Run `python test_api.py` for comprehensive diagnostics
