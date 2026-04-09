import { useState } from 'react';
import './ValidationResults.css';

export default function ValidationResults({
  overallMetrics = null,
  ablationMetrics = null,
  isLoading = false,
}) {
  const [activeTab, setActiveTab] = useState('metrics'); // 'metrics' or 'ablation'

  if (!overallMetrics && !ablationMetrics) {
    return (
      <div className="validation-placeholder">
        <p>Validation and ablation study results will appear here</p>
      </div>
    );
  }

  return (
    <div className="validation-results">
      <div className="validation-tabs">
        <button
          className={`tab-btn ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Validation Metrics
        </button>
        <button
          className={`tab-btn ${activeTab === 'ablation' ? 'active' : ''}`}
          onClick={() => setActiveTab('ablation')}
        >
          Ablation Study
        </button>
      </div>

      {/* Validation Metrics Tab */}
      {activeTab === 'metrics' && overallMetrics && (
        <div className="metrics-content">
          <div className="metrics-comparison">
            <div className="model-comparison">
              <h4>Baseline Model</h4>
              <div className="model-stats">
                <MetricCard
                  label="Mean IoU"
                  value={overallMetrics.baseline?.meanIoU}
                />
                <MetricCard
                  label="Pixel Accuracy"
                  value={overallMetrics.baseline?.pixelAccuracy}
                />
                <MetricCard label="Dice Score" value={overallMetrics.baseline?.dice} />
                <MetricCard
                  label="Latency"
                  value={overallMetrics.baseline?.latency}
                  unit="ms"
                />
              </div>
            </div>

            <div className="comparison-arrow">→</div>

            <div className="model-comparison">
              <h4>Improved Model</h4>
              <div className="model-stats">
                <MetricCard
                  label="Mean IoU"
                  value={overallMetrics.improved?.meanIoU}
                />
                <MetricCard
                  label="Pixel Accuracy"
                  value={overallMetrics.improved?.pixelAccuracy}
                />
                <MetricCard label="Dice Score" value={overallMetrics.improved?.dice} />
                <MetricCard
                  label="Latency"
                  value={overallMetrics.improved?.latency}
                  unit="ms"
                />
              </div>
            </div>
          </div>

          {/* Per-class IoU */}
          {overallMetrics.perClassIoU && (
            <div className="per-class-metrics">
              <h4>Per-Class IoU Comparison</h4>
              <div className="class-iou-grid">
                {Object.entries(overallMetrics.perClassIoU).map(([className, iou]) => (
                  <div key={className} className="class-iou-item">
                    <label>{className}</label>
                    <div className="iou-bar">
                      <div
                        className="iou-fill"
                        style={{
                          width: `${Math.min(iou * 100, 100)}%`,
                          background: `hsl(${(iou * 120).toFixed(0)}, 100%, 50%)`,
                        }}
                      />
                    </div>
                    <span>{(iou * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Ablation Study Tab */}
      {activeTab === 'ablation' && ablationMetrics && (
        <div className="ablation-content">
          <div className="ablation-comparison">
            <div className="ablation-model">
              <h4>Without Augmentation</h4>
              <div className="ablation-stats">
                <MetricCard
                  label="Mean IoU"
                  value={ablationMetrics.withoutAugmentation?.meanIoU}
                />
                <MetricCard
                  label="Pixel Accuracy"
                  value={ablationMetrics.withoutAugmentation?.pixelAccuracy}
                />
                <MetricCard
                  label="Inference Time"
                  value={ablationMetrics.withoutAugmentation?.inferenceTime}
                  unit="ms"
                />
              </div>
              <p className="ablation-note">
                Baseline configuration without data augmentation
              </p>
            </div>

            <div className="comparison-arrow">→</div>

            <div className="ablation-model highlight">
              <h4>With Augmentation</h4>
              <div className="ablation-stats">
                <MetricCard
                  label="Mean IoU"
                  value={ablationMetrics.withAugmentation?.meanIoU}
                  improved
                />
                <MetricCard
                  label="Pixel Accuracy"
                  value={ablationMetrics.withAugmentation?.pixelAccuracy}
                  improved
                />
                <MetricCard
                  label="Inference Time"
                  value={ablationMetrics.withAugmentation?.inferenceTime}
                  unit="ms"
                />
              </div>
              <p className="ablation-note">
                Configuration with aggressive data augmentation
              </p>
            </div>
          </div>

          {/* Improvement metrics */}
          {ablationMetrics.withAugmentation &&
            ablationMetrics.withoutAugmentation && (
              <div className="improvement-metrics">
                <h4>Augmentation Impact</h4>
                <div className="improvement-grid">
                  <ImprovementCard
                    label="Mean IoU Improvement"
                    baseline={ablationMetrics.withoutAugmentation.meanIoU}
                    improved={ablationMetrics.withAugmentation.meanIoU}
                  />
                  <ImprovementCard
                    label="Pixel Accuracy Improvement"
                    baseline={
                      ablationMetrics.withoutAugmentation.pixelAccuracy
                    }
                    improved={ablationMetrics.withAugmentation.pixelAccuracy}
                  />
                </div>
              </div>
            )}
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value, unit = '', improved = false }) {
  return (
    <div className={`metric-card ${improved ? 'highlight' : ''}`}>
      <label>{label}</label>
      <div className="metric-value">
        {value !== null && value !== undefined ? (
          <>
            <span>{(value * 100).toFixed(2)}</span>
            {unit && <span className="unit">{unit}</span>}
          </>
        ) : (
          <span>-</span>
        )}
      </div>
    </div>
  );
}

function ImprovementCard({ label, baseline, improved }) {
  const improvement = (improved - baseline) * 100;
  const percentageGain = ((improvement / (baseline * 100)) * 100).toFixed(1);

  return (
    <div className="improvement-card">
      <label>{label}</label>
      <div className="improvement-value">
        <span className={improvement >= 0 ? 'positive' : 'negative'}>
          {improvement >= 0 ? '+' : ''}
          {improvement.toFixed(2)}%
        </span>
        <span className="gain">({percentageGain}% gain)</span>
      </div>
    </div>
  );
}
