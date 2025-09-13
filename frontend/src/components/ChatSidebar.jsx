import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, Plus, Search, MoreHorizontal, Trash2, Edit2, 
  ChevronDown, ChevronRight, Calendar, Clock, Menu, X, RefreshCw
} from 'lucide-react';
import { agentApi } from '../api/agentApi';
import { toast } from 'react-hot-toast';
import './ChatSidebar.css';

const ChatSidebar = ({ 
  currentChatId, 
  onChatSelect, 
  onNewChat,
  isCollapsed,
  onToggleCollapse,
  user,
  refreshTrigger 
}) => {
  const [chats, setChats] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false); // Start with false
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState(null);
  const [groupedChats, setGroupedChats] = useState({
    today: [],
    yesterday: [],
    thisWeek: [],
    thisMonth: [],
    older: []
  });

  // Test function to check the API
  const testAPI = async () => {
    try {
      const userId = user?.uid || user?.id;
      console.log('Testing API with user ID:', userId);
      
      const response = await fetch(`http://localhost:5000/api/chats/user/${userId}`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('API Response status:', response.status);
      const data = await response.json();
      console.log('API Response data:', data);
    } catch (error) {
      console.error('Direct API test failed:', error);
    }
  };

  useEffect(() => {
    if (user && (user.uid || user.id)) {
      console.log('User detected:', user);
      console.log('Loading chats for user:', user.uid || user.id);
      
      // Test the API directly first
      testAPI();
      
      loadChats();
    } else {
      console.log('No user found, cannot load chats');
      setLoading(false);
      setHasLoaded(true);
    }
  }, [user, refreshTrigger]);

  const loadChats = async () => {
    if (loading) return; // Prevent multiple simultaneous loads
    
    try {
      setLoading(true);
      setError(null);
      
      const userId = user?.uid || user?.id;
      if (!userId) {
        console.error('No user ID available');
        setError('User not authenticated');
        setChats([]);
        setLoading(false);
        setHasLoaded(true);
        return;
      }
      
      console.log('Fetching chat history for user ID:', userId);
      
      const response = await agentApi.getChatHistory(userId);
      console.log('Chat history API response:', response);
      
      if (response && response.chats) {
        console.log(`Loaded ${response.chats.length} chats`);
        setChats(response.chats);
        groupChatsByDate(response.chats);
      } else {
        console.log('No chats found in response');
        setChats([]);
        setGroupedChats({
          today: [],
          yesterday: [],
          thisWeek: [],
          thisMonth: [],
          older: []
        });
      }
      setHasLoaded(true);
    } catch (error) {
      console.error('Error loading chats:', error);
      
      // Try to provide some mock data for testing
      if (process.env.NODE_ENV === 'development') {
        const mockChats = [
          {
            id: 'mock-1',
            title: 'Sample Chat 1',
            preview: 'This is a sample chat for testing...',
            lastUpdated: new Date().toISOString(),
            createdAt: new Date().toISOString()
          },
          {
            id: 'mock-2',
            title: 'Sample Chat 2',
            preview: 'Another sample chat...',
            lastUpdated: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
          }
        ];
        
        console.log('Using mock data for development');
        setChats(mockChats);
        groupChatsByDate(mockChats);
        setError(null);
      } else {
        setError(error.message || 'Failed to load chat history');
        
        // Don't show error toast on first load, only on refresh
        if (hasLoaded) {
          toast.error('Failed to load chat history');
        }
        
        setChats([]);
      }
      
      setHasLoaded(true);
    } finally {
      setLoading(false);
    }
  };

  const groupChatsByDate = (chatList) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);
    const monthAgo = new Date(today);
    monthAgo.setMonth(monthAgo.getMonth() - 1);

    const grouped = {
      today: [],
      yesterday: [],
      thisWeek: [],
      thisMonth: [],
      older: []
    };

    chatList.forEach(chat => {
      const chatDate = new Date(chat.lastUpdated || chat.createdAt);
      
      if (chatDate >= today) {
        grouped.today.push(chat);
      } else if (chatDate >= yesterday) {
        grouped.yesterday.push(chat);
      } else if (chatDate >= weekAgo) {
        grouped.thisWeek.push(chat);
      } else if (chatDate >= monthAgo) {
        grouped.thisMonth.push(chat);
      } else {
        grouped.older.push(chat);
      }
    });

    setGroupedChats(grouped);
  };

  const filteredChats = searchQuery
    ? chats.filter(chat => 
        chat.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        chat.preview?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : chats;

  const deleteChat = async (chatId, e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this chat?')) {
      try {
        await agentApi.deleteChat(chatId);
        
        // Remove the chat from the local state immediately
        const updatedChats = chats.filter(c => c.id !== chatId);
        setChats(updatedChats);
        
        // Re-group the remaining chats
        groupChatsByDate(updatedChats);
        
        toast.success('Chat deleted successfully', {
          icon: '🗑️',
          duration: 2000,
        });
        
        // If the deleted chat was currently selected, start a new chat
        if (currentChatId === chatId) {
          onNewChat();
        }
        
        // Optionally reload all chats to ensure consistency
        setTimeout(() => {
          loadChats();
        }, 500);
      } catch (error) {
        console.error('Error deleting chat:', error);
        toast.error('Failed to delete chat');
        // Reload chats to restore correct state
        loadChats();
      }
    }
  };

  const renameChat = async (chatId, currentTitle, e) => {
    e.stopPropagation();
    const newTitle = prompt('Enter new title:', currentTitle);
    if (newTitle && newTitle !== currentTitle) {
      try {
        await agentApi.updateChatTitle(chatId, newTitle);
        
        // Update the chat title in local state
        const updatedChats = chats.map(c => 
          c.id === chatId ? { ...c, title: newTitle } : c
        );
        setChats(updatedChats);
        
        // Re-group chats to maintain organization
        groupChatsByDate(updatedChats);
        
        toast.success('Chat renamed successfully', {
          icon: '✏️',
          duration: 2000,
        });
      } catch (error) {
        console.error('Error renaming chat:', error);
        toast.error('Failed to rename chat');
        // Reload chats to restore correct state
        loadChats();
      }
    }
  };

  const ChatItem = ({ chat }) => {
    const [showMenu, setShowMenu] = useState(false);
    const [isTouched, setIsTouched] = useState(false);
    const isActive = currentChatId === chat.id;

    // Handle touch devices - show menu on touch/active state
    const handleTouchStart = (e) => {
      e.stopPropagation();
      setIsTouched(true);
      setShowMenu(true);
    };

    const handleTouchEnd = () => {
      // Keep menu visible for a moment on touch devices
      setTimeout(() => {
        setIsTouched(false);
        if (!isActive) setShowMenu(false);
      }, 100);
    };

    // Show menu on hover for desktop, always for active item, or when touched
    const shouldShowMenu = !isCollapsed && (showMenu || isActive || isTouched);

    return (
      <div
        className={`chat-item ${isActive ? 'active' : ''} ${shouldShowMenu ? 'show-menu' : ''}`}
        onClick={() => onChatSelect(chat.id)}
        onMouseEnter={() => setShowMenu(true)}
        onMouseLeave={() => !isTouched && setShowMenu(false)}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        <MessageSquare size={16} className="chat-item-icon" />
        <div className="chat-item-content">
          <div className="chat-item-title">{chat.title || 'New Chat'}</div>
          {!isCollapsed && chat.preview && (
            <div className="chat-item-preview">{chat.preview}</div>
          )}
        </div>
        {shouldShowMenu && (
          <div className="chat-item-menu">
            <button
              className="chat-menu-btn"
              onClick={(e) => {
                e.stopPropagation();
                renameChat(chat.id, chat.title, e);
              }}
              title="Rename"
            >
              <Edit2 size={14} />
            </button>
            <button
              className="chat-menu-btn delete"
              onClick={(e) => {
                e.stopPropagation();
                deleteChat(chat.id, e);
              }}
              title="Delete"
            >
              <Trash2 size={14} />
            </button>
          </div>
        )}
      </div>
    );
  };

  const ChatGroup = ({ title, chats, icon }) => {
    const [isExpanded, setIsExpanded] = useState(true);

    if (chats.length === 0) return null;

    return (
      <div className="chat-group">
        {!isCollapsed && (
          <div 
            className="chat-group-header"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <div className="chat-group-title">
              {icon}
              <span>{title}</span>
            </div>
            {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </div>
        )}
        {isExpanded && (
          <div className="chat-group-items">
            {chats.map(chat => (
              <ChatItem key={chat.id} chat={chat} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <aside className={`claude-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button 
          className="sidebar-toggle-btn"
          onClick={onToggleCollapse}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <Menu size={20} /> : <X size={20} />}
        </button>
        {!isCollapsed && (
          <>
            <button className="new-chat-btn" onClick={onNewChat} title="Start a new chat">
              <Plus size={18} />
              <span>New chat</span>
            </button>
            <button 
              className="refresh-btn"
              onClick={loadChats}
              disabled={loading}
              title="Refresh chat list"
            >
              <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            </button>
          </>
        )}
      </div>

      {!isCollapsed && (
        <div className="sidebar-search">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
      )}

      <div className="sidebar-chats">
        {loading && !hasLoaded ? (
          <div className="loading-state">
            <div className="loading-spinner" />
            <p className="loading-text">Loading chats...</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <MessageSquare size={32} />
            <p className="error-message">{error}</p>
            <button className="retry-btn" onClick={loadChats}>
              <RefreshCw size={16} />
              <span>Retry</span>
            </button>
          </div>
        ) : searchQuery ? (
          <div className="search-results">
            {filteredChats.length > 0 ? (
              filteredChats.map(chat => (
                <ChatItem key={chat.id} chat={chat} />
              ))
            ) : (
              <div className="empty-search">
                No chats found
              </div>
            )}
          </div>
        ) : (
          <>
            <ChatGroup 
              title="Today" 
              chats={groupedChats.today}
              icon={<Calendar size={14} />}
            />
            <ChatGroup 
              title="Yesterday" 
              chats={groupedChats.yesterday}
              icon={<Clock size={14} />}
            />
            <ChatGroup 
              title="Previous 7 Days" 
              chats={groupedChats.thisWeek}
              icon={<Calendar size={14} />}
            />
            <ChatGroup 
              title="Previous Month" 
              chats={groupedChats.thisMonth}
              icon={<Calendar size={14} />}
            />
            <ChatGroup 
              title="Older" 
              chats={groupedChats.older}
              icon={<Clock size={14} />}
            />
          </>
        )}

        {!loading && hasLoaded && chats.length === 0 && !searchQuery && !error && (
          <div className="empty-state">
            <MessageSquare size={32} />
            <p>No conversations yet</p>
            <button className="start-chat-btn" onClick={onNewChat}>
              Start a new chat
            </button>
          </div>
        )}
      </div>
    </aside>
  );
};

export default ChatSidebar;