import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  User, Bot, Clock, ThumbsUp, ThumbsDown, Copy, Share2, 
  RotateCcw, AlertCircle, CheckCircle, Sparkles 
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { toast } from 'react-hot-toast';
import { AnimatePresence } from 'framer-motion';

const MessageRenderer = ({ message }) => {
  const [feedback, setFeedback] = useState(null);
  const [isHovered, setIsHovered] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      toast.success('Message copied to clipboard', {
        icon: '📋',
        duration: 2000,
      });
    } catch (error) {
      toast.error('Failed to copy message', {
        icon: '❌',
        duration: 2000,
      });
    }
  };

  const handleFeedback = (type) => {
    setFeedback(type);
    toast.success(`Feedback recorded: ${type}`, {
      icon: type === 'positive' ? '👍' : '👎',
      duration: 2000,
    });
  };

  const handleRegenerate = () => {
    toast.success('Regenerating response...', {
      icon: '🔄',
      duration: 2000,
    });
  };

  const getMessageIcon = () => {
    switch (message.type) {
      case 'user':
        return <User size={18} className="text-grey" />;
      case 'bot':
        return <Bot size={18} className="text-primary-600" />;
      case 'system':
        return <Sparkles size={18} className="text-warning-600" />;
      case 'error':
        return <AlertCircle size={18} className="text-error-600" />;
      default:
        return <Bot size={18} className="text-primary-600" />;
    }
  };

  const getMessageStyles = () => {
    switch (message.type) {
      case 'user':
        return 'bg-gradient-to-r from-primary-500 to-primary-600 text-grey ml-auto';
      case 'bot':
        return 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 mr-auto';
      case 'system':
        return 'bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800 mx-auto';
      case 'error':
        return 'bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 mr-auto';
      default:
        return 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 mr-auto';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <motion.div
      className={`flex ${message.type === 'user' ? 'justify-end' : message.type === 'system' ? 'justify-center' : 'justify-start'}`}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      <div className={`max-w-3xl w-full ${message.type === 'system' ? 'max-w-md' : ''}`}>
        <div className={`rounded-2xl p-4 shadow-lg ${getMessageStyles()} relative group`}>
          {/* Message Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <motion.div
                animate={{ rotate: message.type === 'bot' ? [0, 5, -5, 0] : 0 }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {getMessageIcon()}
              </motion.div>
              <span className={`text-sm font-medium ${
                message.type === 'user' ? 'text-grey' : 'text-gray-700 dark:text-gray-300'
              }`}>
                {message.type === 'user' ? 'You' : 
                 message.type === 'bot' ? 'AI Assistant' :
                 message.type === 'system' ? 'System' : 'Error'}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className={`flex items-center space-x-1 text-xs ${
                message.type === 'user' ? 'text-grey/70' : 'text-gray-500 dark:text-gray-400'
              }`}>
                <Clock size={12} />
                <span>{formatTimestamp(message.timestamp)}</span>
              </div>
            </div>
          </div>

          {/* Message Content */}
          <div className={`prose prose-sm max-w-none text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 ${
            message.type === 'user' ? 'prose-invert' : 'dark:prose-invert'
          }`}>
            {message.type === 'error' ? (
              <div className="flex items-start space-x-2">
                <AlertCircle size={16} className="text-error-600 mt-0.5 flex-shrink-0" />
                <div className="text-error-700 dark:text-error-300">
                  {message.content}
                </div>
              </div>
            ) : (
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <div className="relative">
                        <div className="flex items-center justify-between bg-gray-800 text-gray-300 px-4 py-2 text-xs rounded-t-lg">
                          <span>{match[1]}</span>
                          <motion.button
                            className="hover:bg-gray-700 p-1 rounded transition-colors"
                            onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <Copy size={12} />
                          </motion.button>
                        </div>
                        <SyntaxHighlighter
                          style={oneDark}
                          language={match[1]}
                          PreTag="div"
                          className="rounded-t-none"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      </div>
                    ) : (
                      <code className={`${className} bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-sm`} {...props}>
                        {children}
                      </code>
                    );
                  },
                  table: ({ children }) => (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        {children}
                      </table>
                    </div>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-4 border-primary-500 pl-4 italic text-gray-600 dark:text-gray-400">
                      {children}
                    </blockquote>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
          </div>

          {/* Message Actions */}
          <AnimatePresence>
            {(isHovered || feedback) && message.type !== 'system' && (
              <motion.div
                className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200/50 dark:border-gray-700/50"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.2 }}
              >
                <div className="flex items-center space-x-2">
                  <motion.button
                    className={`p-1.5 rounded-lg transition-colors ${
                      message.type === 'user' 
                        ? 'hover:bg-grey/20 text-grey/70 hover:text-grey' 
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                    }`}
                    onClick={handleCopy}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    title="Copy message"
                  >
                    <Copy size={14} />
                  </motion.button>

                  {message.type === 'bot' && (
                    <>
                      <motion.button
                        className={`p-1.5 rounded-lg transition-colors ${
                          feedback === 'positive' 
                            ? 'bg-success-100 text-success-600' 
                            : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                        }`}
                        onClick={() => handleFeedback('positive')}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        title="Good response"
                      >
                        <ThumbsUp size={14} />
                      </motion.button>

                      <motion.button
                        className={`p-1.5 rounded-lg transition-colors ${
                          feedback === 'negative' 
                            ? 'bg-error-100 text-error-600' 
                            : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                        }`}
                        onClick={() => handleFeedback('negative')}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        title="Poor response"
                      >
                        <ThumbsDown size={14} />
                      </motion.button>

                      <motion.button
                        className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors"
                        onClick={handleRegenerate}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        title="Regenerate response"
                      >
                        <RotateCcw size={14} />
                      </motion.button>
                    </>
                  )}
                </div>

                {message.metadata && (
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {message.metadata.agent && (
                      <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full">
                        {message.metadata.agent}
                      </span>
                    )}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Message Status Indicator */}
          {message.type === 'bot' && (
            <motion.div
              className="absolute -bottom-1 -right-1 w-6 h-6 bg-success-500 rounded-full flex items-center justify-center"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5, type: "spring", stiffness: 500 }}
            >
              <CheckCircle size={12} className="text-grey" />
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default MessageRenderer;

