import axios from 'axios';

// Determine the API URL based on environment
const getApiUrl = () => {
  // If VITE_API_URL is set, use it
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // If running on localhost, use local backend
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:5001';
  }

  // If running on Vercel, use Render backend
  if (window.location.hostname.includes('vercel.app')) {
    return 'https://ai-agent-with-frontend.onrender.com';
  }

  // Default to production backend
  return 'https://ai-agent-with-frontend.onrender.com';
};

const API_BASE_URL = getApiUrl();
console.log('Using API URL:', API_BASE_URL);
      
// Create optimized axios instance with dynamic timeout and retry logic
const api = axios.create({
  baseURL: API_BASE_URL + '/', // Add trailing slash to prevent double slashes in URLs
  timeout: 60000, // Increased timeout for chat requests (60 seconds)
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  maxRedirects: 3,
});

// Add request caching for auth checks
const requestCache = new Map();
const CACHE_DURATION = 30000; // 30 seconds for auth checks

// Request interceptor with caching and optimization
api.interceptors.request.use(
  (config) => {
    // Only log in development
    if (import.meta.env.DEV) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    
    // Cache GET requests for auth checks
    if (config.method === 'get' && config.url.includes('/auth/check-auth')) {
      const cacheKey = `${config.method}:${config.url}`;
      const cached = requestCache.get(cacheKey);
      
      if (cached && (Date.now() - cached.timestamp) < CACHE_DURATION) {
        // Return cached response
        config.useCache = true;
        config.cachedData = cached.data;
      }
    }
    
    return config;
  },
  (error) => {
    if (import.meta.env.DEV) {
      console.error('API Request Error:', error);
    }
    return Promise.reject(error);
  }
);

// Advanced retry logic helper
const retryRequest = async (config, maxRetries = 2, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await api.request(config);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Only retry on specific errors
      const shouldRetry = 
        error.code === 'ECONNABORTED' || 
        error.code === 'NETWORK_ERROR' ||
        (error.response?.status >= 500);
        
      if (!shouldRetry) throw error;
      
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
};

// Response interceptor with intelligent caching and retry logic
api.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`API Response: ${response.status} ${response.config.url}`);
    }
    
    // Cache auth check responses
    if (response.config.url?.includes('/auth/check-auth')) {
      const cacheKey = `${response.config.method}:${response.config.url}`;
      requestCache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now()
      });
      
      // Clean old cache entries
      setTimeout(() => {
        requestCache.delete(cacheKey);
      }, CACHE_DURATION);
    }
    
    return response;
  },
  async (error) => {
    if (import.meta.env.DEV) {
      console.error('API Response Error:', error.response?.data || error.message);
    }
    
    // Don't retry auth errors or client errors
    if (error.response?.status === 401 || error.response?.status === 403) {
      return Promise.reject(error);
    }
    
    // Auto-retry on timeouts and server errors for non-chat requests
    const isTimeout = error.code === 'ECONNABORTED';
    const isServerError = error.response?.status >= 500;
    const isNetworkError = error.code === 'NETWORK_ERROR';
    const isChatRequest = error.config.url?.includes('/api/chat');
    
    if ((isTimeout || isServerError || isNetworkError) && !isChatRequest) {
      try {
        return await retryRequest(error.config, 2, 1000);
      } catch (retryError) {
        return Promise.reject(retryError);
      }
    }
    
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
      // Check local cache first for ultra-fast response
      const cacheKey = 'get:/api/auth/check-auth';
      const cached = requestCache.get(cacheKey);
      
      if (cached && (Date.now() - cached.timestamp) < CACHE_DURATION) {
        return cached.data;
      }
      
      const response = await api.get('/api/auth/check-auth');
      
      // Cache the response
      requestCache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now()
      });
      
      return response.data;
    } catch (error) {
      if (import.meta.env.DEV) {
        console.log('Auth check failed:', error.response?.data || error.message);
      }
      // If there's an error (e.g., 401 Unauthorized), assume not authenticated
      return { authenticated: false, reason: 'network_error' };
    }
  },
  

  // Chat APIs with smart timeout and progress handling
  sendMessage: async (message, options = {}) => {
    const { onProgress, timeout = 60000 } = options;
    
    try {
      // Clear auth cache on chat to ensure fresh session
      requestCache.delete('get:/api/auth/check-auth');
      
      // Create request with custom timeout for chat
      const source = axios.CancelToken.source();
      
      // Set up progress tracking if callback provided
      if (onProgress) {
        onProgress('Sending message...');
      }
      
      const response = await api.post('/api/chat', 
        { message }, 
        { 
          timeout,
          cancelToken: source.token,
          onUploadProgress: (progressEvent) => {
            if (onProgress) {
              onProgress('Processing request...');
            }
          }
        }
      );
      
      if (response.data && response.data.success) {
        if (onProgress) {
          onProgress('Response received!');
        }
        return {
          response: response.data.response,
          metadata: response.data.metadata || {}
        };
      } else {
        throw new Error(response.data.error || 'Failed to process message');
      }
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('Chat API Error:', error.response?.data || error.message);
      }
      
      // Enhanced error messages for timeouts
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timed out. The AI is taking longer than expected to respond. Please try a shorter message or try again.');
      }
      
      throw new Error(error.response?.data?.error || error.message || 'Failed to send message');
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

  // Chat History APIs for Firebase
  getChatHistory: async (userId) => {
    try {
      const response = await api.get(`/api/chats/user/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching chat history:', error);
      return { chats: [] };
    }
  },

  getChat: async (chatId) => {
    try {
      const response = await api.get(`/api/chats/${chatId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching chat:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch chat');
    }
  },

  createChat: async (userId, title) => {
    try {
      const response = await api.post('/api/chats', { userId, title });
      return response.data;
    } catch (error) {
      console.error('Error creating chat:', error);
      throw new Error(error.response?.data?.error || 'Failed to create chat');
    }
  },

  updateChat: async (chatId, messages) => {
    try {
      const response = await api.put(`/api/chats/${chatId}`, { messages });
      return response.data;
    } catch (error) {
      console.error('Error updating chat:', error);
      throw new Error(error.response?.data?.error || 'Failed to update chat');
    }
  },

  updateChatTitle: async (chatId, title) => {
    try {
      const response = await api.patch(`/api/chats/${chatId}/title`, { title });
      return response.data;
    } catch (error) {
      console.error('Error updating chat title:', error);
      throw new Error(error.response?.data?.error || 'Failed to update chat title');
    }
  },

  deleteChat: async (chatId) => {
    try {
      const response = await api.delete(`/api/chats/${chatId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting chat:', error);
      throw new Error(error.response?.data?.error || 'Failed to delete chat');
    }
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
