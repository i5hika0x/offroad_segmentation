# API Contract - Offroad Segmentation

## Overview

This document defines the **API contract** for the Offroad Semantic Segmentation service. This contract will be used by:
- The local FastAPI server (current implementation)
- The future civic backend (to be integrated by another developer)
- The React frontend (client application)

The contract is **standardized** and **independent** of the underlying implementation.

---

## Base Configuration

```
Protocol:     HTTP/HTTPS
Default Host: http://localhost:8000
Default Port: 8000 (local) / 5000+ (civic backend)
Timeout:      60 seconds
```

### Environment Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `VITE_API_BASE` | Frontend API base URL | `http://localhost:8000` | `http://localhost:8000` |
| `VITE_API_TIMEOUT` | API request timeout (ms) | `60000` | `120000` |
| `MODEL_CHECKPOINT` | ML model path (backend) | `./segmentation_head.pth` | `/models/segmentation_head.pth` |
| `DEVICE` | PyTorch device (backend) | Auto (cuda/cpu) | `cuda` |

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify API server is running and model is loaded.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cuda",
  "num_classes": 10,
  "class_names": [
    "Trees",
    "Lush Bushes",
    "Dry Grass",
    "Dry Bushes",
    "Ground Clutter",
    "Flowers",
    "Logs",
    "Rocks",
    "Landscape",
    "Sky"
  ]
}
```

---

### 2. Model Metadata

**Endpoint:** `GET /metadata`

**Purpose:** Get model specifications and capabilities.

**Request:**
```bash
curl http://localhost:8000/metadata
```

**Response (200 OK):**
```json
{
  "api_version": "1.0.0",
  "model_type": "DINOv2 + ConvNeXt Segmentation Head",
  "num_classes": 10,
  "class_names": [
    "Trees",
    "Lush Bushes",
    "Dry Grass",
    "Dry Bushes",
    "Ground Clutter",
    "Flowers",
    "Logs",
    "Rocks",
    "Landscape",
    "Sky"
  ],
  "device": "cuda",
  "checkpoint_path": "./segmentation_head.pth",
  "input_height": 504,
  "input_width": 504,
  "supported_formats": ["PNG", "JPG", "JPEG", "BMP"],
  "api_endpoints": {
    "/health": "GET - Health check",
    "/metadata": "GET - Model metadata",
    "/predict": "POST - Single image prediction",
    "/predict-batch": "POST - Batch prediction"
  }
}
```

---

### 3. Single Image Prediction

**Endpoint:** `POST /predict`

**Purpose:** Run semantic segmentation on a single image.

**Request Headers:**
```
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <binary image data>
```

**Supported Image Formats:** PNG, JPG, JPEG, BMP  
**Max File Size:** No hard limit (recommend < 50MB)

**cURL Example:**
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@image.jpg"
```

**Python Example:**
```python
import requests

with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/predict', files=files)
    result = response.json()
    print(result)
```

**JavaScript/Fetch Example:**
```javascript
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  body: formData,
});

const result = await response.json();
```

**Response (200 OK):**
```json
{
  "success": true,
  "mask": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "overlay": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "class_distribution": {
    "Trees": 25.5,
    "Lush Bushes": 15.2,
    "Dry Grass": 20.8,
    "Dry Bushes": 12.3,
    "Ground Clutter": 8.5,
    "Flowers": 3.2,
    "Logs": 2.1,
    "Rocks": 7.8,
    "Landscape": 4.1,
    "Sky": 0.5
  },
  "coverage": [
    ["Trees", 25.5],
    ["Dry Grass", 20.8],
    ["Lush Bushes", 15.2],
    ["Dry Bushes", 12.3],
    ["Rocks", 7.8],
    ["Ground Clutter", 8.5],
    ["Landscape", 4.1],
    ["Flowers", 3.2],
    ["Logs", 2.1],
    ["Sky", 0.5]
  ],
  "num_classes": 10,
  "image_width": 1920,
  "image_height": 1080
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid image format or unable to read file"
}
```

**Response (503 Service Unavailable):**
```json
{
  "detail": "Model not loaded"
}
```

### Field Descriptions:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether prediction succeeded |
| `mask` | string | Base64-encoded PNG segmentation mask |
| `overlay` | string | Base64-encoded PNG overlay (mask + original) |
| `class_distribution` | object | `{class_name: percentage}` for each class |
| `coverage` | array | `[[class_name, percentage], ...]` sorted by percentage |
| `num_classes` | int | Total number of segmentation classes |
| `image_width` | int | Width of input image (pixels) |
| `image_height` | int | Height of input image (pixels) |
| `error` | string | Error message (only if `success=false`) |

### Image Format:

- `mask` and `overlay` are **base64-encoded PNG images**
- To display in HTML: `<img src="data:image/png;base64,${mask}" />`
- To decode in JavaScript:
  ```javascript
  const binaryString = atob(base64String);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  const blob = new Blob([bytes], { type: 'image/png' });
  ```

---

### 4. Batch Prediction

**Endpoint:** `POST /predict-batch`

**Purpose:** Run predictions on multiple images efficiently.

**Request Headers:**
```
Content-Type: multipart/form-data
```

**Request Body:**
```
files: <multiple binary image files>
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/predict-batch \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.jpg"
```

**Python Example:**
```python
import requests

files = [
    ('files', open('image1.jpg', 'rb')),
    ('files', open('image2.jpg', 'rb')),
    ('files', open('image3.jpg', 'rb')),
]

response = requests.post('http://localhost:8000/predict-batch', files=files)
result = response.json()
```

