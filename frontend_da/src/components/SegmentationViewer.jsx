import { useState } from 'react';
import './SegmentationViewer.css';

export default function SegmentationViewer({
  originalImage,
  maskImage,
  overlayImage,
  inferenceTime,
  modelVersion,
}) {
  const [activeView, setActiveView] = useState('original'); // 'original', 'mask', 'overlay'

  if (!originalImage) {
    return (
      <div className="viewer-placeholder">
        <p>Upload an image to view segmentation results</p>
      </div>
    );
  }

  return (
    <div className="segmentation-viewer">
      <div className="viewer-header">
        <h3>Segmentation Analysis</h3>
        <div className="viewer-info">
          <span className="model-tag">{modelVersion} Model</span>
          <span className="inference-time">⚡ {inferenceTime}ms</span>
        </div>
      </div>

      <div className="viewer-tabs">
        <button
          className={`tab-btn ${activeView === 'original' ? 'active' : ''}`}
          onClick={() => setActiveView('original')}
        >
          Original
        </button>
        <button
          className={`tab-btn ${activeView === 'mask' ? 'active' : ''}`}
          onClick={() => setActiveView('mask')}
        >
          Predicted Mask
        </button>
        <button
          className={`tab-btn ${activeView === 'overlay' ? 'active' : ''}`}
          onClick={() => setActiveView('overlay')}
        >
          Overlay
        </button>
      </div>

      <div className="viewer-container">
        <div className="image-wrapper">
          {activeView === 'original' && (
            <img
              src={originalImage}
              alt="Original"
              className="segmentation-image"
            />
          )}
          {activeView === 'mask' && maskImage && (
            <img src={maskImage} alt="Predicted Mask" className="segmentation-image" />
          )}
          {activeView === 'overlay' && overlayImage && (
            <img src={overlayImage} alt="Overlay" className="segmentation-image" />
          )}
        </div>

        {/* Side-by-side comparison view */}
        <div className="comparison-view">
          <div className="comparison-item">
            <img src={originalImage} alt="Original" />
            <label>Original</label>
          </div>
          {maskImage && (
            <div className="comparison-item">
              <img src={maskImage} alt="Mask" />
              <label>Predicted</label>
            </div>
          )}
          {overlayImage && (
            <div className="comparison-item">
              <img src={overlayImage} alt="Overlay" />
              <label>Overlay</label>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
