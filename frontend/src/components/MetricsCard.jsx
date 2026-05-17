import React from 'react';
import './MetricsCard.css';

const MetricsCard = ({ title, value, unit, max, color, icon }) => {
  const percentage = max > 0 ? (value / max) * 100 : 0;
  const displayMax = max > 0 ? `${max}${unit}` : unit;

  return (
    <div className="metrics-card">
      <div className="card-header">
        <span className="icon">{icon}</span>
        <h3>{title}</h3>
      </div>
      
      <div className="card-value">
        <span className="value" style={{ color }}>
          {typeof value === 'number' ? value.toFixed(1) : value}
        </span>
        <span className="unit">{unit}</span>
      </div>

      {max > 0 && (
        <>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${Math.min(percentage, 100)}%`,
                backgroundColor: color,
              }}
            />
          </div>
          <div className="card-footer">
            <span className="percentage">{percentage.toFixed(0)}%</span>
            <span className="max-value">Max: {displayMax}</span>
          </div>
        </>
      )}
    </div>
  );
};

export default MetricsCard;
