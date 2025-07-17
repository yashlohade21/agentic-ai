import axios from 'axios';

// Use local development server by default, fallback to production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const agentApi = {
  // Authentication APIs
  register: async (userData) => {
    try {
      const response = await api.post('/api/auth/register', userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Registration failed');
    }
  },
  
  login: async (credentials) => {
    try {
      const response = await api.post('/api/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  },

  logout: async () => {
    try {
      const response = await api.post('/api/auth/logout');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Logout failed');
    }
  },

  checkAuth: async () => {
    try {
      const response = await api.get('/api/auth/check-auth');
      return response.data;
    } catch (error) {
      console.log('Auth check failed:', error.response?.data || error.message);
      // If there's an error (e.g., 401 Unauthorized), assume not authenticated
      return { authenticated: false, reason: 'network_error' };
    }
  },

  // Chat APIs
  sendMessage: async (message) => {
    try {
      const response = await api.post('/api/chat', { message });
      if (response.data && response.data.success) {
        return {
          response: response.data.response,
          metadata: response.data.metadata || {}
        };
      } else {
        throw new Error(response.data.error || 'Failed to process message');
      }
    } catch (error) {
      console.error('API Error:', error.response?.data || error.message);
      throw new Error(error.response?.data?.error || 'Failed to send message');
    }
  },

getSystemStatus: async () => {
    try {
      const response = await api.get('/api/chat/status');
      return {
        status: response.data.status || 'active',
        agents: response.data.agents || [],
        session_requests: response.data.session_requests || 0
      };
    } catch (error) {
      console.error('Error getting system status:', error);
      // Return a default status that indicates connection issues
      return { 
        status: 'connection_error', 
        agents: [], 
        session_requests: 0 
      };
    }
  },

  initializeAI: async () => {
    try {
      const response = await api.post('/api/chat/initialize');
      return response.data;
    } catch (error) {
      console.error('Error initializing AI:', error);
      throw new Error(error.response?.data?.detail || 'Failed to initialize AI');
    }
  },

  healthCheck: async () => {
    try {
      const response = await api.get('/api/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error(error.response?.data?.detail || 'Backend health check failed');
    }
  },

  clearHistory: async () => {
    // This is a client-side clear for now, as there's no backend history persistence yet
    // If backend history is implemented, this would make an API call
    console.log('Client-side history cleared.');
    return { message: 'History cleared' };
  },

  debugSession: async () => {
    try {
      const response = await api.get('/api/auth/debug-session');
      return response.data;
    } catch (error) {
      console.error('Debug session error:', error);
      throw new Error(error.response?.data?.error || 'Debug session failed');
    }
  }
};

// WebSocket for future real-time features (not fully implemented in backend yet)
export class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.listeners = {};
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('WebSocket connected');
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.emit(data.type, data);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
        
        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.emit('disconnect');
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(type, data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...data }));
    }
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }
}

export default agentApi;
