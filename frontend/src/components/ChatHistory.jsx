import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  History, Search, Trash2, MessageSquare, Clock, 
  User, Bot, ChevronRight, RefreshCw, Calendar,
  Filter, X, Download, Archive
} from 'lucide-react';
import { toast } from 'react-hot-toast';

const ChatHistory = ({ onClose, onSelectConversation }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  const filters = [
    { id: 'all', label: 'All Conversations', icon: MessageSquare },
    { id: 'today', label: 'Today', icon: Clock },
    { id: 'week', label: 'This Week', icon: Calendar },
    { id: 'month', label: 'This Month', icon: Archive }
  ];

  useEffect(() => {
    loadConversations();
  }, [selectedFilter]);

  useEffect(() => {
    if (searchQuery.trim()) {
      performSearch();
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/chat-history/conversations', {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to load conversations');
      }

      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (error) {
      console.error('Error loading conversations:', error);
      toast.error('Failed to load chat history');
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  const performSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setSearching(true);
      const response = await fetch(`/api/chat-history/search?q=${encodeURIComponent(searchQuery)}`, {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setSearchResults(data.messages || []);
    } catch (error) {
      console.error('Error searching:', error);
      toast.error('Search failed');
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const clearHistory = async () => {
    if (!window.confirm('Are you sure you want to clear all chat history? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch('/api/chat-history/clear', {
        method: 'POST',
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to clear history');
      }

      const data = await response.json();
      toast.success(`Cleared ${data.deleted_messages} messages`);
      setConversations([]);
      setSearchResults([]);
      setSearchQuery('');
    } catch (error) {
      console.error('Error clearing history:', error);
      toast.error('Failed to clear history');
    }
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString();
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getFilteredConversations = () => {
    if (searchQuery.trim()) return [];

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

    return conversations.filter(conv => {
      const convDate = new Date(conv.start_time);
      
      switch (selectedFilter) {
        case 'today':
          return convDate >= today;
        case 'week':
          return convDate >= weekAgo;
        case 'month':
          return convDate >= monthAgo;
        default:
          return true;
      }
    });
  };

  const displayItems = searchQuery.trim() ? searchResults : getFilteredConversations();

  return (
    <motion.div
      className="chat-history-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={(e) => e.target === e.currentTarget && onClose?.()}
    >
      <motion.div
        className="chat-history-modal"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ type: "spring", damping: 20 }}
      >
        {/* Header */}
        <div className="modal-header">
          <div className="header-title">
            <History size={24} />
            <h2>Chat History</h2>
          </div>
          <div className="header-actions">
            <motion.button
              className="action-btn"
              onClick={() => setShowFilters(!showFilters)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Filter size={18} />
            </motion.button>
            <motion.button
              className="action-btn"
              onClick={loadConversations}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RefreshCw size={18} />
            </motion.button>
            <motion.button
              className="action-btn danger"
              onClick={clearHistory}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Trash2 size={18} />
            </motion.button>
            <motion.button
              className="close-btn"
              onClick={onClose}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <X size={20} />
            </motion.button>
          </div>
        </div>

        {/* Filters */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              className="filters-section"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <div className="filters-list">
                {filters.map((filter) => (
                  <motion.button
                    key={filter.id}
                    className={`filter-btn ${selectedFilter === filter.id ? 'active' : ''}`}
                    onClick={() => setSelectedFilter(filter.id)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <filter.icon size={16} />
                    <span>{filter.label}</span>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Search */}
        <div className="search-section">
          <div className="search-input-container">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            {searchQuery && (
              <motion.button
                className="clear-search-btn"
                onClick={() => setSearchQuery('')}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <X size={16} />
              </motion.button>
            )}
          </div>
          {searching && (
            <div className="search-status">
              <RefreshCw size={16} className="spinning" />
              <span>Searching...</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="modal-content">
          {loading ? (
            <div className="loading-state">
              <RefreshCw size={32} className="spinning" />
              <p>Loading chat history...</p>
            </div>
          ) : displayItems.length === 0 ? (
            <div className="empty-state">
              <MessageSquare size={48} />
              <h3>
                {searchQuery.trim() 
                  ? 'No matching conversations found' 
                  : 'No conversations yet'}
              </h3>
              <p>
                {searchQuery.trim() 
                  ? 'Try adjusting your search terms' 
                  : 'Start chatting to see your conversation history here'}
              </p>
            </div>
          ) : (
            <div className="conversations-list">
              <AnimatePresence>
                {displayItems.map((item, index) => (
                  <motion.div
                    key={searchQuery.trim() ? item.id : item.id}
                    className="conversation-item"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => {
                      if (searchQuery.trim()) {
                        // For search results, we might want to highlight the message
                        onSelectConversation?.(item);
                      } else {
                        // For conversations, load the full conversation
                        onSelectConversation?.(item);
                      }
                      onClose?.();
                    }}
                    whileHover={{ scale: 1.01, x: 4 }}
                    whileTap={{ scale: 0.99 }}
                  >
                    {searchQuery.trim() ? (
                      // Search result item
                      <div className="search-result-content">
                        <div className="message-header">
                          <div className="sender-info">
                            {item.sender === 'user' ? (
                              <User size={16} className="user-icon" />
                            ) : (
                              <Bot size={16} className="bot-icon" />
                            )}
                            <span className="sender-label">
                              {item.sender === 'user' ? 'You' : 'AI'}
                            </span>
                          </div>
                          <span className="message-time">
                            {formatDate(item.timestamp)} at {formatTime(item.timestamp)}
                          </span>
                        </div>
                        <div className="message-content">
                          {item.content}
                        </div>
                      </div>
                    ) : (
                      // Conversation item
                      <div className="conversation-content">
                        <div className="conversation-header">
                          <h4 className="conversation-title">{item.title}</h4>
                          <div className="conversation-meta">
                            <span className="message-count">
                              {item.message_count} messages
                            </span>
                            <span className="conversation-date">
                              {formatDate(item.start_time)}
                            </span>
                          </div>
                        </div>
                        <div className="conversation-preview">
                          {item.preview}
                        </div>
                        <div className="conversation-stats">
                          <div className="stat">
                            <User size={14} />
                            <span>{item.user_messages}</span>
                          </div>
                          <div className="stat">
                            <Bot size={14} />
                            <span>{item.bot_messages}</span>
                          </div>
                          <div className="conversation-time">
                            {formatTime(item.last_time)}
                          </div>
                        </div>
                      </div>
                    )}
                    <ChevronRight size={16} className="chevron-icon" />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <div className="footer-stats">
            {!searchQuery.trim() && (
              <span>
                {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
              </span>
            )}
            {searchQuery.trim() && (
              <span>
                {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} for "{searchQuery}"
              </span>
            )}
          </div>
          <div className="footer-actions">
            <motion.button
              className="btn btn-secondary"
              onClick={onClose}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Close
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ChatHistory;

