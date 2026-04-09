import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

// Upload utilities
export async function uploadImage(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post(`${API_BASE}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  return response.data; // { imageId, path, filename }
}

export async function uploadFolder(files) {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await axios.post(`${API_BASE}/batch-upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

  return response.data; // { imageIds, count, paths }
}

// Inference
export async function runInference(imageId, modelVersion = 'improved') {
  const response = await axios.post(`${API_BASE}/infer`, {
    imageId,
    modelVersion,
  });

  return response.data; // { maskUrl, overlayUrl, predictions, inferenceTime, modelVersion }
}

export async function runBatchInference(imageIds, modelVersion = 'improved') {
  const response = await axios.post(`${API_BASE}/infer-batch`, {
    imageIds,
    modelVersion,
  });

  return response.data; // { results: [...], avgInferenceTime }
}

// Metrics
export async function fetchValidationMetrics() {
  const response = await axios.get(`${API_BASE}/metrics`);
  return response.data; // { baseline: {...}, improved: {...}, comparison: {...} }
}

export async function fetchAblationResults() {
  const response = await axios.get(`${API_BASE}/ablation`);
  return response.data; // { withAugmentation: {...}, withoutAugmentation: {...} }
}

export async function fetchDemoSamples() {
  const response = await axios.get(`${API_BASE}/demo-samples`);
  return response.data; // { samples: [...] }
}

// Export
export async function exportBatchResultsCSV(results) {
  const response = await axios.post(`${API_BASE}/export-csv`, { results }, {
    responseType: 'blob',
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `segmentation-results-${Date.now()}.csv`);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
}

// Helper to read local image file as data URL for preview
export function readImageAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