**JavaScript Example:**
```javascript
const formData = new FormData();
imageFiles.forEach((file) => {
  formData.append('files', file);
});

const response = await fetch('http://localhost:8000/predict-batch', {
  method: 'POST',
  body: formData,
});

const result = await response.json();
```

**Response (200 OK):**
```json
{
  "success": true,
  "results": [
    {
      "filename": "image1.jpg",
      "success": true,
      "mask": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
      "overlay": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
      "class_distribution": {
        "Trees": 25.5,
        "Lush Bushes": 15.2
      },
      "coverage": [
        ["Trees", 25.5],
        ["Lush Bushes", 15.2]
      ],
      "image_width": 1920,
      "image_height": 1080
    },
    {
      "filename": "image2.jpg",
      "success": true,
      "mask": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
      "overlay": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
      "class_distribution": {},
      "coverage": [],
      "image_width": 1920,
      "image_height": 1080
    },
    {
      "filename": "image3.jpg",
      "success": false,
      "error": "Unsupported image format"
    }
  ],
  "total_images": 3,
  "successful": 2,
  "failed": 1,
  "processing_time_ms": 2345.67
}
```

### Field Descriptions:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether ALL predictions succeeded |
| `results` | array | Array of prediction results (one per file) |
| `total_images` | int | Total number of files sent |
| `successful` | int | Number of successful predictions |
| `failed` | int | Number of failed predictions |
| `processing_time_ms` | float | Total processing time in milliseconds |

---

## Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

### Common HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| `200` | Success | Prediction completed successfully |
| `400` | Bad Request | Invalid file format, corrupted image |
| `422` | Validation Error | Missing required field |
| `500` | Server Error | Unexpected backend error |
| `503` | Service Unavailable | Model not loaded, out of memory |

### Frontend Error Handling Example

```javascript
try {
  const response = await fetch('/predict', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    console.error(`API Error (${response.status}):`, error.detail);
    // Handle error in UI
  }

  const result = await response.json();
  if (!result.success) {
    console.error('Prediction failed:', result.error);
  } else {
    // Display results
  }
} catch (error) {
  console.error('Network error:', error.message);
}
```

---

## Data Types

### Class Distribution

Object mapping class names to percentages (0-100):

```javascript
{
  "Trees": 25.5,
  "Lush Bushes": 15.2,
  "Dry Grass": 20.8,
  // ...
}
```

### Coverage Array

2D array of `[class_name, percentage]`, sorted by percentage descending:

```javascript
[
  ["Trees", 25.5],
  ["Dry Grass", 20.8],
  ["Lush Bushes", 15.2],
  // ...
]
```

### Base64 Images

PNG images encoded as base64 strings. Use in HTML:

```html
<img src="data:image/png;base64,{base64_string}" alt="Prediction Result" />
```

---

## Integration Notes for Future Backend (civic)

When the civic backend is integrated, replace the API URL and ensure the following:

1. **Endpoint paths can change**, but the data contract should remain compatible
2. **Response format should match** (base64 images, class_distribution, coverage)
3. **Error handling** must return appropriate HTTP status codes
4. **CORS headers** must allow requests from the frontend origin

### Frontend Configuration for civic Backend

Update the `.env` file in `frontend_da/`:

```bash
# For local ML API (current)
VITE_API_BASE=http://localhost:8000

# For civic backend (future)
VITE_API_BASE=https://civic-backend.example.com/api/v1
```

---

## Performance Expectations

### Latency

| Operation | Expected Time |
|-----------|----------------|
| Single image prediction | 1-3 seconds (GPU) / 5-15 seconds (CPU) |
| Batch of 10 images | 8-30 seconds (GPU) / 50-150 seconds (CPU) |
| Health check | < 100ms |
| Metadata fetch | < 100ms |

### Resource Usage

- **GPU (CUDA):** ~2GB VRAM
- **CPU:** ~1GB RAM
- **Disk:** ~500MB for model files

---

## Example Workflows

### Frontend to Local API (Current)

```
┌─────────────┐
│   Frontend  │
│ React/Vite  │
└──────┬──────┘
       │
       │ POST /predict
       │ (multipart/form-data)
       │
       ▼
┌──────────────────────┐
│  Local FastAPI      │
│  (inference_server) │
│  http://localhost:8000
└──────┬───────────────┘
       │
       │ Load model (once)
       │ Load image
       │ Run inference
       │ Return base64 images
       │
       ▼
┌──────────────────────┐
│   ML Model          │
│  (DINOv2 +          │
│   ConvNeXt Head)    │
└─────────────────────┘
```

### Frontend to Future civic Backend

```
┌─────────────┐
│   Frontend  │
│ React/Vite  │
└──────┬──────┘
       │
       │ POST /predict
       │ (same contract!)
       │
       ▼
┌──────────────────────┐
│  civic Backend       │
│  (Future)            │
│ https://civic-api... │
└──────┬───────────────┘
       │
       │ May use different ML
       │ infrastructure
       │ (same response format)
       │
       ▼
┌──────────────────────┐
│   ML Infrastructure │
│  (May vary)          │
└─────────────────────┘
```

**Key Point:** Frontend code doesn't change! Only the `VITE_API_BASE` environment variable changes.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial API contract |

---

## Questions?

- **API Issues:** Check `/health` endpoint first
- **Model Issues:** Check logs in inference server
- **Frontend Issues:** Check browser console and network tab
