import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, Paperclip, Mic, Square, Smile, Image, 
  FileText, Video, Music, X, Plus
} from 'lucide-react';
import MediaUpload from './MediaUpload';

const ChatInput = ({ 
  inputValue, 
  setInputValue, 
  onSendMessage, 
  isLoading, 
  onKeyPress,
  onFileUpload 
}) => {
  const [showMediaUpload, setShowMediaUpload] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [showAttachMenu, setShowAttachMenu] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState([]);
  const textareaRef = useRef(null);
  const attachMenuRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  }, [inputValue]);

  // Close attach menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (attachMenuRef.current && !attachMenuRef.current.contains(event.target)) {
        setShowAttachMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSend = () => {
    if (inputValue.trim() || attachedFiles.length > 0) {
      onSendMessage();
      setAttachedFiles([]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = (file) => {
    setAttachedFiles(prev => [...prev, file]);
    if (onFileUpload) {
      onFileUpload(file);
    }
  };

  const removeAttachedFile = (fileId) => {
    setAttachedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const startRecording = () => {
    setIsRecording(true);
    // TODO: Implement voice recording
  };

  const stopRecording = () => {
    setIsRecording(false);
    // TODO: Stop voice recording and process
  };

  const attachmentOptions = [
    { icon: Image, label: 'Images', action: () => setShowMediaUpload(true) },
    { icon: FileText, label: 'Documents', action: () => setShowMediaUpload(true) },
    { icon: Video, label: 'Videos', action: () => setShowMediaUpload(true) },
    { icon: Music, label: 'Audio', action: () => setShowMediaUpload(true) },
  ];

  return (
    <>
      <div className="chat-input-container">
        {/* Attached Files Preview */}
        <AnimatePresence>
          {attachedFiles.length > 0 && (
            <motion.div
              className="attached-files-preview"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
            >
              <div className="attached-files-list">
                {attachedFiles.map((file, index) => (
                  <motion.div
                    key={file.id}
                    className="attached-file-item"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <div className="file-preview">
                      {file.file_type === 'images' ? (
                        <img src={file.url} alt={file.original_name} className="file-thumbnail" />
                      ) : (
                        <div className="file-icon">
                          {file.file_type === 'documents' && <FileText size={16} />}
                          {file.file_type === 'video' && <Video size={16} />}
                          {file.file_type === 'audio' && <Music size={16} />}
                        </div>
                      )}
                    </div>
                    <div className="file-info">
                      <span className="file-name">{file.original_name}</span>
                      <span className="file-size">{file.size_human}</span>
                    </div>
                    <motion.button
                      className="remove-file-btn"
                      onClick={() => removeAttachedFile(file.id)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <X size={14} />
                    </motion.button>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Input Area */}
        <div className="chat-input-wrapper">
          <div className="input-controls-left">
            {/* Attachment Menu */}
            <div className="attachment-menu-container" ref={attachMenuRef}>
              <motion.button
                className={`control-btn attachment-btn ${showAttachMenu ? 'active' : ''}`}
                onClick={() => setShowAttachMenu(!showAttachMenu)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={isLoading}
              >
                <motion.div
                  animate={{ rotate: showAttachMenu ? 45 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <Plus size={18} />
                </motion.div>
              </motion.button>

              <AnimatePresence>
                {showAttachMenu && (
                  <motion.div
                    className="attachment-options"
                    initial={{ opacity: 0, scale: 0.9, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: 10 }}
                    transition={{ duration: 0.2 }}
                  >
                    {attachmentOptions.map((option, index) => (
                      <motion.button
                        key={option.label}
                        className="attachment-option"
                        onClick={() => {
                          option.action();
                          setShowAttachMenu(false);
                        }}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        whileHover={{ scale: 1.02, x: 4 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <option.icon size={16} />
                        <span>{option.label}</span>
                      </motion.button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Text Input */}
          <div className="text-input-container">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isLoading ? "AI is thinking..." : "Type your message..."}
              disabled={isLoading}
              className="chat-textarea"
              rows={1}
            />
          </div>

          <div className="input-controls-right">
            {/* Voice Recording */}
            <motion.button
              className={`control-btn voice-btn ${isRecording ? 'recording' : ''}`}
              onClick={isRecording ? stopRecording : startRecording}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              disabled={isLoading}
            >
              <AnimatePresence mode="wait">
                {isRecording ? (
                  <motion.div
                    key="stop"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                  >
                    <Square size={18} />
                  </motion.div>
                ) : (
                  <motion.div
                    key="mic"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                  >
                    <Mic size={18} />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>

            {/* Send Button */}
            <motion.button
              className={`send-btn ${(inputValue.trim() || attachedFiles.length > 0) && !isLoading ? 'active' : ''}`}
              onClick={handleSend}
              disabled={(!inputValue.trim() && attachedFiles.length === 0) || isLoading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <AnimatePresence mode="wait">
                {isLoading ? (
                  <motion.div
                    key="loading"
                    initial={{ scale: 0, rotate: 0 }}
                    animate={{ scale: 1, rotate: 360 }}
                    exit={{ scale: 0 }}
                    transition={{ rotate: { duration: 1, repeat: Infinity, ease: "linear" } }}
                  >
                    <div className="loading-spinner-small" />
                  </motion.div>
                ) : (
                  <motion.div
                    key="send"
                    initial={{ scale: 0, x: -10 }}
                    animate={{ scale: 1, x: 0 }}
                    exit={{ scale: 0, x: 10 }}
                  >
                    <Send size={18} />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>
          </div>
        </div>

        {/* Input Footer */}
        <div className="input-footer">
          <div className="input-hints">
            <span>Press Enter to send, Shift+Enter for new line</span>
          </div>
          <div className="input-stats">
            {inputValue.length > 0 && (
              <span className="char-count">{inputValue.length} characters</span>
            )}
          </div>
        </div>
      </div>

      {/* Media Upload Modal */}
      <AnimatePresence>
        {showMediaUpload && (
          <MediaUpload
            onFileUpload={handleFileUpload}
            onClose={() => setShowMediaUpload(false)}
            maxFiles={5}
          />
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatInput;

