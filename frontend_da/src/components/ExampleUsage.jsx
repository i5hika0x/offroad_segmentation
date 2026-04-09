/**
 * ExampleUsage.jsx - Frontend Integration Examples
 * 
 * Shows how to use the segmentationAPI functions in your React components.
 * 
 * Usage:
 * - Import functions from @/api/segmentationAPI
 * - Call them from your components
 * - Handle loading and error states
 * - Display results
 */

import { useState } from 'react';
import {
  predict,
  predictBatch,
  getMetadata,
  checkHealth,
  imageToDataURL,
  downloadBase64Image,
  formatCoverageForDisplay,
  formatAPIError,
  exportResultsAsCSV,
} from '@/api/segmentationAPI';

// ============================================================================
// EXAMPLE 1: Single Image Prediction
// ============================================================================

export function Example1SingleImagePrediction() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      // Show preview
      const imageUrl = await imageToDataURL(file);
      setImage(imageUrl);

      // Run prediction
      setLoading(true);
      setError(null);

      const predictionResult = await predict(file);
      setResult(predictionResult);
    } catch (err) {
      const formattedError = formatAPIError(err);
      setError(formattedError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="example-container">
      <h2>Example 1: Single Image Prediction</h2>

      {/* File Input */}
      <div>
        <label htmlFor="image-input">Select an image:</label>
        <input
          id="image-input"
          type="file"
          accept="image/*"
          onChange={handleImageSelect}
          disabled={loading}
        />
      </div>

      {/* Preview */}
      {image && (
        <div>
          <h3>Preview</h3>
          <img src={image} alt="preview" style={{ maxWidth: '300px' }} />
        </div>
      )}

      {/* Loading */}
      {loading && <p>Processing image...</p>}

      {/* Error */}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {/* Results */}
      {result && (
        <div>
          <h3>Results</h3>

          {/* Mask */}
          <div>
            <h4>Segmentation Mask</h4>
            <img src={result.mask} alt="mask" style={{ maxWidth: '300px' }} />
            <button onClick={() => downloadBase64Image(result.mask, 'mask.png')}>
              📥 Download Mask
            </button>
          </div>

          {/* Overlay */}
          <div>
            <h4>Overlay</h4>
            <img src={result.overlay} alt="overlay" style={{ maxWidth: '300px' }} />
            <button onClick={() => downloadBase64Image(result.overlay, 'overlay.png')}>
              📥 Download Overlay
            </button>
          </div>

          {/* Class Distribution */}
          <div>
            <h4>Class Distribution</h4>
            <table>
              <thead>
                <tr>
                  <th>Class</th>
                  <th>Coverage (%)</th>
                </tr>
              </thead>
              <tbody>
                {formatCoverageForDisplay(result.class_distribution).map(([className, percentage]) => (
                  <tr key={className}>
                    <td>{className}</td>
                    <td>{percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Image Info */}
          <div>
            <h4>Image Info</h4>
            <p>
              Dimensions: {result.image_width}x{result.image_height}
            </p>
            <p>Classes detected: {result.num_classes}</p>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// EXAMPLE 2: Batch Prediction
// ============================================================================

export function Example2BatchPrediction() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFilesSelect = (e) => {
    const selectedFiles = Array.from(e.target.files || []);
    setFiles(selectedFiles);
  };

  const handleBatchPredict = async () => {
    if (files.length === 0) {
      setError('Please select at least one image');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const batchResults = await predictBatch(files);
      setResults(batchResults);
    } catch (err) {
      const formattedError = formatAPIError(err);
      setError(formattedError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="example-container">
      <h2>Example 2: Batch Prediction</h2>

      {/* File Input */}
      <div>
        <label htmlFor="batch-input">Select multiple images:</label>
        <input
          id="batch-input"
          type="file"
          accept="image/*"
          multiple
          onChange={handleFilesSelect}
          disabled={loading}
        />
        <button onClick={handleBatchPredict} disabled={loading || files.length === 0}>
          {loading ? 'Processing...' : `Predict (${files.length} files)`}
        </button>
      </div>

      {/* Error */}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {/* Results */}
      {results && (
        <div>
          <h3>Batch Results</h3>
          <p>
            Processed {results.successful} / {results.total_images} images in{' '}
            {(results.processing_time_ms / 1000).toFixed(2)}s
          </p>

          {results.failed > 0 && (
            <p style={{ color: 'orange' }}>
              ⚠️ {results.failed} image(s) failed to process
            </p>
          )}

          {/* Results Table */}
          <table>
            <thead>
              <tr>
                <th>Filename</th>
                <th>Status</th>
                <th>Top Class</th>
                <th>Coverage</th>
              </tr>
            </thead>
            <tbody>
              {results.results.map((result, idx) => (
                <tr key={idx}>
                  <td>{result.filename}</td>
                  <td>{result.success ? '✓' : '✗'}</td>
                  <td>
                    {result.success && result.coverage?.[0]
                      ? result.coverage[0][0]
                      : result.error || 'N/A'}
                  </td>
                  <td>
                    {result.success && result.coverage?.[0]
                      ? `${result.coverage[0][1].toFixed(1)}%`
                      : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Export Button */}
          <button onClick={() => exportResultsAsCSV(results.results)}>
            📊 Export as CSV
          </button>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// EXAMPLE 3: Health Check & Metadata
// ============================================================================

export function Example3HealthAndMetadata() {
  const [health, setHealth] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCheckHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await checkHealth();
      setHealth(data);
    } catch (err) {
      const formattedError = formatAPIError(err);
      setError(formattedError.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGetMetadata = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getMetadata();
      setMetadata(data);
    } catch (err) {
      const formattedError = formatAPIError(err);
      setError(formattedError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="example-container">
      <h2>Example 3: Health Check & Metadata</h2>

      <button onClick={handleCheckHealth} disabled={loading}>
        🔍 Check Health
      </button>
      <button onClick={handleGetMetadata} disabled={loading}>
        📋 Get Metadata
      </button>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {health && (
        <div>
          <h3>Health Status</h3>
          <pre>{JSON.stringify(health, null, 2)}</pre>
        </div>
      )}

      {metadata && (
        <div>
          <h3>Model Metadata</h3>
          <p>
            <strong>Type:</strong> {metadata.model_type}
          </p>
          <p>
            <strong>Classes:</strong> {metadata.num_classes}
          </p>
          <p>
            <strong>Device:</strong> {metadata.device}
          </p>
          <div>
            <strong>Supported Classes:</strong>
            <ul>
              {metadata.class_names.map((className) => (
                <li key={className}>{className}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// EXAMPLE 4: Error Handling
// ============================================================================

export function Example4ErrorHandling() {
  const [lastError, setLastError] = useState(null);

  const handleTest = async () => {
    try {
      // Test 1: API not running
      const response = await fetch('http://localhost:9999/health');
    } catch (error) {
      const formatted = formatAPIError(error);
      setLastError({
        title: 'Connection Error',
        ...formatted,
      });
    }
  };

  const handleInvalidImage = async () => {
    try {
      // Create an invalid "image"
      const blob = new Blob(['not an image'], { type: 'text/plain' });
      const file = new File([blob], 'invalid.txt');

      await predict(file);
    } catch (error) {
      const formatted = formatAPIError(error);
      setLastError({
        title: 'Prediction Error',
        ...formatted,
      });
    }
  };

  return (
    <div className="example-container">
      <h2>Example 4: Error Handling</h2>

      <button onClick={handleTest}>Test Connection Error</button>
      <button onClick={handleInvalidImage}>Test Invalid Image</button>

      {lastError && (
        <div style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '5px' }}>
          <h3>{lastError.title}</h3>
          <p>
            <strong>Status:</strong> {lastError.status || 'No server response'}
          </p>
          <p>
            <strong>Message:</strong> {lastError.message}
          </p>
          {lastError.data && (
            <details>
              <summary>Details</summary>
              <pre>{JSON.stringify(lastError.data, null, 2)}</pre>
            </details>
          )}
        </div>
      )}

      <div style={{ backgroundColor: '#fffacd', padding: '10px', borderRadius: '5px', marginTop: '10px' }}>
        <h4>Error Handling Best Practices:</h4>
        <ul>
          <li>Always check if API is running: `curl http://localhost:8000/health`</li>
          <li>Use `formatAPIError()` for user-friendly error messages</li>
          <li>Display specific errors to help users troubleshoot</li>
          <li>Provide fallback UI when API is unavailable</li>
          <li>Log errors to console for debugging</li>
        </ul>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN EXPORT: All Examples
// ============================================================================

export function AllExamples() {
  const [activeExample, setActiveExample] = useState(1);

  return (
    <div className="examples-container">
      <h1>API Integration Examples</h1>

      <div className="example-tabs">
        {[1, 2, 3, 4].map((num) => (
          <button
            key={num}
            onClick={() => setActiveExample(num)}
            className={activeExample === num ? 'active' : ''}
          >
            Example {num}
          </button>
        ))}
      </div>

      <div className="example-content">
        {activeExample === 1 && <Example1SingleImagePrediction />}
        {activeExample === 2 && <Example2BatchPrediction />}
        {activeExample === 3 && <Example3HealthAndMetadata />}
        {activeExample === 4 && <Example4ErrorHandling />}
      </div>

      <div
        style={{
          marginTop: '20px',
          padding: '10px',
          backgroundColor: '#e8f4f8',
          borderRadius: '5px',
        }}
      >
        <h3>💡 Tips</h3>
        <ul>
          <li>
            <strong>Before running examples:</strong> Make sure the API server is running
            (http://localhost:8000)
          </li>
          <li>
            <strong>Check browser console (F12):</strong> Look for network requests and error
            messages
          </li>
          <li>
            <strong>API Documentation:</strong> Visit http://localhost:8000/docs for interactive
            API explorer
          </li>
          <li>
            <strong>For production:</strong> Replace `http://localhost:8000` with actual civic
            backend URL
          </li>
        </ul>
      </div>
    </div>
  );
}

// ============================================================================
// EXPORT: Individual Components
// ============================================================================

export default {
  Example1SingleImagePrediction,
  Example2BatchPrediction,
  Example3HealthAndMetadata,
  Example4ErrorHandling,
  AllExamples,
};
