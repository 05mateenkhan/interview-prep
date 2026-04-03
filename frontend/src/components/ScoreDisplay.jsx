import './ScoreDisplay.css';

export default function ScoreDisplay({ score }) {
  const getScoreColor = (value) => {
    if (value >= 80) return 'var(--success)';
    if (value >= 60) return 'var(--warning)';
    return 'var(--error)';
  };

  const metrics = [
    { label: 'Accuracy', value: score.accuracy },
    { label: 'Clarity', value: score.clarity },
    { label: 'Completeness', value: score.completeness },
  ];

  return (
    <div className="score-display">
      <div className="score-overall">
        <span className="score-label">Overall Score</span>
        <span
          className="score-value"
          style={{ color: getScoreColor(score.overall) }}
        >
          {score.overall}
        </span>
        <span className="score-max">/100</span>
      </div>

      <div className="score-metrics">
        {metrics.map((metric) => (
          <div key={metric.label} className="score-metric">
            <div className="metric-header">
              <span className="metric-label">{metric.label}</span>
              <span
                className="metric-value"
                style={{ color: getScoreColor(metric.value) }}
              >
                {metric.value}
              </span>
            </div>
            <div className="metric-bar">
              <div
                className="metric-fill"
                style={{
                  width: `${metric.value}%`,
                  background: getScoreColor(metric.value),
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}