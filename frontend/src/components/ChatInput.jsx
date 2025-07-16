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
    <div className="chat-input-wrapper">
      {/* Quick Prompts */}
      <motion.div 
        className="quick-prompts"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {quickPrompts.map((prompt, index) => (
          <motion.button
            key={prompt}
            className="quick-prompt-btn"
            onClick={() => setInputValue(prompt + " ")}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Zap size={12} />
            <span>{prompt}</span>
          </motion.button>
        ))}
      </motion.div>

      {/* Main Input Container */}
      <motion.div
        className="chat-input-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        whileFocusWithin={{ 
          boxShadow: "0 0 0 3px rgba(99, 102, 241, 0.1)",
          borderColor: "rgb(99, 102, 241)"
        }}
      >
        {/* Input Area */}
        <div className="input-area">
          {/* Action Buttons Left */}
          <div className="action-buttons-left">
            <motion.button
              className="action-btn"
              onClick={handleFileAttach}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Attach file"
            >
              <Paperclip size={18} />
            </motion.button>
            
            <motion.button
              className="action-btn"
              onClick={handleEmojiPicker}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Add emoji"
            >
              <Smile size={18} />
            </motion.button>
          </div>

          {/* Text Input */}
          <div className="text-input-wrapper">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={onKeyPress}
              placeholder="Type your message here..."
              className="text-input"
              rows={1}
              disabled={isLoading}
            />
            
            {/* Character Counter */}
            {inputValue.length > 0 && (
              <motion.div
                className="char-counter"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                {inputValue.length}
              </motion.div>
            )}
          </div>

          {/* Action Buttons Right */}
          <div className="action-buttons-right">
            <motion.button
              className="action-btn"
              onClick={handleVoiceInput}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Voice input"
            >
              <Mic size={18} />
            </motion.button>

            {/* Send Button */}
            <motion.button
              className={`send-btn ${
                inputValue.trim() && !isLoading ? 'active' : 'disabled'
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
                  <div className="loading-spinner" />
                </motion.div>
              ) : (
                <Send size={18} />
              )}
            </motion.button>
          </div>
        </div>

        {/* Input Footer */}
        <motion.div 
          className="input-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="footer-left">
            <span className="ai-indicator">AI-powered responses</span>
            <div className="status-indicator">
              <motion.div
                className="status-dot"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <span>Online</span>
            </div>
          </div>
          
          <div className="footer-right">
            <kbd className="key-hint">Enter</kbd>
            <span>to send</span>
          </div>
        </motion.div>

        {/* Typing Indicator */}
        {isLoading && (
          <motion.div
            className="typing-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="typing-content">
              <div className="typing-dots">
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
              <span className="typing-text">Processing...</span>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Input Hints */}
      <motion.div 
        className="input-hints"
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