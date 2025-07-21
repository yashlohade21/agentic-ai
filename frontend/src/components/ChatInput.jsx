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
    <div className="w-full max-w-4xl mx-auto px-4 pb-4">
      {/* Attached Files Preview */}
      <AnimatePresence>
        {attachedFiles.length > 0 && (
          <motion.div
            className="mb-2 bg-white/80 rounded-lg p-2 shadow-sm"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="flex flex-wrap gap-2">
              {attachedFiles.map((file, index) => (
                <motion.div
                  key={file.id}
                  className="flex items-center bg-gray-50 rounded-lg p-2 pr-3 gap-2"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="flex-shrink-0">
                    {file.file_type === 'images' ? (
                      <img 
                        src={file.url} 
                        alt={file.original_name} 
                        className="w-10 h-10 object-cover rounded-md" 
                      />
                    ) : (
                      <div className="w-10 h-10 flex items-center justify-center bg-gray-200 rounded-md">
                        {file.file_type === 'documents' && <FileText size={16} className="text-gray-600" />}
                        {file.file_type === 'video' && <Video size={16} className="text-gray-600" />}
                        {file.file_type === 'audio' && <Music size={16} className="text-gray-600" />}
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">{file.original_name}</p>
                    <p className="text-xs text-gray-500">{file.size_human}</p>
                  </div>
                  <button
                    className="p-1 text-gray-500 hover:text-gray-700 transition-colors"
                    onClick={() => removeAttachedFile(file.id)}
                  >
                    <X size={14} />
                  </button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Input Area */}
      <div className="relative bg-white rounded-xl shadow-md border border-gray-200">
        <div className="flex items-end p-2">
          {/* Attachment Menu */}
          <div className="relative mr-2" ref={attachMenuRef}>
            <button
              className={`p-2 rounded-lg ${showAttachMenu ? 'bg-gray-100' : 'hover:bg-gray-100'} transition-colors`}
              onClick={() => setShowAttachMenu(!showAttachMenu)}
              disabled={isLoading}
            >
              <Plus size={20} className={`transition-transform ${showAttachMenu ? 'rotate-45' : ''}`} />
            </button>

            <AnimatePresence>
              {showAttachMenu && (
                <motion.div
                  className="absolute bottom-full left-0 mb-2 bg-white rounded-lg shadow-lg border border-gray-200 z-10"
                  initial={{ opacity: 0, scale: 0.9, y: 10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9, y: 10 }}
                  transition={{ duration: 0.2 }}
                >
                  <div className="grid grid-cols-2 gap-1 p-1">
                    {attachmentOptions.map((option, index) => (
                      <button
                        key={option.label}
                        className="flex items-center p-2 text-sm hover:bg-gray-100 rounded-md transition-colors"
                        onClick={() => {
                          option.action();
                          setShowAttachMenu(false);
                        }}
                      >
                        <option.icon size={16} className="mr-2" />
                        <span>{option.label}</span>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Text Input */}
          <div className="flex-1 min-w-0">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isLoading ? "AI is thinking..." : "Type your message..."}
              disabled={isLoading}
              className="w-full min-h-[40px] max-h-[120px] px-3 py-2 bg-transparent outline-none resize-none"
              rows={1}
            />
          </div>

          {/* Right Controls */}
          <div className="flex items-center ml-2">
            {/* Voice Recording */}
            <button
              className={`p-2 rounded-lg ${isRecording ? 'bg-red-100 text-red-600' : 'hover:bg-gray-100'} transition-colors`}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading}
            >
              {isRecording ? <Square size={20} /> : <Mic size={20} />}
            </button>

            {/* Send Button */}
            <button
              className={`ml-2 p-2 rounded-lg ${(inputValue.trim() || attachedFiles.length > 0) && !isLoading 
                ? 'bg-blue-600 text-white hover:bg-blue-700' 
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'} transition-colors`}
              onClick={handleSend}
              disabled={(!inputValue.trim() && attachedFiles.length === 0) || isLoading}
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>
        </div>

        {/* Input Footer */}
        <div className="px-3 py-2 border-t border-gray-100 text-xs text-gray-500 flex justify-between">
          <div>
            Press Enter to send, Shift+Enter for new line
          </div>
          {inputValue.length > 0 && (
            <div>
              {inputValue.length} characters
            </div>
          )}
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
    </div>
  );
};

export default ChatInput;