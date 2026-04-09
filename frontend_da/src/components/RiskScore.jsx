import { calculateRiskScore } from '../config/segmentationConfig';
import './RiskScore.css';

export default function RiskScore({ pixelCoverages = null }) {
  if (!pixelCoverages) {
    return (
      <div className="risk-score-placeholder">
        <p>Run inference to see traversability score</p>
      </div>
    );
  }

  const { score, level, color } = calculateRiskScore(pixelCoverages);

  return (
    <div className="risk-score-card">
      <div className="risk-header">
        <h3>Traversability Score</h3>
        <span className={`risk-level risk-${level.toLowerCase()}`}>{level}</span>
      </div>

      <div className="risk-gauge">
        <div
          className="risk-indicator"
          style={{
            background: `conic-gradient(${color} 0deg ${
              (score / 100) * 360
            }deg, rgba(255,255,255,0.1) ${(score / 100) * 360}deg 360deg)`,
          }}
        >
          <div className="risk-score-value">
            <span className="score">{score.toFixed(1)}</span>
            <span className="unit">%</span>
          </div>
        </div>
      </div>

      <p className="risk-description">
        {level === 'Safe' &&
          'Terrain is safe for traversal with high confidence in ground-level coverage.'}
        {level === 'Caution' &&
          'Mixed terrain detected. Proceed with caution due to moderate obstacles.'}
        {level === 'High-Risk' &&
          'High obstacle density or water detected. Not recommended for traversal.'}
      </p>

      <div className="risk-metrics">
        <div className="metric-item">
          <label>Risk Assessment</label>
          <div
            className="metric-bar"
            style={{
              background: `linear-gradient(90deg, #4CAF50 0%, #FFC107 50%, #E53935 100%)`,
            }}
          >
            <div
              className="metric-indicator"
              style={{ left: `${score}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
