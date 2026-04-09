# SegVision - Complete Development Guide

## Project Overview

SegVision is an advanced semantic segmentation demo platform designed for:
1. **Real-time demonstration** of baseline vs improved segmentation models
2. **Autonomous traversability assessment** with risk scoring
3. **Comprehensive evaluation** with metrics, ablation studies, and qualitative examples
4. **Production-ready architecture** suitable for pitches and client presentations

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  SegVision Frontend (React)                 │
│                   segvision-ui/ (This Project)              │
├─────────────────────────────────────────────────────────────┤
│  Components:                                                 │
│  • UploadPanel → Image/folder upload with drag-drop         │
│  • SegmentationViewer → Side-by-side image comparison       │
│  • ClassLegend → Fixed-color class palette + coverage %     │
│  • RiskScore → Traversability assessment (Safe/Caution/HR)  │
│  • BatchResultsTable → Multi-image results + CSV export     │
│  • ValidationResults → Metrics & ablation study comparison  │
│  • Demo.jsx → Main orchestrator integrating all components  │
└─────────────────────────────────────────────────────────────┘
                           ↕↕↕
            REST API Communication via Axios
                           ↕↕↕
┌─────────────────────────────────────────────────────────────┐
│               SegVision Backend (Your Implementation)        │
│                    (FastAPI / Flask / Django)               │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                  │
│  • POST /upload - Single image upload                       │
│  • POST /batch-upload - Folder/multiple upload              │
│  • POST /infer - Run segmentation on image                  │
│  • POST /infer-batch - Batch processing                     │
│  • GET /metrics - Validation metrics (baseline vs improved) │
│  • GET /ablation - Ablation study results                   │
│  • GET /demo-samples - Preloaded unseen test samples        │
│  • POST /export-csv - Batch results CSV export              │
└─────────────────────────────────────────────────────────────┘
                           ↕↕↕
                   Your ML Model(s)
                           ↕↕↕
┌─────────────────────────────────────────────────────────────┐
│           Segmentation Models (Your Training Code)          │
│  • Baseline Model (Initial version)                         │
│  • Improved Model (With augmentation/optimizations)         │
│  • Validation Dataset (Metrics computation)                 │
│  • Demo Samples (Unseen test set for live demo)             │
└─────────────────────────────────────────────────────────────┘
```

---

## Frontend Setup & Development

### Initial Setup (Already Done)

```bash
# The frontend has been scaffolded with all components:
npm install                    # Install dependencies
cp .env.example .env.local    # Copy environment template
npm run dev                    # Start development server (http://localhost:5173)
```

### Frontend File Structure

```
src/
├── api/
│   └── segmentationAPI.js          # All backend API calls
├── config/
│   └── segmentationConfig.js       # Class definitions + risk score logic
├── components/
│   ├── UploadPanel.jsx/.css        # File upload UI
│   ├── SegmentationViewer.jsx/.css # Image comparison display
│   ├── ClassLegend.jsx/.css        # Class palette + percentages
│   ├── RiskScore.jsx/.css          # Traversability gauge
│   ├── BatchResultsTable.jsx/.css  # Results table + CSV export
│   ├── ValidationResults.jsx/.css  # Metrics & ablation tabs
│   ├── Demo.jsx/.css               # Main demo (integrates all above)
│   ├── Hero.jsx/.css
│   ├── Navbar.jsx/.css
│   └── Architecture.jsx/.css
├── App.jsx                         # Root component
├── main.jsx                        # Vite entry point
└── index.css                       # Global styles
```

### Key Components Explained

#### 1. **Demo.jsx** (Main Orchestrator)
```jsx
// Manages three views:
- Single Image Mode: Upload → Infer → Display results
- Batch Mode: Upload folder → Batch infer → Results table
- Validation Mode: Show metrics & ablation study

