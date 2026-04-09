import { Download } from 'lucide-react';
import { exportBatchResultsCSV } from '../api/segmentationAPI';
import './BatchResultsTable.css';

export default function BatchResultsTable({ results = [], isLoading = false }) {
  const handleExportCSV = async () => {
    try {
      await exportBatchResultsCSV(results);
    } catch (err) {
      console.error('Export failed:', err);
      alert('Failed to export CSV');
    }
  };

  if (results.length === 0) {
    return (
      <div className="batch-results-placeholder">
        <p>Upload multiple images to see batch results</p>
      </div>
    );
  }

  return (
    <div className="batch-results">
      <div className="results-header">
        <h3>Batch Processing Results</h3>
        <button
          className="export-btn"
          onClick={handleExportCSV}
          disabled={isLoading}
        >
          <Download size={16} />
          Export CSV
        </button>
      </div>

      <div className="table-responsive">
        <table className="results-table">
          <thead>
            <tr>
              <th>Filename</th>
              <th>Inference Time (ms)</th>
              <th>Model Version</th>
              <th>Top Class</th>
              <th>Confidence</th>
              <th>Risk Level</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, idx) => (
              <tr key={idx} className={`status-${result.status}`}>
                <td className="filename">
                  <span title={result.filename}>{result.filename}</span>
                </td>
                <td>{result.inferenceTime || '-'}</td>
                <td>
                  <span className="model-badge">{result.modelVersion || '-'}</span>
                </td>
                <td>{result.topClass || '-'}</td>
                <td>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${(result.confidence || 0) * 100}%`,
                      }}
                    />
                    <span>{((result.confidence || 0) * 100).toFixed(1)}%</span>
                  </div>
                </td>
                <td>
                  <span
                    className={`risk-badge risk-${(result.riskLevel || 'unknown').toLowerCase()}`}
                  >
                    {result.riskLevel || '-'}
                  </span>
                </td>
                <td>
                  <span className={`status-badge status-${result.status}`}>
                    {result.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="results-summary">
        <div className="summary-stat">
          <label>Total Images</label>
          <value>{results.length}</value>
        </div>
        <div className="summary-stat">
          <label>Avg Inference Time</label>
          <value>
            {(
              results.reduce((sum, r) => sum + (r.inferenceTime || 0), 0) /
              results.length
            ).toFixed(1)}
            ms
          </value>
        </div>
        <div className="summary-stat">
          <label>Success Rate</label>
          <value>
            {(
              (results.filter((r) => r.status === 'completed').length /
                results.length) *
              100
            ).toFixed(1)}
            %
          </value>
        </div>
      </div>
    </div>
  );
}
