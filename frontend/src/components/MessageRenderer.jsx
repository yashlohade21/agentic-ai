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
      toast.success('Copied to clipboard', {
        icon: '📋',
        duration: 2000,
      });
    } catch (error) {
      toast.error('Failed to copy', {
        icon: '❌',
        duration: 2000,
      });
    }
  };

  const handleFeedback = (type) => {
    setFeedback(type);
    toast.success(`Feedback: ${type}`, {
      icon: type === 'positive' ? '👍' : '👎',
      duration: 2000,
    });
  };

  const handleRegenerate = () => {
    toast('Regenerating...', {
      icon: '🔄',
      duration: 2000,
    });
  };

  const getMessageIcon = () => {
    switch (message.type) {
      case 'user':
        return <User className="w-3 h-3 md:w-4 md:h-4 lg:w-5 lg:h-5 text-grey" />;
      case 'bot':
        return <Bot className="w-3 h-3 md:w-4 md:h-4 lg:w-5 lg:h-5 text-primary-600" />;
      case 'system':
        return <Sparkles className="w-3 h-3 md:w-4 md:h-4 lg:w-5 lg:h-5 text-warning-600" />;
      case 'error':
        return <AlertCircle className="w-3 h-3 md:w-4 md:h-4 lg:w-5 lg:h-5 text-error-600" />;
      default:
        return <Bot className="w-3 h-3 md:w-4 md:h-4 lg:w-5 lg:h-5 text-primary-600" />;
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
      className={`flex ${message.type === 'user' ? 'justify-end' : message.type === 'system' ? 'justify-center' : 'justify-start'} px-2 md:px-3 lg:px-4`}
      initial={{ opacity: 0, y: 10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      onTouchStart={() => setIsHovered(true)}
      onTouchEnd={() => setTimeout(() => setIsHovered(false), 1000)}
    >
      <div className={`w-full ${message.type === 'system' ? 'max-w-xs sm:max-w-md' : 'max-w-full sm:max-w-2xl lg:max-w-3xl'}`}>
        <div className={`rounded-lg md:rounded-xl lg:rounded-2xl p-3 md:p-4 shadow-sm md:shadow-md lg:shadow-lg ${getMessageStyles()} relative group`}>
          {/* Message Header */}
          <div className="flex items-center justify-between mb-2 md:mb-3">
            <div className="flex items-center space-x-1 md:space-x-2">
              <motion.div
                animate={{ rotate: message.type === 'bot' ? [0, 5, -5, 0] : 0 }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {getMessageIcon()}
              </motion.div>
              <span className={`text-xs md:text-sm font-medium ${
                message.type === 'user' ? 'text-grey' : 'text-gray-700 dark:text-gray-300'
              }`}>
                {message.type === 'user' ? 'You' : 
                 message.type === 'bot' ? 'Binarybrained' :
                 message.type === 'system' ? 'System' : 'Error'}
              </span>
            </div>
            
            <div className="flex items-center space-x-1 md:space-x-2">
              <div className={`flex items-center space-x-0.5 md:space-x-1 text-[10px] md:text-xs ${
                message.type === 'user' ? 'text-grey/70' : 'text-gray-500 dark:text-gray-400'
              }`}>
                <Clock className="w-2.5 h-2.5 md:w-3 md:h-3 lg:w-4 lg:h-4" />
                <span>{formatTimestamp(message.timestamp)}</span>
              </div>
            </div>
          </div>

          {/* Message Content */}
          <div className={`prose 
            prose-xs    // Default for smallest screens (under 400px)
            xs:prose-sm // Extra small devices (400px and up)
            sm:prose-sm // Small devices (640px and up)
            md:prose-base // Medium devices (768px and up)
            lg:prose-lg // Large devices (1024px and up)
            xl:prose-xl // Extra large devices (1280px and up)
            2xl:prose-2xl // 2XL devices (1536px and up)
            max-w-none ${
              message.type === 'user' ? 'prose-invert' : 'dark:prose-invert'
            }`}>
            {message.type === 'error' ? (
              <div className="flex items-start gap-1 
                xs:gap-1.5
                sm:gap-2
                md:gap-2.5">
                <AlertCircle className="
                  w-2.5 h-2.5    // Default (under 400px)
                  xs:w-3 xs:h-3  // 400px+
                  sm:w-3.5 sm:h-3.5 // 640px+
                  md:w-4 md:h-4   // 768px+
                  lg:w-5 lg:h-5   // 1024px+
                  text-error-600 
                  mt-0.5 
                  flex-shrink-0" />
                <div className="text-error-700 dark:text-error-300 
                  text-xs      // Default (under 400px)
                  xs:text-xs   // 400px+
                  sm:text-sm   // 640px+
                  md:text-base // 768px+
                  lg:text-lg   // 1024px+">
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
                        <div className="flex items-center justify-between bg-gray-800 text-gray-300 
                          px-2 py-1      // Default (under 400px)
                          xs:px-2 xs:py-1 // 400px+
                          sm:px-3 sm:py-1.5 // 640px+
                          md:px-4 md:py-2 // 768px+
                          lg:px-5 lg:py-2.5 // 1024px+
                          text-[10px]     // Default
                          xs:text-[11px]  // 400px+
                          sm:text-xs      // 640px+
                          md:text-sm      // 768px+
                          rounded-t">
                          <span>{match[1]}</span>
                          <motion.button
                            className="hover:bg-gray-700 
                              p-0.5      // Default
                              sm:p-0.75  // 640px+
                              md:p-1     // 768px+
                              rounded transition-colors"
                            onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <Copy className="
                              w-2.5 h-2.5    // Default
                              xs:w-3 xs:h-3  // 400px+
                              sm:w-3.5 sm:h-3.5 // 640px+
                              md:w-4 md:h-4   // 768px+"/>
                          </motion.button>
                        </div>
                        <SyntaxHighlighter
                          style={oneDark}
                          language={match[1]}
                          PreTag="div"
                          className="
                            text-[10px]    // Default
                            xs:text-[11px] // 400px+
                            sm:text-xs     // 640px+
                            md:text-sm     // 768px+
                            lg:text-base   // 1024px+
                            rounded-t-none"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      </div>
                    ) : (
                      <code className={`${className} bg-gray-100 dark:bg-gray-700 
                        px-1 py-0.5      // Default
                        sm:px-1.5 sm:py-0.75 // 640px+
                        rounded 
                        text-xs          // Default
                        sm:text-sm       // 640px+
                        md:text-base     // 768px+`} 
                        {...props}>
                        {children}
                      </code>
                    );
                  },
                  table: ({ children }) => (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 
                        text-xs      // Default
                        sm:text-sm   // 640px+
                        md:text-base // 768px+">
                        {children}
                      </table>
                    </div>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="
                      border-l-2      // Default
                      sm:border-l-3   // 640px+
                      md:border-l-4    // 768px+
                      border-primary-500 
                      pl-2            // Default
                      sm:pl-3         // 640px+
                      md:pl-4         // 768px+
                      lg:pl-5         // 1024px+
                      italic 
                      text-gray-600 dark:text-gray-400 
                      text-xs        // Default
                      sm:text-sm      // 640px+
                      md:text-base    // 768px+">
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
                className="flex items-center justify-between mt-2 md:mt-3 pt-2 md:pt-3 border-t border-gray-200/50 dark:border-gray-700/50"
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 5 }}
                transition={{ duration: 0.15 }}
              >
                <div className="flex items-center space-x-1 md:space-x-2">
                  <motion.button
                    className={`p-1 md:p-1.5 rounded-md md:rounded-lg transition-colors ${
                      message.type === 'user' 
                        ? 'hover:bg-grey/20 text-grey/70 hover:text-grey' 
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                    }`}
                    onClick={handleCopy}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    title="Copy message"
                  >
                    <Copy className="w-2.5 h-2.5 md:w-3 md:h-3 lg:w-4 lg:h-4" />
                  </motion.button>

                  {message.type === 'bot' && (
                    <>
                      <motion.button
                        className={`p-1 md:p-1.5 rounded-md md:rounded-lg transition-colors ${
                          feedback === 'positive' 
                            ? 'bg-success-100 text-success-600' 
                            : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                        }`}
                        onClick={() => handleFeedback('positive')}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        title="Good response"
                      >
                        <ThumbsUp className="w-2.5 h-2.5 md:w-3 md:h-3 lg:w-4 lg:h-4" />
                      </motion.button>

                      <motion.button
                        className={`p-1 md:p-1.5 rounded-md md:rounded-lg transition-colors ${
                          feedback === 'negative' 
                            ? 'bg-error-100 text-error-600' 
                            : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                        }`}
                        onClick={() => handleFeedback('negative')}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        title="Poor response"
                      >
                        <ThumbsDown className="w-2.5 h-2.5 md:w-3 md:h-3 lg:w-4 lg:h-4" />
                      </motion.button>

                      <motion.button
                        className="p-1 md:p-1.5 rounded-md md:rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors"
                        onClick={handleRegenerate}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        title="Regenerate response"
                      >
                        <RotateCcw className="w-2.5 h-2.5 md:w-3 md:h-3 lg:w-4 lg:h-4" />
                      </motion.button>
                    </>
                  )}
                </div>

                {message.metadata && (
                  <div className="text-[10px] md:text-xs text-gray-500 dark:text-gray-400">
                    {message.metadata.agent && (
                      <span className="bg-gray-100 dark:bg-gray-700 px-1 md:px-1.5 lg:px-2 py-0.5 md:py-1 rounded-full">
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
              className="absolute -bottom-1 -right-1 w-3 h-3 md:w-4 md:h-4 lg:w-5 lg:h-5 bg-success-500 rounded-full flex items-center justify-center"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5, type: "spring", stiffness: 500 }}
            >
              <CheckCircle className="w-1.5 h-1.5 md:w-2 md:h-2 lg:w-3 lg:h-3 text-grey" />
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default MessageRenderer;