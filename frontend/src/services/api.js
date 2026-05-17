import io from 'socket.io-client';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
let socket = null;

export const initializeSocket = () => {
  if (!socket) {
    socket = io(API_BASE_URL, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      transports: ['websocket', 'polling'],
    });
  }
  return socket;
};

export const getSocket = () => {
  return socket || initializeSocket();
};

// ==================== WebSocket Events ====================

export const requestMetrics = () => {
  const sock = getSocket();
  if (sock) {
    sock.emit('request_metrics');
  }
};

export const startMetricsStream = () => {
  const sock = getSocket();
  if (sock) {
    sock.emit('start_metrics_stream');
  }
};

export const stopMetricsStream = () => {
  const sock = getSocket();
  if (sock) {
    sock.emit('stop_metrics_stream');
  }
};

// ==================== REST API Calls ====================

export const getSystemMetrics = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/system`);
    return response.data;
  } catch (error) {
    console.error('Error fetching system metrics:', error);
    throw error;
  }
};

export const getContainers = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/docker/containers`);
    return response.data;
  } catch (error) {
    console.error('Error fetching containers:', error);
    throw error;
  }
};

export const getContainerStats = async (containerId) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/api/docker/containers/${containerId}/stats`
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching container stats:', error);
    throw error;
  }
};

export const startContainer = async (containerId) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/docker/containers/${containerId}/start`
    );
    return response.data;
  } catch (error) {
    console.error('Error starting container:', error);
    throw error;
  }
};

export const stopContainer = async (containerId) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/docker/containers/${containerId}/stop`
    );
    return response.data;
  } catch (error) {
    console.error('Error stopping container:', error);
    throw error;
  }
};

export const getContainerLogs = async (containerId, tail = 100) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/api/docker/containers/${containerId}/logs`,
      { params: { tail } }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching container logs:', error);
    throw error;
  }
};
