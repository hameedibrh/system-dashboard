import React, { useEffect, useState } from 'react';
import './App.css';
import MetricsCard from './components/MetricsCard';
import ContainerList from './components/ContainerList';
import SystemInfo from './components/SystemInfo';
import { initializeSocket, requestMetrics } from './services/api';

function App() {
  const [metrics, setMetrics] = useState(null);
  const [containers, setContainers] = useState([]);
  const [systemInfo, setSystemInfo] = useState(null);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    const socket = initializeSocket();

    socket.on('connection_response', () => {
      setConnected(true);
      requestMetrics();
    });

    socket.on('metrics_data', (data) => {
      setMetrics(data.metrics);
      setContainers(data.containers || []);
      if (data.metrics.timestamp) {
        setSystemInfo(data.metrics);
      }
      setLastUpdate(new Date());
      setLoading(false);
    });

    socket.on('metrics_update', (data) => {
      setMetrics(data.metrics);
      setContainers(data.containers || []);
      setLastUpdate(new Date());
    });

    socket.on('disconnect', () => {
      setConnected(false);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  if (loading) {
    return (
      <div className="app loading">
        <div className="loader">
          <div className="spinner"></div>
          <p>Connecting to Tenet...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>Tenet</h1>
          <div className="header-right">
            <span className={`status ${connected ? 'connected' : 'disconnected'}`}>
              {connected ? '● Connected' : '● Disconnected'}
            </span>
            <span className="last-update">
              Updated: {lastUpdate.toLocaleTimeString()}
            </span>
          </div>
        </div>
      </header>

      <main className="main-content">
        <section className="metrics-section">
          <h2>System Metrics</h2>
          <div className="metrics-grid">
            {metrics && (
              <>
                <MetricsCard
                  title="CPU Usage"
                  value={metrics.cpu.percent}
                  unit="%"
                  max={100}
                  color="#3b82f6"
                  icon="📊"
                />
                <MetricsCard
                  title="Memory Usage"
                  value={(metrics.memory.used / metrics.memory.total * 100).toFixed(1)}
                  unit="%"
                  max={100}
                  color="#8b5cf6"
                  icon="🧠"
                />
                <MetricsCard
                  title="RAM"
                  value={(metrics.memory.used / (1024 ** 3)).toFixed(1)}
                  unit="GB"
                  max={(metrics.memory.total / (1024 ** 3)).toFixed(1)}
                  color="#ec4899"
                  icon="💾"
                />
                <MetricsCard
                  title="Network Sent"
                  value={(metrics.network.bytes_sent / (1024 ** 3)).toFixed(2)}
                  unit="GB"
                  max={0}
                  color="#10b981"
                  icon="📤"
                />
              </>
            )}
          </div>
        </section>

        {/* Disk Usage */}
        <section className="disk-section">
          <h2>Disk Usage</h2>
          <div className="disk-grid">
            {metrics &&
              Object.values(metrics.disk).map((disk) => (
                <div key={disk.device} className="disk-card">
                  <div className="disk-header">
                    <h3>{disk.device}</h3>
                    <span className="disk-mount">{disk.mountpoint}</span>
                  </div>
                  <div className="disk-bar">
                    <div
                      className="disk-used"
                      style={{
                        width: `${disk.percent}%`,
                        backgroundColor: disk.percent > 80 ? '#ef4444' : '#3b82f6',
                      }}
                    />
                  </div>
                  <div className="disk-stats">
                    <span>{disk.percent.toFixed(1)}% used</span>
                    <span>
                      {(disk.used / (1024 ** 3)).toFixed(1)} GB /{' '}
                      {(disk.total / (1024 ** 3)).toFixed(1)} GB
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </section>

        {/* System Info */}
        {systemInfo && <SystemInfo metrics={metrics} />}

        {/* Docker Containers */}
        <section className="containers-section">
          <h2>Docker Containers ({containers.length})</h2>
          <ContainerList containers={containers} />
        </section>
      </main>
    </div>
  );
}

export default App;
