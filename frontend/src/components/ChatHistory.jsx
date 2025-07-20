import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { History, Trash2, RefreshCw, MessageSquare, User, Bot } from 'lucide-react';
import { toast } from 'react-hot-toast';

const ChatHistory = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [clearing, setClearing] = useState(false);

  const fetchChatHistory = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/chat/history?limit=50', {
        method: 'GET',
        credentials: 'include',
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setMessages(result.messages);
      } else {
        throw new Error(result.error || 'Failed to fetch chat history');
      }
    } catch (error) {
      toast.error(`Failed to load chat history: ${error.message}`, {
        icon: '❌',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const clearChatHistory = async () => {
    if (!window.confirm('Are you sure you want to clear all chat history? This action cannot be undone.')) {
      return;
    }

    setClearing(true);
    try {
      const response = await fetch('/api/chat/clear', {
        method: 'POST',
        credentials: 'include',
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setMessages([]);
        toast.success(`Cleared ${result.deleted_count} messages`, {
          icon: '✅',
          duration: 3000,
        });
      } else {
        throw new Error(result.error || 'Failed to clear chat history');
      }
    } catch (error) {
      toast.error(`Failed to clear chat history: ${error.message}`, {
        icon: '❌',
        duration: 3000,
      });
    } finally {
      setClearing(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchChatHistory();
    }
  }, [isOpen]);

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getSenderIcon = (sender) => {
    return sender === 'user' ? <User size={16} /> : <Bot size={16} />;
  };

  const getSenderColor = (sender) => {
    return sender === 'user' ? 'text-blue-600' : 'text-purple-600';
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <History size={24} />
                <h2 className="text-xl font-semibold">Chat History</h2>
              </div>
              <div className="flex items-center gap-2">
                <motion.button
                  className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  onClick={fetchChatHistory}
                  disabled={loading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title="Refresh"
                >
                  <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                </motion.button>
                <motion.button
                  className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  onClick={clearChatHistory}
                  disabled={clearing || messages.length === 0}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title="Clear History"
                >
                  <Trash2 size={18} className={clearing ? 'animate-pulse' : ''} />
                </motion.button>
                <motion.button
                  className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  onClick={onClose}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title="Close"
                >
                  ✕
                </motion.button>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-4 overflow-y-auto max-h-[60vh]">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                <span className="ml-3 text-gray-600">Loading chat history...</span>
              </div>
            ) : messages.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">No chat history found</p>
                <p className="text-sm">Start a conversation to see your messages here</p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <motion.div
                    key={message.id || index}
                    className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`flex-shrink-0 ${getSenderColor(message.sender)}`}>
                        {getSenderIcon(message.sender)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`font-medium ${getSenderColor(message.sender)}`}>
                            {message.sender === 'user' ? 'You' : 'BinaryBrained'}
                          </span>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(message.timestamp)}
                          </span>
                        </div>
                        <div className="text-gray-800 whitespace-pre-wrap break-words">
                          {message.content}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-4 py-3 border-t">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>
                {messages.length > 0 ? `${messages.length} messages` : 'No messages'}
              </span>
              <span>
                Press ESC to close
              </span>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ChatHistory;

