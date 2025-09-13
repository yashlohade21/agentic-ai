import React, { useState, useEffect, useRef } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { 
  Bot, Settings, History, FileText, Brain, Search, Code, Eye, X, RefreshCw, 
  LogOut, Menu, Sun, Moon, MessageSquare, Users, Activity, Plus, Send, ChevronLeft
} from 'lucide-react';
import { agentApi } from './api/agentApi';
import MessageRenderer from './components/MessageRenderer';
import WelcomeMessage from './components/WelcomeMessage';
import ChatInput from './components/ChatInput';
import AuthForm from './components/AuthForm';
import AgentStatus from './components/AgentStatus';
import ChatSidebar from './components/ChatSidebar';
import DeepLearningDashboard from './components/DeepLearningDashboard';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [chats, setChats] = useState([]);
  const [refreshSidebar, setRefreshSidebar] = useState(0);
  const sidebarRef = useRef(null);
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
  const [currentView, setCurrentView] = useState('chat'); // 'chat' or 'deeplearning'
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
    
    // Initialize dark mode from localStorage or system preference
    const savedDarkMode = localStorage.getItem('darkMode');
    const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldUseDarkMode = savedDarkMode ? JSON.parse(savedDarkMode) : systemDarkMode;
    
    setDarkMode(shouldUseDarkMode);
    if (shouldUseDarkMode) {
      document.documentElement.classList.add('theme-dark');
      document.body.classList.add('theme-dark');
    }
  }, []);
  
  // Save dark mode preference
  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  useEffect(() => {
    if (isAuthenticated) {
      checkBackendConnection();
      
      // Reduced frequency of auth checks to 15 minutes for better performance
      const authCheckInterval = setInterval(async () => {
        const authStatus = await agentApi.checkAuth();
        if (!authStatus.authenticated) {
          if (authStatus.reason === 'session_expired') {
            toast.error('Your session has expired. Please log in again.', {
              icon: '⏰',
              duration: 4000,
            });
          }
          setUser(null);
          setIsAuthenticated(false);
          setMessages([]);
          setConnectionStatus('disconnected');
        }
      }, 15 * 60 * 1000); // 15 minutes instead of 5
      
      return () => clearInterval(authCheckInterval);
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
      } else {
        // Handle different reasons for not being authenticated
        if (authStatus.reason === 'session_expired') {
          toast.error('Your session has expired. Please log in again.', {
            icon: '⏰',
            duration: 4000,
          });
        }
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.log('Auth check failed:', error);
      setUser(null);
      setIsAuthenticated(false);
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
      toast.success(`Welcome to BinaryBrained, ${response.user.username}!`, {
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
      // Clear all local state
      setUser(null);
      setIsAuthenticated(false);
      setMessages([]);
      setConnectionStatus('disconnected');
      setSystemStatus({ status: 'inactive', agents: [], session_requests: 0 });
      setActiveAgents([]);
      setCurrentView('chat');
      
      toast.success('Logged out successfully', {
        icon: '👋',
        duration: 2000,
      });
    } catch (error) {
      console.error('Logout error:', error);
      // Even if logout fails on server, clear local state
      setUser(null);
      setIsAuthenticated(false);
      setMessages([]);
      setConnectionStatus('disconnected');
      setSystemStatus({ status: 'inactive', agents: [], session_requests: 0 });
      setActiveAgents([]);
      setCurrentView('chat');
      
      toast.error('Logout completed (with errors)', {
        icon: '⚠️',
        duration: 3000,
      });
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Create a new chat if there isn't one
    let chatId = currentChatId;
    if (!chatId && user) {
      try {
        const userId = user.uid || user.id;
        const newChat = await agentApi.createChat(userId, inputValue.substring(0, 50));
        chatId = newChat.id;
        setCurrentChatId(chatId);
      } catch (error) {
        console.error('Failed to create chat:', error);
      }
    }

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
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
      const allMessages = [...updatedMessages, botMessage];
      setMessages(allMessages);
      
      // Save messages to chat history
      if (chatId) {
        await agentApi.updateChat(chatId, allMessages.map(msg => ({
          content: msg.content,
          type: msg.type,
          timestamp: msg.timestamp?.toISOString() || new Date().toISOString()
        })));
        // Trigger sidebar refresh to show updated chat with a slight delay
        setTimeout(() => {
          setRefreshSidebar(prev => prev + 1);
        }, 100);
      }
      
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

  const handleNewChat = () => {
    setMessages([]);
    setCurrentChatId(null);
    setInputValue('');

    // Close sidebar on mobile after starting new chat
    if (window.innerWidth <= 768) {
      setShowSidebar(false);
    }

    // Trigger sidebar refresh to show the new state
    setRefreshSidebar(prev => prev + 1);
    toast.success('New chat started', {
      icon: '✨',
      duration: 1500,
    });
  };

  const handleChatSelect = async (chatId) => {
    try {
      setIsLoading(true);
      const chat = await agentApi.getChat(chatId);
      if (chat && chat.messages) {
        setMessages(chat.messages.map((msg, index) => ({
          ...msg,
          id: index,
          timestamp: new Date(msg.timestamp)
        })));
        setCurrentChatId(chatId);

        // Close sidebar on mobile after selecting chat
        if (window.innerWidth <= 768) {
          setShowSidebar(false);
        }

        toast.success('Chat loaded', {
          icon: '📂',
          duration: 1000,
        });
      }
    } catch (error) {
      console.error('Error loading chat:', error);
      toast.error('Failed to load chat');
    } finally {
      setIsLoading(false);
    }
  };

  const clearHistory = async () => {
    handleNewChat();
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
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    
    // Update document class for consistent theming
    if (newDarkMode) {
      document.documentElement.classList.add('theme-dark');
      document.body.classList.add('theme-dark');
    } else {
      document.documentElement.classList.remove('theme-dark');
      document.body.classList.remove('theme-dark');
    }
    
    toast.success(`${darkMode ? 'Light' : 'Dark'} mode activated`, {
      icon: darkMode ? '☀️' : '🌙',
      duration: 2000,
    });
  };

  // Professional loading screen
  if (authLoading) {
    return (
      <div className="loading-screen">
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: darkMode ? '#1e293b' : '#ffffff',
              color: darkMode ? '#e2e8f0' : '#334155',
              border: `1px solid ${darkMode ? '#334155' : '#e2e8f0'}`,
              borderRadius: '8px',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            },
          }}
        />
        <div className="loading-content">
          <div className="mb-8">
            <Bot size={48} />
          </div>
          <h2>AI Business Assistant</h2>
          <p>Loading application...</p>
          <div className="loading-spinner" />
        </div>
      </div>
    );
  }

  // Auth form
  if (!isAuthenticated) {
    return <AuthForm onLogin={handleLogin} onRegister={handleRegister} isLoading={authLoading} />;
  }

  // Render Deep Learning Dashboard
  if (currentView === 'deeplearning') {
    return (
      <div className="modern-app">
        <Toaster 
          position="top-center"
          toastOptions={{
            duration: 3000,
            style: {
              background: darkMode ? '#2d3748' : '#ffffff',
              color: darkMode ? '#e2e8f0' : '#1a202c',
              border: `1px solid ${darkMode ? '#4a5568' : '#e2e8f0'}`,
              borderRadius: '8px',
              fontSize: '14px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            },
          }}
        />
        
        {/* Header for Deep Learning View */}
        <header className="modern-header">
          <div className="header-content">
            <button
              className="back-btn"
              onClick={() => setCurrentView('chat')}
            >
              <ChevronLeft size={20} />
              <span>Back to Chat</span>
            </button>
            
            <div className="header-title">
              <Brain size={24} />
              <h1>Analytics Dashboard</h1>
            </div>

            <div className="header-actions">
              <button
                className="header-action-btn"
                onClick={toggleDarkMode}
                title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {darkMode ? <Sun size={18} /> : <Moon size={18} />}
              </button>

              <button
                className="header-action-btn logout"
                onClick={handleLogout}
                title="Sign out"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </header>

        <DeepLearningDashboard />
      </div>
    );
  }

  return (
    <div className="modern-app">
      <Toaster 
        position="top-center"
        toastOptions={{
          duration: 3000,
          style: {
            background: darkMode ? '#2d3748' : '#ffffff',
            color: darkMode ? '#e2e8f0' : '#1a202c',
            border: `1px solid ${darkMode ? '#4a5568' : '#e2e8f0'}`,
            borderRadius: '8px',
            fontSize: '14px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          },
        }}
      />
      
      <div className="app-layout">
        {/* Mobile Overlay */}
        {showSidebar && (
          <div
            className="mobile-sidebar-overlay"
            onClick={() => setShowSidebar(false)}
          />
        )}

        {/* Chat Sidebar with History */}
        <ChatSidebar
          currentChatId={currentChatId}
          onChatSelect={handleChatSelect}
          onNewChat={handleNewChat}
          isCollapsed={!showSidebar}
          onToggleCollapse={() => setShowSidebar(!showSidebar)}
          user={user}
          refreshTrigger={refreshSidebar}
        />
        
        {/* Additional Sidebar Controls */}
        {showSidebar && (
          <div className="sidebar-extras">
            <div className="sidebar-footer">
              <button 
                className="sidebar-footer-btn"
                onClick={() => setCurrentView('deeplearning')}
              >
                <Brain size={16} />
                <span>Analytics</span>
              </button>
              <button 
                className="sidebar-footer-btn"
                onClick={() => setShowSettings(!showSettings)}
              >
                <Settings size={16} />
                <span>Settings</span>
              </button>
              <button 
                className="sidebar-footer-btn"
                onClick={toggleDarkMode}
              >
                {darkMode ? <Sun size={16} /> : <Moon size={16} />}
                <span>{darkMode ? 'Light' : 'Dark'}</span>
              </button>
            </div>
          </div>
        )}

        {/* Main Chat Area */}
        <main className="main-content">
          <div className="chat-header">
            <div className="chat-title">
              <button
                className="mobile-menu-btn action-btn"
                onClick={() => setShowSidebar(true)}
                title="Open sidebar"
              >
                <Menu size={20} />
              </button>
              <Bot size={24} className="chat-icon" />
              <div>
                <h1>AI Assistant</h1>
                <span className="status">Online • {user?.username}</span>
              </div>
            </div>

            <div className="chat-actions">
              <button
                className="action-btn"
                onClick={handleLogout}
                title="Sign out"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>

          <div className="messages-area">
            {messages.length === 0 && (
              <WelcomeMessage onExampleClick={setInputValue} />
            )}

            <div className="messages-container">
              {messages.map((message, index) => (
                <div key={message.id} className="message-wrapper">
                  <MessageRenderer message={message} />
                </div>
              ))}

              {isLoading && (
                <div className="message-wrapper">
                  <div className="assistant-message thinking">
                    <div className="message-avatar">
                      <Bot size={20} />
                    </div>
                    <div className="message-content">
                      <div className="thinking-indicator">
                        <div className="dot"></div>
                        <div className="dot"></div>
                        <div className="dot"></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <div className="input-container">
              <div className="input-wrapper">
                <textarea
                  className="message-input"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Message AI Assistant..."
                  rows={1}
                  disabled={isLoading}
                  onInput={(e) => {
                    e.target.style.height = 'auto';
                    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                  }}
                />
                <button
                  className="send-btn"
                  onClick={sendMessage}
                  disabled={!inputValue.trim() || isLoading}
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </div>
        </main>

        {/* Settings Panel */}
        {showSettings && (
          <div className="settings-overlay">
            <div className="settings-modal">
              <div className="settings-header">
                <h2>Settings</h2>
                <button
                  className="close-btn"
                  onClick={() => setShowSettings(false)}
                >
                  <X size={20} />
                </button>
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
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