// Features:
- Model toggle (baseline/improved)
- Auto-switch model results
- Load demo samples
- Batch CSV export
```

#### 2. **SegmentationConfig.js**
```javascript
// Class definitions with:
- Fixed RGB colors (consistent across sessions)
- Risk weights for traversability scoring
- Class helper functions

// Risk calculation:
Safe: score < 30       (high ground, low obstacles)
Caution: 30-60         (mixed terrain)
High-Risk: > 60        (water, obstacles, etc)
```

#### 3. **SegmentationAPI.js**
```javascript
// Wrapper for all backend calls:
- uploadImage()
- uploadFolder()
- runInference()
- runBatchInference()
- fetchValidationMetrics()
- fetchAblationResults()
- fetchDemoSamples()
- exportBatchResultsCSV()

// Configuration:
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
```

---

## Backend Implementation Guide

### Step 1: Choose Your Framework

**Recommended: FastAPI** (Modern, async, auto-docs)

```bash
pip install fastapi uvicorn python-multipart pillow opencv-python
```

**Alternative: Flask** (Simple, lightweight)
```bash
pip install flask werkzeug pillow opencv-python
```

### Step 2: Implement API Routes

Use `BACKEND_TEMPLATE.py` as a starting point. Key things to implement:

1. **Upload Endpoints**
   - Validate file type (image only)
   - Check file size
   - Generate unique ID
   - Save to disk/storage

2. **Inference Endpoints**
   - Load model (baseline or improved)
   - Preprocess image
   - Run segmentation
   - Post-process predictions
   - Generate mask & overlay PNG
   - Return predictions dict

3. **Metrics Endpoints**
   - Pre-compute on startup or cache
   - Return structured metrics for both models
   - Include per-class IoU breakdown

4. **Demo Samples Endpoint**
   - Load unseen validation images
   - Serve URLs to previously-inferred results

### Step 3: Model Integration

**Key Requirements:**

```python
# Your inference function must return:
predictions = {
    "pixelCoverages": {
        0: 152500,  # pixel count for each class
        1: 42300,
        2: 28450,
        # ... 10 classes total
    },
    "totalPixels": 580900,
    "topClass": "sky",  # Most frequent class name
    "topClassConfidence": 0.32,  # Coverage of top class
    "allClassConfidences": {  # Coverage per class (0-1)
        0: 0.263,
        1: 0.073,
        # ...
    }
}

# Must also generate:
# - mask.png: Color-coded segmentation mask
# - overlay.png: Original image with semi-transparent seg overlay
```

### Step 4: Metrics Computation (Pre-computed)

```python
# Calculate offline on validation set, serve static data:

validation_results = {
    "baseline": {
        "meanIoU": 0.687,      # Mean Intersection-over-Union
        "pixelAccuracy": 0.812, # % of pixels classified correctly
        "dice": 0.756,          # Dice coefficient
        "latency": 25.2,        # Inference time in ms
        "perClassIoU": {        # IoU for each class
            "drivable_ground": 0.856,
            "rock": 0.623,
            # ...
        }
    },
    "improved": {
        # Same structure, improved results
    },
    "comparison": {
        "meanIoUImprovement": 0.051,
        # ... improvement metrics
    }
}
```

### Step 5: Demo Samples Preparation

```python
# Prepare before deployment:
1. Reserve validation subset (10+ samples)
2. Ensure model has never trained on these
3. Pre-run inference (cache results)
4. Store image + ground truth + predictions

# Serve from /demo-samples endpoint:
GET /demo-samples?limit=10
→ Returns 10 random unseen samples with metadata
```

---

## Deployment Checklist

### Frontend Deployment

```bash
# 1. Build
npm run build

# 2. Deploy dist/ folder to:
# - Vercel (push to GitHub)
# - Netlify (drag-drop dist/)
# - AWS S3 + CloudFront
# - Docker

