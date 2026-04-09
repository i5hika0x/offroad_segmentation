/**
 * Segmentation API Client
 * 
 * Handles communication with the ML inference API.
 * Can work with local FastAPI server or future civic backend.
 * 
 * Environment Variables:
 * - VITE_API_BASE: Base URL for API (default: http://localhost:8000)
 * - VITE_API_TIMEOUT: Request timeout in ms (default: 60000)
 */

import axios from 'axios';

// ============================================================================
// CONFIG
// ============================================================================

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT ? parseInt(import.meta.env.VITE_API_TIMEOUT) : 60000;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: API_TIMEOUT,
});

// ============================================================================
// METADATA & HEALTH CHECKS
// ============================================================================

/**
 * Check if API server is healthy and ready
 */
export async function checkHealth() {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    throw new Error(`API health check failed: ${error.message}`);
  }
}

/**
 * Get model metadata and supported classes
 */
export async function getMetadata() {
  try {
    const response = await apiClient.get('/metadata');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch metadata: ${error.message}`);
  }
}

// ============================================================================
// PREDICTION ENDPOINTS
// ============================================================================

/**
 * Run inference on a single image
 * 
 * @param {File} imageFile - Image file to predict on
 * @returns {Promise<Object>} Prediction result with mask and overlay (base64)
 * 
 * Response format:
 * {
 *   success: boolean,
 *   mask: "data:image/png;base64,...",
 *   overlay: "data:image/png;base64,...",
 *   class_distribution: { class_name: percentage, ... },
 *   coverage: [ [class_name, percentage], ... ],
 *   num_classes: number,
 *   image_width: number,
 *   image_height: number,
 *   error?: string (if success=false)
 * }
 */
export async function predict(imageFile) {
  if (!imageFile) {
    throw new Error('Image file is required');
  }

  const formData = new FormData();
  formData.append('file', imageFile);

  try {
    const response = await apiClient.post('/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    if (!response.data.success) {
      throw new Error(response.data.error || 'Prediction failed');
    }

    // Convert base64 to data URLs for display
    return {
      ...response.data,
      mask: `data:image/png;base64,${response.data.mask}`,
      overlay: `data:image/png;base64,${response.data.overlay}`,
    };
  } catch (error) {
    throw new Error(`Prediction failed: ${error.message}`);
  }
}

/**
 * Run batch inference on multiple images
 * 
 * @param {File[]} imageFiles - Array of image files
 * @returns {Promise<Object>} Batch results
 * 
 * Response format:
 * {
 *   success: boolean,
 *   results: [
 *     {
 *       filename: string,
 *       success: boolean,
 *       mask: "data:image/png;base64,...",
 *       overlay: "data:image/png;base64,...",
 *       class_distribution: { ... },
 *       coverage: [ ... ],
 *       image_width: number,
 *       image_height: number,
 *       error?: string
 *     },
 *     ...
 *   ],
 *   total_images: number,
 *   successful: number,
 *   failed: number,
 *   processing_time_ms: number
 * }
 */
export async function predictBatch(imageFiles) {
  if (!imageFiles || imageFiles.length === 0) {
    throw new Error('At least one image file is required');
  }

  const formData = new FormData();
  imageFiles.forEach((file) => {
    formData.append('files', file);
  });

  try {
    const response = await apiClient.post('/predict-batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    // Convert base64 to data URLs for all results
    const results = response.data.results.map((result) => {
      if (result.success) {
        return {
          ...result,
          mask: `data:image/png;base64,${result.mask}`,
          overlay: `data:image/png;base64,${result.overlay}`,
        };
      }
      return result;
    });

    return {
      ...response.data,
      results,
    };
  } catch (error) {
    throw new Error(`Batch prediction failed: ${error.message}`);
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Convert image File to base64 string for preview/display
 * 
 * @param {File} file - Image file
 * @returns {Promise<string>} Data URL (data:image/...)
 */
export function imageToDataURL(file) {
  return new Promise((resolve, reject) => {
    if (!file) {
      reject(new Error('File is required'));
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = (err) => reject(new Error(`Failed to read file: ${err}`));
    reader.readAsDataURL(file);
  });
}

/**
 * Convert base64 image to blob for download
 * 
 * @param {string} base64String - Base64 encoded image
 * @param {string} filename - Filename for download
 */
export async function downloadBase64Image(base64String, filename) {
  // Remove data URL prefix if present
  const base64Data = base64String.includes(',') 
    ? base64String.split(',')[1] 
    : base64String;

  const byteCharacters = atob(base64Data);
  const byteArray = new Uint8Array(byteCharacters.length);
  
  for (let i = 0; i < byteCharacters.length; i++) {
    byteArray[i] = byteCharacters.charCodeAt(i);
  }

  const blob = new Blob([byteArray], { type: 'image/png' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * Format class coverage for display
 * 
 * @param {Object} classDistribution - {class_name: percentage, ...}
 * @returns {Array} Sorted array of [class_name, percentage]
 */
export function formatCoverageForDisplay(classDistribution) {
  return Object.entries(classDistribution)
    .map(([className, percentage]) => [className, percentage.toFixed(2)])
    .sort((a, b) => b[1] - a[1]); // Sort by percentage descending
}

/**
 * Get API configuration for debugging/display
 */
export function getAPIConfig() {
  return {
    baseURL: API_BASE,
    timeout: API_TIMEOUT,
    endpoints: {
      health: '/health',
      metadata: '/metadata',
      predict: '/predict',
      predictBatch: '/predict-batch',
    },
  };
}

// ============================================================================
// ERROR HANDLING
// ============================================================================

/**
 * Handle API errors with user-friendly messages
 */
export function formatAPIError(error) {
  if (error.response) {
    // Server responded with error status
    return {
      status: error.response.status,
      message: error.response.data?.error || error.response.data?.detail || 'Server error',
      data: error.response.data,
    };
  } else if (error.request) {
    // Request made but no response
    return {
      status: null,
      message: 'No response from server. Is the API running?',
      data: null,
    };
  } else {
    // Error in request setup
    return {
      status: null,
      message: error.message || 'Unknown error',
      data: null,
    };
  }
}

// ============================================================================
// EXPORT UTILITIES
// ============================================================================

/**
 * Export prediction results as CSV
 * 
 * @param {Array} results - Array of prediction results
 * @param {string} filename - Output filename
 */
export function exportResultsAsCSV(results, filename = 'segmentation-results.csv') {
  const rows = [];
  
  // Header row
  rows.push(['Filename', 'Class Name', 'Coverage (%)', 'Num Classes']);
  
  // Data rows
  results.forEach((result) => {
    if (result.success && result.coverage) {
      result.coverage.forEach(([className, percentage]) => {
        rows.push([
          result.filename || 'unknown',
          className,
          percentage.toFixed(2),
          result.num_classes,
        ]);
      });
    }
  });
  
  // Create CSV content
  const csvContent = rows.map((row) => row.map((cell) => `"${cell}"`).join(',')).join('\n');
  
  // Download
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
  window.URL.revokeObjectURL(url);
}

// ============================================================================
// EXPORT ALL
// ============================================================================

export default {
  // Metadata
  checkHealth,
  getMetadata,
  getAPIConfig,
  
  // Prediction
  predict,
  predictBatch,
  
  // Utilities
  imageToDataURL,
  downloadBase64Image,
  formatCoverageForDisplay,
  formatAPIError,
  exportResultsAsCSV,
};
