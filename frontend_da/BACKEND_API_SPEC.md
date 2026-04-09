# SegVision Backend API Routes

Complete API specification for the SegVision segmentation demo frontend.

## Base URL
```
http://localhost:5000/api
```

## Environment Configuration
Add to `.env` or pass via `VITE_API_BASE`:
```
VITE_API_BASE=http://localhost:5000/api
```

---

## Upload Endpoints

### 1. Upload Single Image
**POST** `/upload`

Upload a single image file for processing.

**Request:**
```
Content-Type: multipart/form-data

- file (required): Image file (PNG, JPG, JPEG, GIF)
```

**Response:**
```json
{
  "imageId": "uuid-string",
  "filename": "image.jpg",
  "path": "/uploads/uuid-string.jpg",
  "size": 524288,
  "uploadedAt": "2024-04-09T12:00:00Z"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid file type
- 413: File too large

---

### 2. Batch Upload (Folder/Multiple Files)
**POST** `/batch-upload`

Upload multiple image files at once.

**Request:**
```
Content-Type: multipart/form-data

- files (required): Multiple image files
```

**Response:**
```json
{
  "imageIds": ["uuid-1", "uuid-2", "uuid-3"],
  "count": 3,
  "paths": ["/uploads/uuid-1.jpg", "/uploads/uuid-2.jpg", "/uploads/uuid-3.jpg"],
  "uploadedAt": "2024-04-09T12:00:00Z"
}
```

---

## Inference Endpoints

### 3. Run Single Inference
**POST** `/infer`

Run segmentation inference on an uploaded image.

**Request:**
```json
{
  "imageId": "uuid-string",
  "modelVersion": "improved" // or "baseline"
}
```

**Response:**
```json
{
  "imageId": "uuid-string",
  "maskUrl": "/results/uuid-string-mask.png",
  "overlayUrl": "/results/uuid-string-overlay.png",
  "inferenceTime": 12.5,
  "modelVersion": "improved",
  "predictions": {
    "pixelCoverages": {
      "0": 152500,  // drivable_ground
      "1": 42300,   // rock
      "2": 28450,   // log
      "3": 19200,   // clutter
      "4": 98700,   // grass
      "5": 185960,  // sky
      "6": 0,       // water
      "7": 35670,   // vegetation
      "8": 5120,    // stairs
      "9": 12900    // obstacle
    },
    "totalPixels": 580900,
    "topClass": "sky",
    "topClassConfidence": 0.32,
    "allClassConfidences": {
      "0": 0.263,
      "1": 0.073,
      "2": 0.049,
      "3": 0.033,
      "4": 0.170,
      "5": 0.320,
      "6": 0.0,
      "7": 0.061,
      "8": 0.0088,
      "9": 0.022
    }
  }
}
```

---

### 4. Batch Inference
**POST** `/infer-batch`

Run inference on multiple uploaded images.

**Request:**
```json
{
  "imageIds": ["uuid-1", "uuid-2", "uuid-3"],
  "modelVersion": "improved" // or "baseline"
}
```

**Response:**
```json
{
  "results": [
    {
      "imageId": "uuid-1",
      "filename": "image1.jpg",
      "maskUrl": "/results/uuid-1-mask.png",
      "overlayUrl": "/results/uuid-1-overlay.png",
      "inferenceTime": 12.5,
      "modelVersion": "improved",
      "status": "completed",
      "predictions": {
        "pixelCoverages": { ... },
        "totalPixels": 580900,
        "topClass": "sky",
        "topClassConfidence": 0.32
      },
      "riskLevel": "Caution"
    },
    {
      "imageId": "uuid-2",
      "filename": "image2.jpg",
      "status": "completed",
      ...
    }
  ],
  "totalCount": 3,
  "completedCount": 3,
  "failedCount": 0,
  "avgInferenceTime": 12.8
}
```

---

## Metrics Endpoints

### 5. Get Validation Metrics
**GET** `/metrics`

Retrieve comprehensive validation metrics comparing baseline and improved models.

**Query Parameters:**
```
- scene_type (optional): "outdoor", "indoor", "mixed"
- lighting_condition (optional): "daylight", "shadow", "night"
```

**Response:**
```json
{
  "baseline": {
    "meanIoU": 0.687,
    "pixelAccuracy": 0.812,
    "dice": 0.756,
    "latency": 25.2,
    "perClassIoU": {
      "drivable_ground": 0.856,
      "rock": 0.623,
      "log": 0.541,
      "clutter": 0.438,
      "grass": 0.754,
      "sky": 0.934,
      "water": 0.0,
      "vegetation": 0.621,
      "stairs": 0.289,
      "obstacle": 0.512
    }
  },
  "improved": {
    "meanIoU": 0.738,
    "pixelAccuracy": 0.854,
    "dice": 0.803,
    "latency": 12.8,
    "perClassIoU": {
      "drivable_ground": 0.891,
      "rock": 0.687,
      "log": 0.612,
      "clutter": 0.521,
      "grass": 0.803,
      "sky": 0.951,
      "water": 0.0,
      "vegetation": 0.698,
      "stairs": 0.421,
      "obstacle": 0.624
    }
  },
  "comparison": {
    "meanIoUImprovement": 0.051,
    "pixelAccuracyImprovement": 0.042,
    "diceImprovement": 0.047,
    "latencyReduction": 12.4
  }
}
```

---

### 6. Get Ablation Study Results
**GET** `/ablation`

Retrieve ablation study results comparing augmented vs non-augmented training.

**Response:**
```json
{
  "withoutAugmentation": {
    "meanIoU": 0.712,
    "pixelAccuracy": 0.831,
    "diceScore": 0.778,
    "inferenceTime": 12.8,
    "perClassIoU": {
      "drivable_ground": 0.867,
      "rock": 0.645,
      ...
    }
  },
  "withAugmentation": {
    "meanIoU": 0.738,
    "pixelAccuracy": 0.854,
    "diceScore": 0.803,
    "inferenceTime": 12.8,
    "perClassIoU": {
      "drivable_ground": 0.891,
      "rock": 0.687,
      ...
    }
  },
  "improvement": {
    "meanIoU": {
      "value": 0.026,
      "percentage": 3.65
    },
    "pixelAccuracy": {
      "value": 0.023,
      "percentage": 2.77
    }
  },
  "qualitativeExamples": {
    "goodCases": [
      {
        "imageId": "uuid-1",
        "description": "Clear ground with good sky segmentation",
        "url": "/examples/good/uuid-1.jpg"
      }
    ],
    "failureCases": [
      {
        "imageId": "uuid-fail-1",
        "description": "Water reflection misclassified as sky",
        "url": "/examples/failure/uuid-fail-1.jpg",
        "issue": "Water reflection"
      }
    ]
  }
}
```

---

### 7. Get Demo Samples (Unseen Test Set)
**GET** `/demo-samples`

Retrieve preloaded demo samples for the live pitch demo - samples the model has never seen during training.

**Query Parameters:**
```
- limit (optional, default=10): Maximum number of samples to return
- scene_type (optional): Filter by scene type
```

**Response:**
```json
{
  "samples": [
    {
      "imageId": "demo-uuid-1",
      "imageUrl": "/demo-samples/demo-uuid-1.jpg",
      "filename": "unseen_sample_1.jpg",
      "sceneType": "outdoor_rocky",
      "lightingCondition": "daylight",
      "description": "Rocky terrain with mixed vegetation"
    },
    {
      "imageId": "demo-uuid-2",
      "imageUrl": "/demo-samples/demo-uuid-2.jpg", 
      "filename": "unseen_sample_2.jpg",
      "sceneType": "outdoor_grassy",
      "lightingCondition": "shadow",
      "description": "Grassy field with shadows"
    }
  ],
  "count": 10,
  "metadata": {
    "totalAvailable": 47,
    "sceneTypes": ["outdoor_rocky", "outdoor_grassy", "indoor_structured", "mixed"],
    "lightingConditions": ["daylight", "shadow", "night"]
  }
}
```

---

## Export Endpoints

### 8. Export Batch Results as CSV
**POST** `/export-csv`

Export batch processing results in CSV format.

**Request:**
```json
{
  "results": [
    {
      "imageId": "uuid-1",
      "filename": "image1.jpg",
      "inferenceTime": 12.5,
      "modelVersion": "improved",
      "topClass": "sky",
      "confidence": 0.32,
      "riskLevel": "Caution",
      "status": "completed"
    }
  ]
}
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename="segmentation-results-1712667600000.csv"