# 3. Set environment variable:
VITE_API_BASE=https://your-api-domain.com/api
```

### Backend Deployment

```bash
# 1. Directory structure
backend/
├── requirements.txt      # python dependencies
├── main.py              # FastAPI app
├── models/              # Model files
├── uploads/             # Temp uploads
├── results/             # Generated masks/overlays
└── demo_samples/        # Precomputed demo results

# 2. Docker
docker build -t segvision-api .
docker run -p 5000:5000 segvision-api

# 3. Production considerations:
- Use Gunicorn/uWSGI for FastAPI
- Add Redis for caching
- Set up job queue (Celery) for batch processing
- Enable CORS properly (restrict origins)
- Add rate limiting
- Use GPU acceleration (CUDA, TensorRT)
- Monitor performance (Prometheus, Grafana)
```

---

## Feature Walkthrough

### 1. Single Image Analysis

```
User Flow:
1. Drag image to UploadPanel
2. Image parsed → UploadPanel.onImageUpload()
3. API: POST /upload → Get imageId
4. API: POST /infer → Get predictions (12-20ms)
5. Display:
   - SegmentationViewer: original/mask/overlay tabs
   - ClassLegend: all 10 classes with % coverage
   - RiskScore: Safe/Caution/High-Risk gauge
```

**Example Result:**
```
IMAGE: highway_scene.jpg
Classes: Sky (32%), Grass (17%), Drivable Ground (26%), etc
Risk: SAFE (32.1%)
Inference: 12.5ms on Improved Model
```

### 2. Batch Processing

```
User Flow:
1. Select mode Toggle → "Batch Processing"
2. Drag folder or select multiple images
3. API: POST /batch-upload → Get imageIds
4. API: POST /infer-batch → Run on all
5. BatchResultsTable shows:
   - Filename | Inference Time | Model | Top Class | Confidence | Risk | Status
   - Avg stats: Total images, Avg time, Success rate
6. Export button → POST /export-csv → Download results.csv
```

### 3. Validation Results

```
User Flow:
1. Select mode Toggle → "Validation Results"
2. API: GET /metrics → Load comparison
3. ValidationResults shows two tabs:

TAB 1: Metrics Comparison
- Baseline Model: Mean IoU 68.7%, Latency 25.2ms
- Improved Model: Mean IoU 73.8%, Latency 12.8ms
- Improvement: +5.1% IoU, 1.96x faster
- Per-class IoU: Breakdown for all 10 classes

TAB 2: Ablation Study
- Without Augmentation: Mean IoU 71.2%
- With Augmentation: Mean IoU 73.8%
- Improvement: +2.6% IoU (+3.65% relative gain)
- Qualitative examples: Good cases + failure cases
```

### 4. Risk Scoring Algorithm

```javascript
// Implemented in segmentationConfig.js

weights = {
    drivable_ground: -1.0,  // Best → reduces risk
    grass: -0.5,
    sky: 0,
    vegetation: 0.3,
    stairs: 0.5,
    clutter: 0.6,
    log: 0.7,
    rock: 0.8,
    obstacle: 0.9,
    water: 1.0              // Worst → max risk
}

score = Σ(pixelCoverage[class] × weight[class]) / total
      = Σ(0.26×(-1) + 0.17×(-0.5) + 0.32×0 + ...) / 1.0
      = -0.095 → normalized to 32.1% → "SAFE"
```

---

## Optimization Guide

### Frontend Optimization

```javascript
// 1. Code splitting (already configured in Vite)
import { lazy } from 'react';
const BatchResults = lazy(() => import('./BatchResultsTable'));

// 2. Memoization for expensive components
const ClassLegend = memo(ClassLegend);

// 3. Image lazy loading
<img loading="lazy" src={url} alt="preview" />

// 4. Debounce model toggle
const handleModelToggle = useCallback(debounce((...) => {...}, 300), [])
```

### Backend Optimization

```python
# 1. Model caching
baseline_model = load_model("models/baseline.pth")  # On startup
improved_model = load_model("models/improved.pth")

