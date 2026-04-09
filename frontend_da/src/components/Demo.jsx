import { useState, useEffect } from 'react';
import UploadPanel from './UploadPanel';
import SegmentationViewer from './SegmentationViewer';
import ClassLegend from './ClassLegend';
import RiskScore from './RiskScore';
import BatchResultsTable from './BatchResultsTable';
import ValidationResults from './ValidationResults';
import {
  runInference,
  runBatchInference,
  fetchValidationMetrics,
  fetchAblationResults,
  fetchDemoSamples,
} from '../api/segmentationAPI';
import './Demo.css';

export default function Demo() {
  // UI State
  const [uploadMode, setUploadMode] = useState('single'); // 'single' or 'batch'
  const [currentView, setCurrentView] = useState('single'); // 'single', 'batch', or 'validation'
  const [modelVersion, setModelVersion] = useState('improved'); // 'baseline' or 'improved'
  const [isLoading, setIsLoading] = useState(false);
  const [useDemo, setUseDemo] = useState(false);

  // Single Image State
  const [currentImage, setCurrentImage] = useState(null);
  const [currentImageData, setCurrentImageData] = useState(null);
  const [inferenceResult, setInferenceResult] = useState(null);

  // Batch State
  const [batchImages, setBatchImages] = useState([]);
  const [batchResults, setBatchResults] = useState([]);

  // Validation State
  const [validationMetrics, setValidationMetrics] = useState(null);
  const [ablationMetrics, setAblationMetrics] = useState(null);

  // Load validation and ablation data on mount
  useEffect(() => {
    const loadValidationData = async () => {
      try {
        const [metrics, ablation] = await Promise.all([
          fetchValidationMetrics(),
          fetchAblationResults(),
        ]);
        setValidationMetrics(metrics);
        setAblationMetrics(ablation);
      } catch (err) {
        console.error('Failed to load validation data:', err);
      }
    };

    loadValidationData();
  }, []);

  // Load demo samples
  const loadDemoSamples = async () => {
    try {
      setIsLoading(true);
      const samples = await fetchDemoSamples();
      if (samples.samples && samples.samples.length > 0) {
        setCurrentImage(samples.samples[0].imageUrl);
        setCurrentImageData(samples.samples[0]);
        const result = await runInference(samples.samples[0].imageId, modelVersion);
        setInferenceResult(result);
      }
    } catch (err) {
      console.error('Failed to load demo samples:', err);
      alert('Failed to load demo samples');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle single image upload
  const handleImageUpload = async (uploadData) => {
    setCurrentImage(uploadData.preview);
    setCurrentImageData(uploadData);
    setCurrentView('single');
    setUploadMode('single');

    try {
      setIsLoading(true);
      const result = await runInference(uploadData.imageId, modelVersion);
      setInferenceResult(result);
    } catch (err) {
      console.error('Inference failed:', err);
      alert('Inference failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle batch upload
  const handleBatchUpload = async (uploadData) => {
    setBatchImages(uploadData);
    setCurrentView('batch');
    setUploadMode('batch');

    try {
      setIsLoading(true);
      const results = await runBatchInference(uploadData.imageIds, modelVersion);
      setBatchResults(results.results || []);
    } catch (err) {
      console.error('Batch processing failed:', err);
      alert('Batch processing failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle model toggle
  const handleModelToggle = async (newModel) => {
    setModelVersion(newModel);

    if (currentImageData && currentView === 'single') {
      try {
        setIsLoading(true);
        const result = await runInference(currentImageData.imageId, newModel);
        setInferenceResult(result);
      } catch (err) {
        console.error('Model switch inference failed:', err);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <section id="demo" className="demo-section">
      <div className="demo-container">
        <h2 className="section-title">Interactive Segmentation Demo</h2>

        {/* Mode Toggle */}
        <div className="mode-tabs">
          <button
            className={`mode-tab ${currentView === 'single' ? 'active' : ''}`}
            onClick={() => setCurrentView('single')}
          >
            Single Image
          </button>
          <button
            className={`mode-tab ${currentView === 'batch' ? 'active' : ''}`}
            onClick={() => setCurrentView('batch')}
          >
            Batch Processing
          </button>
          <button
            className={`mode-tab ${currentView === 'validation' ? 'active' : ''}`}
            onClick={() => setCurrentView('validation')}
          >
            Validation Results
          </button>
        </div>

        {/* Model Toggle */}
        <div className="model-selector">
          <label>Model Version:</label>
          <div className="model-buttons">
            <button
              className={`model-btn ${modelVersion === 'baseline' ? 'active' : ''}`}
              onClick={() => handleModelToggle('baseline')}
              disabled={isLoading}
            >
              Baseline
            </button>
            <button
              className={`model-btn ${modelVersion === 'improved' ? 'active' : ''}`}
              onClick={() => handleModelToggle('improved')}
              disabled={isLoading}
            >
              Improved
            </button>
          </div>
        </div>

        {/* Single Image View */}
        {currentView === 'single' && (
          <div className="single-image-view">
            <UploadPanel
              onImageUpload={handleImageUpload}
              isLoading={isLoading}
            />

            <div className="demo-actions">
              <button
                className="demo-btn"
                onClick={loadDemoSamples}
                disabled={isLoading}
              >
                📸 Load Demo Sample
              </button>
            </div>

            {currentImage && (
              <>
                <SegmentationViewer
                  originalImage={currentImage}
                  maskImage={inferenceResult?.maskUrl}
                  overlayImage={inferenceResult?.overlayUrl}
                  inferenceTime={inferenceResult?.inferenceTime}
                  modelVersion={modelVersion}
                />

                <div className="results-grid">
                  <div className="results-column">
                    <ClassLegend
                      pixelCoverages={inferenceResult?.predictions?.pixelCoverages}
                      totalPixels={inferenceResult?.predictions?.totalPixels}
                    />
                  </div>
                  <div className="results-column">
                    <RiskScore
                      pixelCoverages={inferenceResult?.predictions?.pixelCoverages}
                    />
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* Batch Processing View */}
        {currentView === 'batch' && (
          <div className="batch-view">
            <UploadPanel
              onBatchUpload={handleBatchUpload}
              isLoading={isLoading}
            />

            <BatchResultsTable results={batchResults} isLoading={isLoading} />
          </div>
        )}

        {/* Validation Results View */}
        {currentView === 'validation' && (
          <div className="validation-view">
            <ValidationResults
              overallMetrics={validationMetrics}
              ablationMetrics={ablationMetrics}
              isLoading={isLoading}
            />
          </div>
        )}
      </div>
    </section>
  );
}