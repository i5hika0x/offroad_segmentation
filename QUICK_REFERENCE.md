# Quick Reference - ML Integration

## 📋 Files Created/Updated

| File | Purpose | Type |
|------|---------|------|
| `duality_aii/predict.py` | ML wrapper module | Core |
| `duality_aii/inference_server.py` | FastAPI server | Core |
| `duality_aii/example_backend_usage.py` | Backend examples | Documentation |
| `frontend_da/src/api/segmentationAPI.js` | API client | Core |
| `frontend_da/src/components/ExampleUsage.jsx` | Frontend examples | Documentation |
| `API_CONTRACT.md` | API specification | Documentation |
| `INTEGRATION_GUIDE.md` | Setup instructions | Documentation |
| `IMPLEMENTATION_SUMMARY.md` | Overview | Documentation |
| `duality_aii/.env.example` | Backend config | Configuration |
| `frontend_da/.env.example` | Frontend config | Configuration |

---

## 🚀 Quick Start (5 minutes)

### Terminal 1: Backend
```bash
cd duality_aii
python -m uvicorn inference_server:app --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend_da
npm install  # First time only
npm run dev
```

### Terminal 3: Test
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

Then visit: http://localhost:5173

---

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/metadata` | Model info |
| POST | `/predict` | Single image |
| POST | `/predict-batch` | Multiple images |

---

## 📦 Dependencies

### Backend
```
fastapi
uvicorn
torch
torchvision
opencv-python
pillow
numpy
```

### Frontend
```
axios      (already in package.json)
react      (already in package.json)
```

---

## 🔓 For Civic Backend Integration

**Only 1 line needs to change:**

```javascript
// .env.local (Frontend)

// Current (local):
VITE_API_BASE=http://localhost:8000

// Future (civic):
VITE_API_BASE=https://civic-api.example.com/api/v1
```

**That's it!** Frontend code stays the same.

---

## 📝 Response Format

All `/predict` endpoints return:

```json
{
  "success": true,
  "mask": "iVBORw0KGgoAAAA...",           // base64 PNG
  "overlay": "iVBORw0KGgoAAAA...",         // base64 PNG
  "class_distribution": {
    "Trees": 25.5,
    "Sky": 0.5,
    ...
  },
  "coverage": [["Trees", 25.5], ...],
  "num_classes": 10,
  "image_width": 1920,
  "image_height": 1080
}
```

---

## 🐛 Debugging

### API Not Running?
```bash
curl http://localhost:8000/health
# If fails: API is not running
```

### Frontend Can't Reach API?
```bash
# Check .env.local
cat frontend_da/.env.local | grep VITE_API_BASE

# Should be: VITE_API_BASE=http://localhost:8000
```

### Model Not Found?
```bash
# Check path in .env.local
cat duality_aii/.env.local | grep MODEL_CHECKPOINT

# Should point to segmentation_head.pth location
```

---

## 📚 Documentation

- **API Details:** See `API_CONTRACT.md`
- **Setup Help:** See `INTEGRATION_GUIDE.md`
- **Overview:** See `IMPLEMENTATION_SUMMARY.md`
- **Code Examples:** See `example_backend_usage.py` and `ExampleUsage.jsx`

---

## 💡 Common Tasks

### Test Single Image
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@image.jpg"
```

### Test from Python
```python
import requests

with open('image.jpg', 'rb') as f:
    response = requests.post('http://localhost:8000/predict', files={'file': f})
    print(response.json())
```

### Test from Frontend
```javascript
import { predict } from '@/api/segmentationAPI';

const result = await predict(imageFile);
console.log(result);
```

### Run Civic Backend (Future)
```bash
# In civic backend repo:
VITE_API_BASE=https://civic-api.example.com npm run dev
```

---

## ✅ Checklist

- [ ] Backend runs: `python -m uvicorn inference_server:app --port 8000`
- [ ] Frontend runs: `npm run dev` (port 5173)
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] Can upload image in UI
- [ ] Can see segmentation results
- [ ] Can download mask/overlay
- [ ] Batch upload works
- [ ] CSV export works
- [ ] Error handling works

---

## 🎯 When Civic Backend Is Ready

1. **Civic team:** Implement endpoints following `API_CONTRACT.md`
2. **You:** Update `VITE_API_BASE` in `.env.local`
3. **Test:** Same UI should work with new backend
4. **Deploy:** No frontend code changes needed

---

## 📞 Need Help?

1. Check the relevant documentation file
2. Run example code files
3. Check browser console for errors
4. Check API health: `curl http://localhost:8000/health`
5. Review error in `API_CONTRACT.md` error handling section

---

**Everything is production-ready. You're all set!** ✨