# 2. Async processing for batch
@app.post("/api/infer-batch")
async def batch_infer(request: BatchInferenceRequest):
    tasks = [infer_async(id) for id in request.imageIds]
    results = await asyncio.gather(*tasks)
    return results

# 3. GPU acceleration (CUDA)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# 4. Caching inference results
cache = Redis()
cache.setex(f"infer:{image_id}:{model}", 3600, results_json)
```

---

## Troubleshooting

### Common Issues & Solutions

**1. CORS Error when calling backend**
```
Error: Access to XMLHttpRequest blocked by CORS policy

Solution (Backend):
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**2. Images not uploading despite "200 OK"**
```
Check:
- File size < 100MB
- Content-Type is image/*
- Disk has free space
- Upload directory permissions

Debug:
console.log(uploadedData) in browser
print(file_path) in backend
```

**3. Inference timeout on slow models**
```
Solutions:
- Increase client timeout:
  axios.defaults.timeout = 60000;  // 60 seconds

- Queue batch jobs:
  Use Celery/RabbitMQ for long-running tasks
  
- Optimize model:
  Use model compression, quantization, TensorRT
```

**4. CSV export contains wrong data**
```
Check:
- Results array structure matches expected format
- Filename field populated
- Test with simple CSV first

Debug:
console.log(results) before export
```

---

## Testing Checklist

### Frontend Testing
```
□ Single image upload (drag & click)
□ Batch upload (multiple files)
□ Model toggle (baseline ↔ improved)
□ View tabs (original → mask → overlay)
□ Class legend renders all 10 classes
□ Risk score updates based on predictions
□ CSV export downloads correctly
□ Demo samples load
□ Validation metrics display
```

### Backend Testing
```
□ /upload returns valid imageId
□ /infer requires imageId + modelVersion
□ /infer-batch processes all images
□ /metrics returns expected structure
□ /ablation returns improvement data
□ /demo-samples returns >= 1 sample
□ /export-csv generates valid CSV
□ Error responses have correct format
□ Large batch (50+ images) completes
```

### Integration Testing
```
□ Upload → Infer → Display flow works
□ Model switch re-runs inference correctly
□ CSV export contains accurate data
□ Validation metrics match offlinedata
□ Demo samples never trigger training data
```

---

## Performance Targets

### Frontend
- Page load: < 2 seconds
- Single inference UI update: < 500ms (excluding backend latency)
- Batch results table render (100 rows): < 1 second
- CSV export download (1000 rows): < 2 seconds

### Backend
- Single inference: 10-20ms (GPU), 50-100ms (CPU)
- Batch inference (10 images): < 200ms end-to-end
- Metrics endpoint: < 50ms (cached)
- File upload: Streaming, no memory limit
- CSV generation: < 5 seconds for 1000 rows

---

## Next Steps

1. **Backend Implementation**
   - Start with `BACKEND_TEMPLATE.py`
   - Integrate your segmentation model
   - Compute and cache metrics
   - Prepare demo samples
   - Deploy to server

2. **Frontend Customization**
   - Add authentication if needed
   - Integrate with your CDN
   - Customize colors/branding
   - Add analytics
   - Deploy to hosting

3. **Production Hardening**
   - Add monitoring & logging
   - Set up error tracking (Sentry)
   - Configure automated backups
   - Implement rate limiting
   - Add security headers

4. **Pitch Optimization**
   - Pre-load demo samples
   - Use compression for faster loading
   - Test network latency
   - Prepare offline demo fallback

---

## Support & Resources

- **Frontend Docs**: See `FRONTEND_README.md`
- **API Spec**: See `BACKEND_API_SPEC.md`
- **React Docs**: https://react.dev
- **Vite Docs**: https://vitejs.dev
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Pytorch**: https://pytorch.org

---

**SegVision v1.0** - Built for production-grade segmentation demos.
