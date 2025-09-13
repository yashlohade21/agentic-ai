import React, { useRef, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';

const ChatInput = ({ 
  inputValue, 
  setInputValue, 
  onSendMessage, 
  isLoading, 
  onKeyPress,
  onFileUpload 
}) => {
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  }, [inputValue]);

  const handleSend = () => {
    if (inputValue.trim()) {
      onSendMessage();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && onFileUpload) {
      onFileUpload(file);
    }
    e.target.value = ''; // Reset file input
  };

  return (
    <div className="input-area">
      <div className="input-container">
        <div className="input-wrapper">
          {/* File Upload */}
          <input
            type="file"
            id="file-upload"
            onChange={handleFileSelect}
            className="sr-only"
            accept="image/*,application/pdf,.doc,.docx,.txt"
          />
          
          <label 
            htmlFor="file-upload"
            className="btn btn-ghost btn-sm"
            title="Attach file"
          >
            <Paperclip size={18} />
          </label>

          {/* Text Input */}
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isLoading ? "Processing request..." : "Type your message..."}
            disabled={isLoading}
            className="message-input"
            rows={1}
          />

          {/* Send Button */}
          <button
            className="send-btn"
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            title="Send message"
          >
            {isLoading ? (
              <div className="animate-pulse">
                <div className="w-5 h-5 bg-current rounded-full opacity-50" />
              </div>
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;