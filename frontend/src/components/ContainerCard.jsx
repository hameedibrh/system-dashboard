import React, { useState } from 'react';
import { startContainer, stopContainer } from '../services/api';
import './ContainerCard.css';

const ContainerCard = ({ container }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    try {
      await startContainer(container.id);
    } catch (err) {
      setError('Failed to start container');
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    setError(null);
    try {
      await stopContainer(container.id);
    } catch (err) {
      setError('Failed to stop container');
    } finally {
      setLoading(false);
    }
  };

  const isRunning = container.status === 'running';
  const cpuPercent = container.stats?.cpu_percent || 0;
  const memoryUsage = container.stats?.memory_usage || 0;
  const memoryLimit = container.stats?.memory_limit || 1;
  const memoryPercent = (memoryUsage / memoryLimit) * 100;

  return (
    <div className={`container-card ${isRunning ? 'running' : 'stopped'}`}>
      <div className="container-header">
        <div className="container-info">
          <h4 className="container-name">{container.name}</h4>
          <p className="container-image">{container.image}</p>
        </div>
        <span className={`status-badge ${isRunning ? 'running' : 'stopped'}`}>
          {isRunning ? '● Running' : '● Stopped'}
        </span>
      </div>

      {isRunning && container.stats && (
        <div className="container-stats">
          <div className="stat-item">
            <span className="stat-label">CPU</span>
            <span className="stat-value">{cpuPercent.toFixed(1)}%</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Memory</span>
            <span className="stat-value">{memoryPercent.toFixed(1)}%</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">({(memoryUsage / (1024 ** 2)).toFixed(0)}MB)</span>
          </div>
        </div>
      )}

      {container.ports && container.ports.length > 0 && (
        <div className="container-ports">
          <span className="ports-label">Ports:</span>
          {container.ports.map((port, idx) => (
            <span key={idx} className="port-badge">
              {port.host_port ? `${port.host_port}→` : ''}{port.container_port}
            </span>
          ))}
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      <div className="container-actions">
        {isRunning ? (
          <button
            className="btn btn-stop"
            onClick={handleStop}
            disabled={loading}
          >
            {loading ? 'Stopping...' : '⏹ Stop'}
          </button>
        ) : (
          <button
            className="btn btn-start"
            onClick={handleStart}
            disabled={loading}
          >
            {loading ? 'Starting...' : '▶ Start'}
          </button>
        )}
      </div>
    </div>
  );
};

export default ContainerCard;
