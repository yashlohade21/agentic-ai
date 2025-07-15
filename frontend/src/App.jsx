import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import { 
  Bot, Settings, History, FileText, Brain, Search, Code, Eye, X, RefreshCw, 
  LogOut, Menu, Sun, Moon, Zap, MessageSquare, Users, Activity, Sparkles
} from 'lucide-react';
import { agentApi } from './api/agentApi';
import MessageRenderer from './components/MessageRenderer';
import WelcomeMessage from './components/WelcomeMessage';
import ChatInput from './components/ChatInput';
import AuthForm from './components/AuthForm';
import AgentStatus from './components/AgentStatus';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState({
    status: 'active',
    agents: ['enhanced_orchestrator', 'enhanced_coder', 'researcher'],
    session_requests: 0
  });
  const [activeAgents, setActiveAgents] = useState(systemStatus.agents || []);
  const [showSettings, setShowSettings] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const messagesEndRef = useRef(null);

  const agentIcons = {
    'enhanced_orchestrator': Bot,
    'enhanced_coder': Code,
    'planner': FileText,
    'researcher': Search,
    'file_picker': FileText,
    'reviewer': Eye,
    'thinker': Brain
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      checkBackendConnection();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    console.log('System status updated:', systemStatus);
  }, [systemStatus]);

  const checkAuthStatus = async () => {
    try {
      const authStatus = await agentApi.checkAuth();
      if (authStatus.authenticated) {
        setUser(authStatus.user);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.log('Not authenticated');
    } finally {
      setAuthLoading(false);
    }
  };

  const checkBackendConnection = async () => {
    try {
      const health = await agentApi.healthCheck();
      if (health.status === 'ok') {
        setConnectionStatus('connected');
        const status = await agentApi.getSystemStatus();
        setSystemStatus(status);
        setActiveAgents(status.agents || []);
        toast.success('Connected to AI system', {
          icon: '🤖',
          duration: 2000,
        });
      }
    } catch (error) {
      console.log('Backend not available, using mock mode');
      setConnectionStatus('mock');
      toast.error('Using offline mode', {
        icon: '⚠️',
        duration: 3000,
      });
    }
  };

  const handleLogin = async (credentials) => {
    try {
      const response = await agentApi.login(credentials);
      setUser(response.user);
      setIsAuthenticated(true);
      toast.success(`Welcome back, ${response.user.username}!`, {
        icon: '👋',
        duration: 3000,
      });
      return response;
    } catch (error) {
      throw error;
    }
  };

  const handleRegister = async (userData) => {
    try {
      const response = await agentApi.register(userData);
      setUser(response.user);
      setIsAuthenticated(true);
      toast.success(`Welcome to BinaryBrained AI, ${response.user.username}!`, {
        icon: '🎉',
        duration: 4000,
      });
      return response;
    } catch (error) {
      throw error;
    }
  };

  const handleLogout = async () => {
    try {
      await agentApi.logout();
      setUser(null);
      setIsAuthenticated(false);
      setMessages([]);
      setConnectionStatus('disconnected');
      toast.success('Logged out successfully', {
        icon: '👋',
        duration: 2000,
      });
    } catch (error) {
      console.error('Logout error:', error);
      setUser(null);
      setIsAuthenticated(false);
      setMessages([]);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await agentApi.sendMessage(currentInput);
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.response,
        timestamp: new Date(),
        metadata: response.metadata
      };
      setMessages(prev => [...prev, botMessage]);
      toast.success('Response received', {
        icon: '✨',
        duration: 1500,
      });
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      toast.error('Failed to send message', {
        icon: '❌',
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearHistory = async () => {
    try {
      if (connectionStatus === 'connected') {
        await agentApi.clearHistory();
      }
      setMessages([]);
      toast.success('Chat history cleared', {
        icon: '🧹',
        duration: 2000,
      });
    } catch (error) {
      console.error('Error clearing history:', error);
      setMessages([]);
    }
  };

  const refreshSystem = async () => {
    setIsLoading(true);
    try {
      await checkBackendConnection();
      toast.success('System refreshed', {
        icon: '🔄',
        duration: 2000,
      });
    } catch (error) {
      console.error('Error refreshing system:', error);
      toast.error('Failed to refresh system', {
        icon: '❌',
        duration: 3000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    toast.success(`${darkMode ? 'Light' : 'Dark'} mode activated`, {
      icon: darkMode ? '☀️' : '🌙',
      duration: 2000,
    });
  };

  // Loading screen with enhanced animations
  if (authLoading) {
    return (
      <div className="loading-screen">
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: darkMode ? '#1f2937' : '#ffffff',
              color: darkMode ? '#f9fafb' : '#111827',
              border: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`,
              borderRadius: '12px',
              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
            },
          }}
        />
        <motion.div 
          className="loading-content"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            className="mb-8"
            animate={{ 
              rotate: 360,
              scale: [1, 1.1, 1]
            }}
            transition={{ 
              rotate: { duration: 2, repeat: Infinity, ease: "linear" },
              scale: { duration: 1, repeat: Infinity, ease: "easeInOut" }
            }}
          >
            <Bot size={64} />
          </motion.div>
          <motion.h2 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            BinaryBrained AI
          </motion.h2>
          <motion.p 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            Initializing AI System...
          </motion.p>
          <motion.div 
            className="loading-spinner"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          />
        </motion.div>
      </div>
    );
  }

  // Auth form
  if (!isAuthenticated) {
    return <AuthForm onLogin={handleLogin} onRegister={handleRegister} isLoading={authLoading} />;
  }

  return (
    <div className={`app ${darkMode ? 'dark' : ''}`}>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: darkMode ? '#1f2937' : '#ffffff',
            color: darkMode ? '#f9fafb' : '#111827',
            border: `1px solid ${darkMode ? '#374151' : '#e5e7eb'}`,
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
          },
        }}
      />
      
      {/* Enhanced Header */}
      <motion.header 
        className="app-header"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="header-left">
          <motion.button
            className="menu-btn"
            onClick={() => setShowSidebar(!showSidebar)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Menu size={20} />
          </motion.button>
          
          <motion.div 
            className="app-title-section"
            whileHover={{ scale: 1.02 }}
          >
            <div className="app-icon-container">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                <Bot size={32} className="app-icon" />
              </motion.div>
              <motion.div
                className="status-dot active"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </div>
            <div>
              <h1 className="gradient-text">BinaryBrained AI</h1>
            </div>
          </motion.div>
        </div>

        <div className="header-right">
          {/* Always visible user info */}
          <motion.div 
            className="user-info"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Users size={16} />
            <span>{user?.username}</span>
          </motion.div>

          {/* Desktop buttons - visible on larger screens */}
          <div className="desktop-buttons">
              <motion.button
                    className="header-btn"
                    onClick={toggleDarkMode}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                  </motion.button>

                  <motion.button
                    className="header-btn"
                    onClick={() => setShowSidebar(!showSidebar)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <History size={20} />
                  </motion.button>

                  <motion.button
                    className="header-btn"
                    onClick={() => setShowSettings(!showSettings)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Settings size={20} />
                  </motion.button>

                  <motion.button
                    className="header-btn logout-btn"
                    onClick={handleLogout}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                <LogOut size={20} />
                  </motion.button>
          </div>

          {/* Mobile menu button - visible on small screens */}
          <motion.button
            className="mobile-menu-btn"
            onClick={() => setShowMobileMenu(!showMobileMenu)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Menu size={20} />
          </motion.button>
        </div>
      </motion.header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {showMobileMenu && (
          <motion.div
            className="mobile-menu"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            <motion.button
              className="mobile-menu-item"
              onClick={() => {
                toggleDarkMode();
                setShowMobileMenu(false);
              }}
            >
              {darkMode ? <Sun size={20} /> : <Moon size={20} />}
              <span>{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
            </motion.button>

            <motion.button
                className="mobile-menu-item"
                onClick={() => setShowSettings(!showSettings)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Settings size={20} />
                    <span>Settings</span>
            </motion.button>

            <motion.button
              className="mobile-menu-item"
              onClick={() => {
                setShowSidebar(!showSidebar);
                setShowMobileMenu(false);
              }}
            >
              <History size={20} />
              <span>History</span>
            </motion.button>
            
            <motion.button
              className="mobile-menu-item logout"
              onClick={() => {
                handleLogout();
                setShowMobileMenu(false);
              }}
            >
              <LogOut size={20} />
              <span>Logout</span>
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
      <div className="app-body">
        {/* Enhanced Sidebar */}
        <AnimatePresence>
          {showSidebar && (
            <motion.aside
              className="sidebar open"
              initial={{ x: -320, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -320, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
            >
              <div className="sidebar-content">
                {/* Agent Status */}
                <motion.div
                  className="agents-panel"
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.1 }}
                >
                  <h3>
                    <Activity size={20} />
                    Active Agents
                  </h3>
                  <div className="agents-list">
                    {activeAgents.map((agent, index) => {
                      const IconComponent = agentIcons[agent] || Bot;
                      return (
                        <motion.div
                          key={agent}
                          className="agent-item"
                          initial={{ x: -20, opacity: 0 }}
                          animate={{ x: 0, opacity: 1 }}
                          transition={{ delay: 0.1 * index }}
                          whileHover={{ scale: 1.02 }}
                        >
                          <motion.div
                            animate={{ rotate: [0, 5, -5, 0] }}
                            transition={{ duration: 2, repeat: Infinity, delay: index * 0.5 }}
                          >
                            <IconComponent size={18} />
                          </motion.div>
                          <span>{agent.replace(/_/g, ' ')}</span>
                          <motion.div
                            className="agent-status-indicator"
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, repeat: Infinity, delay: index * 0.3 }}
                          />
                        </motion.div>
                      );
                    })}
                  </div>
                </motion.div>

                {/* Chat History */}
                <motion.div
                  className="history-panel"
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="panel-header">
                    <h3>
                      <MessageSquare size={20} />
                      Recent Chats
                    </h3>
                    <motion.button
                      className="clear-btn"
                      onClick={clearHistory}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Clear
                    </motion.button>
                  </div>
                  <div className="history-list">
                    {messages.filter(m => m.type === 'user').slice(-10).map((msg, index) => (
                      <motion.div
                        key={msg.id}
                        className="history-item"
                        onClick={() => setInputValue(msg.content)}
                        initial={{ x: -20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: 0.05 * index }}
                        whileHover={{ scale: 1.02, x: 5 }}
                      >
                        <p>{msg.content.substring(0, 80)}{msg.content.length > 80 ? '...' : ''}</p>
                        <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
                      </motion.div>
                    ))}
                    {messages.filter(m => m.type === 'user').length === 0 && (
                      <div className="empty-history">
                        <MessageSquare size={32} />
                        <p>No conversations yet</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Main Chat Area */}
        <main className="chat-container">
          <div className="messages-container">
            <AnimatePresence>
              {messages.length === 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.5 }}
                >
                  <WelcomeMessage onExampleClick={setInputValue} />
                </motion.div>
              )}
            </AnimatePresence>

            <div className="messages-list">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.95 }}
                    transition={{ 
                      duration: 0.3,
                      delay: index * 0.05,
                      ease: "easeOut"
                    }}
                  >
                    <MessageRenderer message={message} />
                  </motion.div>
                ))}
              </AnimatePresence>

              {isLoading && (
                <motion.div
                  className="loading-message"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <div className="message bot loading">
                    <div className="message-header">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      >
                        <Bot size={20} />
                      </motion.div>
                      <span>AI is thinking...</span>
                    </div>
                    <div className="message-content">
                      <div className="typing-indicator">
                        {[0, 1, 2].map((i) => (
                          <motion.div
                            key={i}
                            className="typing-dot"
                            animate={{
                              scale: [1, 1.5, 1],
                              opacity: [0.5, 1, 0.5]
                            }}
                            transition={{
                              duration: 1.5,
                              repeat: Infinity,
                              delay: i * 0.2
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
            
            <div ref={messagesEndRef} />
          </div>

          {/* Enhanced Chat Input */}
          <motion.div 
            className="chat-input-section"
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <ChatInput 
              inputValue={inputValue}
              setInputValue={setInputValue}
              onSendMessage={sendMessage}
              isLoading={isLoading}
              onKeyPress={handleKeyPress}
            />
          </motion.div>
        </main>

        {/* Enhanced Settings Panel */}
        <AnimatePresence>
          {showSettings && (
            <motion.aside
              className="settings-panel open"
              initial={{ x: 320, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 320, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
            >
              <div className="panel-header">
                <h3>
                  <Settings size={20} />
                  Settings
                </h3>
                <motion.button
                  className="close-btn"
                  onClick={() => setShowSettings(false)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <X size={20} />
                </motion.button>
              </div>

              <div className="settings-content">
                <AgentStatus 
                  systemStatus={systemStatus}
                  connectionStatus={connectionStatus}
                  user={user}
                  onRefresh={refreshSystem}
                  onClearHistory={clearHistory}
                  onLogout={handleLogout}
                  onToggleDarkMode={toggleDarkMode}
                  darkMode={darkMode}
                  isLoading={isLoading}
                />
              </div>
            </motion.aside>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;