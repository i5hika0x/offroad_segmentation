import { classConfig, classList } from '../config/segmentationConfig';
import './ClassLegend.css';

export default function ClassLegend({ pixelCoverages = {}, totalPixels = 0 }) {
  return (
    <div className="class-legend">
      <h3>Class Legend & Coverage</h3>
      <div className="legend-grid">
        {classList.map((cls) => {
          const pixelCount = pixelCoverages[cls.id] || 0;
          const percentage =
            totalPixels > 0 ? ((pixelCount / totalPixels) * 100).toFixed(2) : 0;

          return (
            <div key={cls.id} className="legend-item">
              <div
                className="legend-color"
                style={{ backgroundColor: cls.color }}
                title={cls.label}
              />
              <div className="legend-content">
                <div className="legend-label">{cls.label}</div>
                <div className="legend-percentage">{percentage}%</div>
              </div>
              <div className="legend-progress">
                <div
                  className="progress-bar"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: cls.color,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
