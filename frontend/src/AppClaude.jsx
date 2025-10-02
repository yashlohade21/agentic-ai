import React, { useState, useEffect, useRef, lazy, Suspense, useCallback, useMemo } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import {
  Bot, Menu, Settings, Sun, Moon, LogOut, Send, User, Plus, Search
} from 'lucide-react';
import { agentApi } from './api/agentApi';
import './Claude.css';

// Lazy load heavy components
const AuthForm = lazy(() => import('./components/AuthForm'));
const ChatSidebar = lazy(() => import('./components/ChatSidebar'));
const MessageRenderer = lazy(() => import('./components/MessageRenderer'));
const AgentStatus = lazy(() => import('./components/AgentStatus'));
const ChatInput = lazy(() => import('./components/ChatInput'));

// Simple loading placeholder
const ComponentLoader = () => (
  <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
    <div className="loading-spinner" />
  </div>
);

function AppClaude() {
  // Auth State
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  
  // Chat State
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // UI State
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [systemStatus, setSystemStatus] = useState({
    status: 'active',
    agents: [],
    session_requests: 0
  });
  
  const messagesEndRef = useRef(null);

  // Scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize auth and dark mode
  useEffect(() => {
    checkAuthStatus();
    
    const savedDarkMode = localStorage.getItem('darkMode');
    const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldUseDarkMode = savedDarkMode ? JSON.parse(savedDarkMode) : systemDarkMode;
    
    setDarkMode(shouldUseDarkMode);
    if (shouldUseDarkMode) {
      document.documentElement.classList.add('theme-dark');
    }
  }, []);

  // Save dark mode preference
  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('theme-dark');
    } else {
      document.documentElement.classList.remove('theme-dark');
    }
  }, [darkMode]);

  // Check backend connection when authenticated (debounced) - REMOVED to improve performance
  // The connection will be checked on first message send instead

  const checkAuthStatus = async () => {
    try {
      const authStatus = await agentApi.checkAuth();
      if (authStatus.authenticated) {
        setUser(authStatus.user);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.log('Auth check failed:', error);
    } finally {
      setAuthLoading(false);
    }
  };

  const checkBackendConnection = async () => {
    try {
      // Use a timeout to fail fast if backend is slow
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const health = await agentApi.healthCheck();
      clearTimeout(timeoutId);

      if (health.status === 'ok') {
        setConnectionStatus('connected');
        // Load system status in background, don't block
        agentApi.getSystemStatus()
          .then(status => setSystemStatus(status))
          .catch(() => {}); // Silent fail for system status
      }
    } catch (error) {
      setConnectionStatus('mock');
      // Don't show error toast on initial load - it's annoying
      if (import.meta.env.DEV) {
        console.warn('Backend connection failed, using offline mode');
      }
    }
  };

  const handleLogin = useCallback(async (credentials) => {
    try {
      const response = await agentApi.login(credentials);
      setUser(response.user);
      setIsAuthenticated(true);
      toast.success(`Welcome back, ${response.user.username}!`);
      return response;
    } catch (error) {
      throw error;
    }
  }, []);

  const handleRegister = useCallback(async (userData) => {
    try {
      const response = await agentApi.register(userData);
      setUser(response.user);
      setIsAuthenticated(true);
      toast.success(`Welcome, ${response.user.username}!`);
      return response;
    } catch (error) {
      throw error;
    }
  }, []);

  const handleLogout = useCallback(async () => {
    try {
      await agentApi.logout();
      setUser(null);
      setIsAuthenticated(false);
      setMessages([]);
      setCurrentChatId(null);
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      setUser(null);
      setIsAuthenticated(false);
    }
  }, []);

  const handleNewChat = useCallback(async () => {
    // Save current chat if it has messages
    if (currentChatId && messages.length > 0) {
      await saveCurrentChat();
    }

    // Create new chat
    try {
      const newChat = await agentApi.createChat(user.uid || user.id, 'New Chat');
      setCurrentChatId(newChat.id);
      setMessages([]);
      setInputValue('');
    } catch (error) {
      console.error('Error creating new chat:', error);
      // Still clear for new chat even if save fails
      setCurrentChatId(null);
      setMessages([]);
      setInputValue('');
    }
  }, [currentChatId, messages, user]);

  const handleChatSelect = async (chatId) => {
    // Save current chat before switching
    if (currentChatId && messages.length > 0) {
      await saveCurrentChat();
    }
    
    // Load selected chat
    try {
      const chat = await agentApi.getChat(chatId);
      setCurrentChatId(chatId);
      setMessages(chat.messages || []);
    } catch (error) {
      console.error('Error loading chat:', error);
      toast.error('Failed to load chat');
    }
  };

  const saveCurrentChat = async () => {
    if (!currentChatId || messages.length === 0) return;
    
    try {
      await agentApi.updateChat(currentChatId, messages);
    } catch (error) {
      console.error('Error saving chat:', error);
    }
  };

  const sendMessage = async (attachedFiles = []) => {
    if ((!inputValue.trim() && attachedFiles.length === 0) || isLoading) return;

    // Create chat if doesn't exist
    if (!currentChatId && user) {
      try {
        const newChat = await agentApi.createChat(
          user.uid || user.id,
          inputValue.substring(0, 50) || 'New Chat'
        );
        setCurrentChatId(newChat.id);
      } catch (error) {
        console.error('Error creating chat:', error);
      }
    }

    // Prepare message content with files
    let messageContent = inputValue;
    if (attachedFiles.length > 0) {
      const fileDescriptions = attachedFiles.map(file =>
        `[Attached: ${file.original_name} (${file.file_type})]`
      ).join('\n');
      messageContent = messageContent ? `${messageContent}\n\n${fileDescriptions}` : fileDescriptions;
    }

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageContent,
      attachedFiles: attachedFiles,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await agentApi.sendMessage(currentInput);
      const botMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        metadata: response.metadata
      };

      const updatedMessages = [...messages, userMessage, botMessage];
      setMessages(updatedMessages);

      // Save chat with new messages
      if (currentChatId) {
        await agentApi.updateChat(currentChatId, updatedMessages);
      }

    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      toast.error('Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (file) => {
    console.log('File uploaded:', file);
    toast.success(`File uploaded: ${file.original_name}`);
  };

  const handleFileAnalyze = (file, analysis) => {
    const botMessage = {
      id: Date.now(),
      type: 'assistant',
      content: `**Analysis of ${file.original_name}:**\n\n${analysis}`,
      timestamp: new Date().toISOString(),
      metadata: {
        analyzed_file: file.original_name,
        file_type: file.file_type
      }
    };

    setMessages(prev => [...prev, botMessage]);
    toast.success('File analysis completed!', {
      icon: '🔍',
      duration: 3000,
    });
  };


  const refreshSystem = useCallback(async () => {
    setIsLoading(true);
    try {
      await checkBackendConnection();
      toast.success('System refreshed');
    } catch (error) {
      toast.error('Failed to refresh system');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Loading screen
  if (authLoading) {
    return (
      <div className="claude-app">
        <Toaster position="top-center" />
        <div className="loading-state">
          <div className="loading-spinner" />
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Auth screen
  if (!isAuthenticated) {
    return (
      <Suspense fallback={<div className="loading-state"><div className="loading-spinner" /><p>Loading...</p></div>}>
        <AuthForm onLogin={handleLogin} onRegister={handleRegister} isLoading={authLoading} />
      </Suspense>
    );
  }

  return (
    <div className="claude-app">
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            background: darkMode ? '#343541' : '#ffffff',
            color: darkMode ? '#ececf1' : '#202123',
            border: `1px solid ${darkMode ? '#565869' : '#e5e5e5'}`,
          },
        }}
      />

      {/* Sidebar */}
      <Suspense fallback={<ComponentLoader />}>
        <ChatSidebar
          currentChatId={currentChatId}
          onChatSelect={handleChatSelect}
          onNewChat={handleNewChat}
          isCollapsed={!sidebarOpen}
          onToggleCollapse={() => setSidebarOpen(!sidebarOpen)}
          user={user}
        />
      </Suspense>
      
      {/* Main Chat Area */}
      <main className="claude-main">
        {/* Header */}
        <header className="claude-header">
          <div className="header-left">
            <button
              className="sidebar-toggle-btn"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <Menu size={20} />
            </button>
            <h1 className="header-title">AI Assistant</h1>
          </div>
          
          <div className="header-actions">
            <button
              className="header-btn"
              onClick={() => setDarkMode(!darkMode)}
              title={darkMode ? 'Light mode' : 'Dark mode'}
            >
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button
              className="header-btn"
              onClick={() => setShowSettings(!showSettings)}
              title="Settings"
            >
              <Settings size={18} />
            </button>
            <button
              className="header-btn"
              onClick={handleLogout}
              title="Sign out"
            >
              <LogOut size={18} />
            </button>
          </div>
        </header>
        
        {/* Messages Area */}
        <div className="claude-messages">
          <div className="messages-scroll-container">
            {messages.length === 0 ? (
              <div className="claude-welcome">
                <div className="welcome-logo">
                  <Bot size={32} color="white" />
                </div>
                <h2 className="welcome-title">How can I help you today?</h2>
                <p className="welcome-subtitle">Ask me anything or try one of these examples</p>
                
                <div className="example-prompts-grid">
                  <div 
                    className="example-prompt-card"
                    onClick={() => setInputValue("Explain quantum computing in simple terms")}
                  >
                    <div className="example-prompt-title">Learn</div>
                    <div className="example-prompt-text">Explain quantum computing in simple terms</div>
                  </div>
                  <div 
                    className="example-prompt-card"
                    onClick={() => setInputValue("Write a Python function to sort a list")}
                  >
                    <div className="example-prompt-title">Code</div>
                    <div className="example-prompt-text">Write a Python function to sort a list</div>
                  </div>
                  <div 
                    className="example-prompt-card"
                    onClick={() => setInputValue("Help me brainstorm ideas for a startup")}
                  >
                    <div className="example-prompt-title">Create</div>
                    <div className="example-prompt-text">Help me brainstorm ideas for a startup</div>
                  </div>
                  <div 
                    className="example-prompt-card"
                    onClick={() => setInputValue("What are the latest AI trends?")}
                  >
                    <div className="example-prompt-title">Explore</div>
                    <div className="example-prompt-text">What are the latest AI trends?</div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="messages-list">
                {messages.map((message) => (
                  <div key={message.id} className={`message-row ${message.type}`}>
                    <div className={`message-avatar ${message.type}`}>
                      {message.type === 'user' ? <User size={16} /> : <Bot size={16} />}
                    </div>
                    <div className="message-content-wrapper">
                      <Suspense fallback={<div className="loading-spinner" />}>
                        <MessageRenderer message={message} />
                      </Suspense>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="message-row assistant">
                    <div className="message-avatar assistant">
                      <Bot size={16} />
                    </div>
                    <div className="message-content-wrapper">
                      <div className="thinking-dots">
                        <div className="thinking-dot" />
                        <div className="thinking-dot" />
                        <div className="thinking-dot" />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
        
        {/* Input Area */}
        <Suspense fallback={<ComponentLoader />}>
          <ChatInput
            inputValue={inputValue}
            setInputValue={setInputValue}
            onSendMessage={sendMessage}
            isLoading={isLoading}
            onFileUpload={handleFileUpload}
            onFileAnalyze={handleFileAnalyze}
          />
        </Suspense>
      </main>
      
      {/* Settings Modal */}
      {showSettings && (
        <div className="settings-modal-overlay" onClick={() => setShowSettings(false)}>
          <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
            <div className="settings-header">
              <h2 className="settings-title">Settings</h2>
              <button
                className="settings-close"
                onClick={() => setShowSettings(false)}
              >
                ×
              </button>
            </div>
            <div className="settings-content">
              <Suspense fallback={<ComponentLoader />}>
                <AgentStatus
                  systemStatus={systemStatus}
                  connectionStatus={connectionStatus}
                  user={user}
                  onRefresh={refreshSystem}
                  onClearHistory={handleNewChat}
                  onLogout={handleLogout}
                  onToggleDarkMode={() => setDarkMode(!darkMode)}
                  darkMode={darkMode}
                  isLoading={isLoading}
                />
              </Suspense>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AppClaude;