filename,inferenceTime,modelVersion,topClass,confidence,riskLevel,status
image1.jpg,12.5,improved,sky,0.32,Caution,completed
image2.jpg,11.8,improved,grass,0.29,Safe,completed
```

---

## Error Responses

All endpoints follow this error format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

**Common Error Codes:**
- `INVALID_FILE_TYPE`: File is not a supported image format
- `FILE_TOO_LARGE`: File exceeds size limit
- `IMAGE_NOT_FOUND`: Requested image ID doesn't exist
- `MODEL_NOT_FOUND`: Requested model version doesn't exist
- `INFERENCE_FAILED`: Error during inference
- `INVALID_REQUEST`: Missing or invalid request parameters
- `SERVER_ERROR`: Internal server error

---

## Implementation Notes

### Class Configuration (Required on Backend)
Should match the frontend `segmentationConfig.js`:

```python
CLASS_CONFIG = {
    0: "drivable_ground",
    1: "rock",
    2: "log",
    3: "clutter",
    4: "grass",
    5: "sky",
    6: "water",
    7: "vegetation",
    8: "stairs",
    9: "obstacle"
}
```

### Risk Score Calculation (Backend Must Compute)
```
risk_score = Σ (pixel_coverage[class] × risk_weight[class])
risk_weight = {
    drivable_ground: -1.0,
    grass: -0.5,
    sky: 0,
    vegetation: 0.3,
    stairs: 0.5,
    clutter: 0.6,
    log: 0.7,
    rock: 0.8,
    obstacle: 0.9,
    water: 1.0
}

if risk_score < 30: level = "Safe"
elif risk_score < 60: level = "Caution"
else: level = "High-Risk"
```

### Mask & Overlay Generation
1. **Mask**: Semantic segmentation output (one channel per class or RGB colorized)
2. **Overlay**: Blend original image with semi-transparent segmentation mask (alpha ~0.4-0.6)

### Performance Requirements
- Single inference: < 20ms target
- Batch processing should be queued if > 50 images
- CSV export: Streaming response for large batches

---

## Rate Limiting (Recommended)

- Single upload: 100 MB max per file
- Batch upload: 500 MB max per request
- Single inference: 1 req/sec per client
- Batch inference: 1 req/10 sec per client (can process up to 100 images per request)

---

## Frontend Configuration

Update `src/api/segmentationAPI.js`:

```javascript
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';
```

Add to `.env.local`:
```
VITE_API_BASE=http://localhost:5000/api
```

Or for production:
```
VITE_API_BASE=https://api.segvision.com/api
```
