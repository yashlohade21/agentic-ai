import React, { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Mic, Paperclip, Smile, Zap } from 'lucide-react';
import { toast } from 'react-hot-toast';

const ChatInput = ({ inputValue, setInputValue, onSendMessage, isLoading, onKeyPress }) => {
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [inputValue]);

  const handleVoiceInput = () => {
    toast.success('Voice input coming soon!', {
      icon: '🎤',
      duration: 2000,
    });
  };

  const handleFileAttach = () => {
    toast.success('File attachment coming soon!', {
      icon: '📎',
      duration: 2000,
    });
  };

  const handleEmojiPicker = () => {
    toast.success('Emoji picker coming soon!', {
      icon: '😊',
      duration: 2000,
    });
  };

  const quickPrompts = [
    "Explain this concept",
    "Write code for",
    "Help me with",
    "Analyze this"
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Quick Prompts */}
      <motion.div 
        className="flex flex-wrap gap-2 mb-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {quickPrompts.map((prompt, index) => (
          <motion.button
            key={prompt}
            className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            onClick={() => setInputValue(prompt + " ")}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Zap size={12} className="inline mr-1" />
            {prompt}
          </motion.button>
        ))}
      </motion.div>

      {/* Main Input Container */}
      <motion.div
        className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        whileFocusWithin={{ 
          boxShadow: "0 0 0 3px rgba(99, 102, 241, 0.1)",
          borderColor: "rgb(99, 102, 241)"
        }}
      >
        {/* Input Area */}
        <div className="flex items-end p-4 space-x-3">
          {/* Action Buttons Left */}
          <div className="flex space-x-2">
            <motion.button
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              onClick={handleFileAttach}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Attach file"
            >
              <Paperclip size={18} />
            </motion.button>
            
            <motion.button
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              onClick={handleEmojiPicker}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Add emoji"
            >
              <Smile size={18} />
            </motion.button>
          </div>

          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={onKeyPress}
              placeholder="Type your message here..."
              className="w-full resize-none border-none outline-none bg-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-base leading-6 max-h-32 min-h-[24px]"
              rows={1}
              disabled={isLoading}
            />
            
            {/* Character Counter */}
            {inputValue.length > 0 && (
              <motion.div
                className="absolute bottom-0 right-0 text-xs text-gray-400 dark:text-gray-500"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                {inputValue.length}
              </motion.div>
            )}
          </div>

          {/* Action Buttons Right */}
          <div className="flex space-x-2">
            <motion.button
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              onClick={handleVoiceInput}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Voice input"
            >
              <Mic size={18} />
            </motion.button>

            {/* Send Button */}
            <motion.button
              className={`p-2 rounded-lg transition-all duration-200 ${
                inputValue.trim() && !isLoading
                  ? 'bg-primary-600 text-grey hover:bg-primary-700 shadow-lg'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
              }`}
              onClick={onSendMessage}
              disabled={!inputValue.trim() || isLoading}
              whileHover={inputValue.trim() && !isLoading ? { scale: 1.05 } : {}}
              whileTap={inputValue.trim() && !isLoading ? { scale: 0.95 } : {}}
              title="Send message"
            >
              {isLoading ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                </motion.div>
              ) : (
                <Send size={18} />
              )}
            </motion.button>
          </div>
        </div>

        {/* Input Footer */}
        <motion.div 
          className="px-4 pb-3 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex items-center space-x-4">
            <span>AI-powered responses</span>
            <div className="flex items-center space-x-1">
              <motion.div
                className="w-2 h-2 bg-success-500 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <span>Online</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">Enter</kbd>
            <span>to send</span>
          </div>
        </motion.div>

        {/* Typing Indicator */}
        {isLoading && (
          <motion.div
            className="absolute inset-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="flex items-center space-x-2 text-primary-600">
              <div className="flex space-x-1">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-primary-600 rounded-full"
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
              <span className="text-sm font-medium">Processing...</span>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Input Hints */}
      <motion.div 
        className="mt-3 text-center text-xs text-gray-500 dark:text-gray-400"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <p>
          BinaryBrained AI can make mistakes. Consider checking important information.
        </p>
      </motion.div>
    </div>
  );
};

export default ChatInput;

