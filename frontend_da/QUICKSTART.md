# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Verify Installation
```bash
cd segvision-ui
npm install
```

### Step 2: Start Frontend
```bash
npm run dev
# Opens at http://localhost:5173
```

### Step 3: Build Backend (Choose One)

**FastAPI (Recommended)**
```bash
pip install fastapi uvicorn python-multipart pillow opencv-python
# Copy BACKEND_TEMPLATE.py as your starting point
# Replace the placeholder functions with your model
python -m uvicorn main:app --reload --port 5000
```

**Flask**
```bash
pip install flask werkzeug pillow opencv-python
# Implement endpoints from BACKEND_API_SPEC.md
python app.py  # Port 5000
```

### Step 4: Test Connection
```bash
# Try uploading an image - should see error → imageId placeholder
# This means backend route isn't implemented yet
```

---

## 📌 What's Already Built (Just Need Backend)

### ✅ Complete Frontend
- 7 core components + 3 existing = DONE
- All styling = DONE
- API integration layer = DONE
- Configuration = DONE

### ❌ What YOU Need to Build
- Backend API (8 endpoints)
- Segmentation model integration
- Mask/overlay generation
- Metrics computation
- Demo sample preparation

---

## 📖 Read These (In Order)

1. **DELIVERY_SUMMARY.md** (5 min read) - Overview of what was built
2. **BACKEND_API_SPEC.md** (10 min read) - Exactly what backend needs to do
3. **BACKEND_TEMPLATE.py** (15 min read) - Starting point for implementation
4. **DEVELOPMENT_GUIDE.md** (20 min read) - Full architecture & deployment

---

## 🔗 API Endpoints Your Backend Must Implement

```
POST   /api/upload              → Get imageId
POST   /api/batch-upload        → Get imageIds array
POST   /api/infer               → Get predictions + mask/overlay URLs
POST   /api/infer-batch         → Get results array
GET    /api/metrics             → Get validation metrics (cached)
GET    /api/ablation            → Get ablation study results (cached)
GET    /api/demo-samples        → Get preloaded samples
POST   /api/export-csv          → Return CSV file
```

Each endpoint spec is detailed in `BACKEND_API_SPEC.md`

---

## 🧠 Implementation Path

### Phase 1: Basic Setup (2 hours)
1. Create backend project with FastAPI
2. Implement upload endpoints
3. Test file upload works

### Phase 2: Model Integration (4-8 hours)
1. Load your segmentation model
2. Implement inference endpoint
3. Generate mask & overlay PNGs
4. Test single inference works

### Phase 3: Metrics & Demo (2-4 hours)
1. Pre-compute validation metrics for both models
2. Prepare ablation study results
3. Gather unseen demo samples
4. Implement metrics & demo endpoints

### Phase 4: Polish (1-2 hours)
1. Optimize performance
2. Add error handling
3. Test full workflow
4. Deploy!

---

## 🎯 Production Checklist Before Pitch

- [ ] Backend deployed to cloud (AWS/GCP/Azure)
- [ ] Frontend deployed to CDN (Vercel/Netlify)
- [ ] Demo samples pre-cached (instant loading)
- [ ] Metrics pre-computed (no startup delay)
- [ ] Model weights optimized (< 20ms inference)
- [ ] CSS/JS minified (< 1s page load)
- [ ] CORS configured properly
- [ ] Error messages user-friendly
- [ ] CSV export tested
- [ ] Batch processing tested (50+ images)
- [ ] Model toggle tested
- [ ] Network latency tested

---

## 💬 Common Questions

**Q: Can I customize the colors?**  
A: Yes! Edit `src/config/segmentationConfig.js` → `classConfig` object

**Q: Can I add more than 10 classes?**  
A: Yes! Add to `classConfig` and update risk weights in the same file

**Q: How do I add authentication?**  
A: Add JWT middleware to backend, store token in localStorage frontend

**Q: How do I deploy to production?**  
A: See DEVELOPMENT_GUIDE.md → Deployment Checklist section

---

## 📞 Files You'll Reference Most

1. **BACKEND_API_SPEC.md** - API reference (bookmark this!)
2. **BACKEND_TEMPLATE.py** - Copy this to start backend
3. **segmentationConfig.js** - Class definitions & colors
4. **segmentationAPI.js** - How frontend talks to backend
5. **Demo.jsx** - Main component orchestrator

---

## ⚡ Performance Targets

Keep these in mind while building:

**Frontend**
- Page load: < 2 seconds
- Single inference UI update: < 500ms (excluding network)
- Batch table render (100 rows): < 1 second

**Backend**
- Single inference: 10-20ms (GPU) / 50-100ms (CPU)
- Batch inference (10 images): < 200ms
- Metrics endpoint: < 50ms (cached)

---

## 🎬 Demo Everything Works

```javascript
// Once your backend is running, test frontend:

// 1. Upload image
// 2. See imageId in console
// 3. Click Infer
// 4. See results

// 5. Load Demo Sample
// 6. Run inference
// 7. Toggle model
// 8. See different results

// 9. Upload batch of 5 images
// 10. Process batch
// 11. Export CSV

// 12. View Validation tab
// 13. See metrics comparison
// 14. View ablation study
```

---

## ✨ Pro Pitch Tips

1. **Start with demo samples** - "Let me show you unseen data"
2. **Highlight risk score** - "Now autonomous systems can decide terrain safety"
3. **Show model comparison** - "Here's baseline, now improved model"
4. **Run batch** - "Processes 50+ images reliably"
5. **Export results** - "All data is exportable for your team"

---

**Questions?** See the 4 documentation files or search within them.

**Time to Deploy:** 8-14 hours of backend work  
**Expected Result:** Production-grade autonomous vision demo  
**Wow Factor:** 🚀🚀🚀
