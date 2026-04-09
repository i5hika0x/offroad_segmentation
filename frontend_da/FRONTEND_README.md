# SegVision UI - Interactive Segmentation Demo Frontend

Professional-grade frontend for semantic segmentation model demonstration with comprehensive feature set for evaluating and pitching autonomous traversability assessment.

## Features

### 🎯 Core Features
- **Single & Batch Upload**: Drag-and-drop interface for single images or entire folders
- **Side-by-Side Visualization**: Original, predicted mask, and overlay comparison views
- **Model Toggle**: Seamlessly switch between baseline and improved models in real-time
- **Live Demo Mode**: Preloaded unseen samples for pitch stability

### 📊 Analysis & Metrics
- **Class Legend**: Fixed-color palette for all 10+ segmentation classes
- **Per-Class Coverage**: Pixel count and percentage for each class
- **Inference Metrics**: Real-time inference time and model version display
- **Batch Results Table**: Multi-image processing with downloadable CSV export
- **Validation Metrics**: Baseline vs improved model comparison
  - Mean IoU, Pixel Accuracy, Dice Score
  - Per-class IoU breakdown
  - Inference latency comparison
- **Ablation Study**: With/Without data augmentation impact analysis
- **Qualitative Examples**: Good cases and failure cases showcase

### 🚗 Autonomous Navigation Features
- **Traversability Score**: Safe | Caution | High-Risk assessment
- **Risk Calculation**: Intelligent class weighting based on terrain difficulty
  - Safe (score < 30): High ground confidence, minimal obstacles
  - Caution (score 30-60): Mixed terrain with moderate hazards
  - High-Risk (score > 60): Water, obstacles, or poor ground confidence
- **Visual Indicators**: Color-coded risk levels and gauges

## Project Structure

```
segvision-ui/
├── src/
│   ├── api/
│   │   └── segmentationAPI.js      # Backend API integration
│   ├── config/
│   │   └── segmentationConfig.js   # Class definitions & risk scores
│   ├── components/
│   │   ├── UploadPanel.jsx         # File upload UI
│   │   ├── SegmentationViewer.jsx  # Image display & comparison
│   │   ├── ClassLegend.jsx         # Class palette & coverage
│   │   ├── RiskScore.jsx           # Traversability gauge
│   │   ├── BatchResultsTable.jsx   # Batch processing results
│   │   ├── ValidationResults.jsx   # Metrics & ablation results
│   │   ├── Demo.jsx                # Main demo orchestrator
│   │   ├── Hero.jsx
│   │   ├── Navbar.jsx
│   │   ├── Architecture.jsx
│   │   └── *.css                   # Component styles
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── public/
├── package.json
├── vite.config.js
├── BACKEND_API_SPEC.md             # Comprehensive API documentation
├── .env.example                    # Environment template
└── README.md
```

## Installation & Setup

### Prerequisites
- Node.js 16+ and npm/yarn
- Backend API running on `http://localhost:5000/api` (or configured endpoint)

### Quick Start

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your backend URL if needed
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

5. **Preview production build**
   ```bash
   npm run preview
   ```

## Component Guide

### UploadPanel
Handles single image and batch folder uploads with drag-and-drop support.

```jsx
<UploadPanel
  onImageUpload={(data) => handleSingleImage(data)}
  onBatchUpload={(data) => handleBatchImages(data)}
  isLoading={false}
/>
```

### SegmentationViewer
Displays original, mask, and overlay with tabbed view switching.

```jsx
<SegmentationViewer
  originalImage={imageUrl}
  maskImage={maskUrl}
  overlayImage={overlayUrl}
  inferenceTime={12.5}
  modelVersion="improved"
/>
```

### ClassLegend
Shows all classes with fixed colors, pixel counts, and coverage percentages.

```jsx
<ClassLegend
  pixelCoverages={predictions.pixelCoverages}
  totalPixels={predictions.totalPixels}
/>
```

### RiskScore
Displays traversability assessment with visual gauge and description.

```jsx
<RiskScore
  pixelCoverages={predictions.pixelCoverages}
/>
```

### BatchResultsTable
Multi-image results with CSV export capability.

```jsx
<BatchResultsTable
  results={batchResults}
  isLoading={false}
/>
```

