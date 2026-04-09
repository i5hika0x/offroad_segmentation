import { useState } from 'react';
import { Upload } from 'lucide-react';
import { uploadImage, uploadFolder, readImageAsDataURL } from '../api/segmentationAPI';
import './UploadPanel.css';

export default function UploadPanel({ onImageUpload, onBatchUpload, isLoading }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadMode, setUploadMode] = useState('single'); // 'single' or 'batch'

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files.length === 0) return;

    if (uploadMode === 'single' && files.length > 0) {
      handleSingleFile(files[0]);
    } else if (uploadMode === 'batch') {
      handleMultipleFiles(Array.from(files));
    }
  };

  const handleSingleFile = async (file) => {
    try {
      const preview = await readImageAsDataURL(file);
      const uploadedData = await uploadImage(file);
      onImageUpload({
        file,
        preview,
        imageId: uploadedData.imageId,
        filename: uploadedData.filename,
      });
    } catch (err) {
      console.error('Upload failed:', err);
      alert('Failed to upload image');
    }
  };

  const handleMultipleFiles = async (files) => {
    try {
      const imageFiles = files.filter((f) => f.type.startsWith('image/'));
      if (imageFiles.length === 0) {
        alert('No image files found');
        return;
      }

      const uploadedData = await uploadFolder(imageFiles);
      const previews = await Promise.all(
        imageFiles.map((f) => readImageAsDataURL(f))
      );

      onBatchUpload({
        files: imageFiles,
        previews,
        imageIds: uploadedData.imageIds,
        count: uploadedData.count,
      });
    } catch (err) {
      console.error('Batch upload failed:', err);
      alert('Failed to upload images');
    }
  };

  const handleFileSelect = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    if (uploadMode === 'single') {
      handleSingleFile(files[0]);
    } else {
      handleMultipleFiles(Array.from(files));
    }
  };

  return (
    <div className="upload-panel">
      <div className="upload-mode-toggle">
        <button
          className={`mode-btn ${uploadMode === 'single' ? 'active' : ''}`}
          onClick={() => setUploadMode('single')}
          disabled={isLoading}
        >
          Single Image
        </button>
        <button
          className={`mode-btn ${uploadMode === 'batch' ? 'active' : ''}`}
          onClick={() => setUploadMode('batch')}
          disabled={isLoading}
        >
          Batch/Folder
        </button>
      </div>

      <div
        className={`upload-zone ${dragActive ? 'active' : ''} ${
          isLoading ? 'loading' : ''
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          multiple={uploadMode === 'batch'}
          accept="image/*"
          onChange={handleFileSelect}
          disabled={isLoading}
          style={{ display: 'none' }}
        />

        <label htmlFor="file-input" className="upload-label">
          <Upload size={32} />
          <span>
            {isLoading
              ? 'Uploading...'
              : uploadMode === 'single'
              ? 'Drag image here or click to browse'
              : 'Drag images/folder here or click to browse'}
          </span>
          <small>
            {uploadMode === 'single'
              ? 'Supported: PNG, JPG, JPEG, GIF'
              : 'Multiple images or entire folder'}
          </small>
        </label>
      </div>
    </div>
  );
}
