import React from 'react';
import ContainerCard from './ContainerCard';
import './ContainerList.css';

const ContainerList = ({ containers }) => {
  const running = containers.filter(c => c.status === 'running');
  const stopped = containers.filter(c => c.status !== 'running');

  return (
    <div className="container-list">
      {containers.length === 0 ? (
        <div className="empty-state">
          <p>No Docker containers found</p>
        </div>
      ) : (
        <>
          {running.length > 0 && (
            <div className="container-group">
              <h3 className="group-title">Running ({running.length})</h3>
              <div className="containers-grid">
                {running.map((container) => (
                  <ContainerCard key={container.id} container={container} />
                ))}
              </div>
            </div>
          )}
          {stopped.length > 0 && (
            <div className="container-group">
              <h3 className="group-title">Stopped ({stopped.length})</h3>
              <div className="containers-grid">
                {stopped.map((container) => (
                  <ContainerCard key={container.id} container={container} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ContainerList;