### ValidationResults
Comprehensive metrics comparison and ablation study visualization.

```jsx
<ValidationResults
  overallMetrics={validationMetrics}
  ablationMetrics={ablationMetrics}
  isLoading={false}
/>
```

## API Integration

All backend communication is handled through `src/api/segmentationAPI.js`:

```javascript
import {
  uploadImage,
  uploadFolder,
  runInference,
  runBatchInference,
  fetchValidationMetrics,
  fetchAblationResults,
  fetchDemoSamples,
  exportBatchResultsCSV
} from '@/api/segmentationAPI';

// Upload and infer
const uploaded = await uploadImage(file);
const result = await runInference(uploaded.imageId, 'improved');

// Batch processing
const batchResults = await runBatchInference(imageIds, 'baseline');

// Export results
await exportBatchResultsCSV(batchResults);
```

See `BACKEND_API_SPEC.md` for complete API documentation.

## Styling

All components use modern CSS with consistent design system:

- **Color Scheme**: Dark theme with green accent (#4CAF50)
- **Fonts**: System fonts with fallbacks for performance
- **Responsive**: Mobile-first design with responsive grid layouts
- **Accessibility**: WCAG 2.1 AA compliant contrast ratios

### CSS Variables (from `index.css`)
```css
--primary-color: #4CAF50;
--bg-primary: #1a1a2e;
--bg-secondary: #16213e;
--text-primary: rgba(255, 255, 255, 0.9);
--text-muted: rgba(255, 255, 255, 0.6);
```

## Class Configuration

10 segmentation classes with fixed colors:

```javascript
{
  0: "drivable_ground" (#4CAF50),
  1: "rock" (#795548),
  2: "log" (#8D6E63),
  3: "clutter" (#A1887F),
  4: "grass" (#81C784),
  5: "sky" (#64B5F6),
  6: "water" (#00BCD4),
  7: "vegetation" (#66BB6A),
  8: "stairs" (#FF9800),
  9: "obstacle" (#E53935)
}
```

## Risk Score Algorithm

The traversability score is computed based on terrain composition:

```
risk_weight = {
  drivable_ground: -1.0,     // Reduces risk significantly
  grass: -0.5,               // Slightly reduces risk
  sky: 0,                    // Neutral
  vegetation: +0.3,          // Minor hazard
  stairs: +0.5,              // Moderate hazard
  clutter: +0.6,             // High hazard
  log: +0.7,                 // High hazard
  rock: +0.8,                // Very high hazard
  obstacle: +0.9,            // Critical hazard
  water: +1.0                // Maximum hazard
}

score = Σ(coverage[class] × risk_weight[class]) / total_coverage × 100
```

## Performance Optimization

- **Code Splitting**: Route-based lazy loading via React Router
- **Image Optimization**: Lazy loading for comparison images
- **Memoization**: React.memo for expensive components
- **CSS-in-JS**: Minimal runtime overhead with CSS modules
- **Build**: Vite for fast dev server and optimized production build

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Available Scripts
```bash
npm run dev       # Start dev server
npm run build     # Production build
npm run lint      # ESLint check
npm run preview   # Preview production build
```

### Code Quality
- ESLint configured for React best practices
- Prettier integration for code formatting
- No TypeScript required (but compatible)

## Deployment

### Static Hosting (Vercel, Netlify, GitHub Pages)
```bash
npm run build
# Serve `dist` folder
```

### Docker
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

### Environment Variables for Production
```
VITE_API_BASE=https://api.segvision.com/api
```

## Troubleshooting

### Issue: API connection fails
- Ensure backend is running on configured `VITE_API_BASE`
- Check CORS headers in backend configuration
- Verify network connectivity

### Issue: Images not uploading
- Check file size limits (100MB for single, 500MB for batch)
- Verify file format (PNG, JPG, JPEG, GIF)
- Check browser console for detailed error

### Issue: Inference slow
- Check backend inference queue
- Verify model is loaded in memory on backend
- For batch, process in smaller chunks

## Future Enhancements

- Real-time segmentation (webcam input)
- 3D terrain visualization
- Active learning for hard cases
- Multi-model ensemble comparison
- Custom class definition UI
- Inference optimization profiles

## License

Proprietary - SegVision

## Support

For issues, feature requests, or backend integration questions, contact the development team.
