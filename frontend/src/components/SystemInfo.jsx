import React from 'react';
import './SystemInfo.css';

const SystemInfo = ({ metrics }) => {
  if (!metrics) return null;

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / (24 * 3600));
    const hours = Math.floor((seconds % (24 * 3600)) / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${mins}m`;
  };

  return (
    <section className="system-info-section">
      <h2>System Information</h2>
      <div className="info-grid">
        <div className="info-item">
          <span className="info-label">Hostname</span>
          <span className="info-value">{metrics.hostname || 'N/A'}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Operating System</span>
          <span className="info-value">{metrics.system || 'N/A'}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Kernel</span>
          <span className="info-value">{metrics.release || 'N/A'}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Architecture</span>
          <span className="info-value">{metrics.architecture || 'N/A'}</span>
        </div>
        <div className="info-item">
          <span className="info-label">CPU Cores</span>
          <span className="info-value">{metrics.cpu?.count || 'N/A'}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Uptime</span>
          <span className="info-value">{formatUptime(metrics.cpu?.uptime_seconds || 0)}</span>
        </div>
      </div>
    </section>
  );
};

export default SystemInfo;
