// Fixed color palette for segmentation classes
export const classConfig = {
  drivable_ground: {
    id: 0,
    label: 'Drivable Ground',
    color: '#4CAF50',
    hexColor: '#4CAF50',
    riskWeight: -1, // Decreases risk
  },
  rock: {
    id: 1,
    label: 'Rock',
    color: '#795548',
    hexColor: '#795548',
    riskWeight: 0.8,
  },
  log: {
    id: 2,
    label: 'Log',
    color: '#8D6E63',
    hexColor: '#8D6E63',
    riskWeight: 0.7,
  },
  clutter: {
    id: 3,
    label: 'Clutter',
    color: '#A1887F',
    hexColor: '#A1887F',
    riskWeight: 0.6,
  },
  grass: {
    id: 4,
    label: 'Grass',
    color: '#81C784',
    hexColor: '#81C784',
    riskWeight: -0.5,
  },
  sky: {
    id: 5,
    label: 'Sky',
    color: '#64B5F6',
    hexColor: '#64B5F6',
    riskWeight: 0,
  },
  water: {
    id: 6,
    label: 'Water',
    color: '#00BCD4',
    hexColor: '#00BCD4',
    riskWeight: 1.0, // High risk
  },
  vegetation: {
    id: 7,
    label: 'Vegetation',
    color: '#66BB6A',
    hexColor: '#66BB6A',
    riskWeight: 0.3,
  },
  stairs: {
    id: 8,
    label: 'Stairs',
    color: '#FF9800',
    hexColor: '#FF9800',
    riskWeight: 0.5,
  },
  obstacle: {
    id: 9,
    label: 'Obstacle',
    color: '#E53935',
    hexColor: '#E53935',
    riskWeight: 0.9,
  },
};

// Convert to array for easier iteration
export const classList = Object.entries(classConfig).map(([key, value]) => ({
  key,
  ...value,
}));

// Calculate traversability/risk score
export function calculateRiskScore(pixelCoverages) {
  let score = 0;
  let totalPixels = 0;

  classList.forEach((cls) => {
    const coverage = pixelCoverages[cls.id] || 0;
    score += coverage * cls.riskWeight;
    totalPixels += coverage;
  });

  // Normalize to 0-100
  if (totalPixels === 0) return { score: 0, level: 'unknown', color: '#999' };

  const normalizedScore = (score / totalPixels) * 100;

  if (normalizedScore < 30) {
    return { score: normalizedScore, level: 'Safe', color: '#4CAF50' };
  } else if (normalizedScore < 60) {
    return { score: normalizedScore, level: 'Caution', color: '#FFC107' };
  } else {
    return { score: normalizedScore, level: 'High-Risk', color: '#E53935' };
  }
}
