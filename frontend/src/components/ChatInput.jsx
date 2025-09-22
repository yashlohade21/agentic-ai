import React, { useState, useRef, useEffect } from "react";
import { Send, Paperclip, Image, FileText } from "lucide-react";
import ImagePDFUpload from "./ImagePDFUpload";
import { toast } from "react-hot-toast";

const ChatInput = ({
  inputValue,
  setInputValue,
  onSendMessage,
  isLoading,
  onFileUpload,
  onFileAnalyze,
}) => {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState([]);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }
  }, [inputValue]);

  const handleSend = () => {
    if (inputValue.trim() || attachedFiles.length > 0) {
      onSendMessage(attachedFiles);
      setAttachedFiles([]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = (file) => {
    if (onFileUpload) onFileUpload(file);
    setAttachedFiles((prev) => [...prev, file]);
    toast.success(`File attached: ${file.original_name}`);
  };

  const handleFileAnalyze = async (file) => {
    try {
      const response = await fetch("/api/media/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          file_id: file.id,
          prompt: "Analyze this file and describe what you see in detail.",
        }),
      });

      if (!response.ok) throw new Error("Analysis failed");

      const result = await response.json();
      if (onFileAnalyze) onFileAnalyze(file, result.analysis);

      const analysisText = `Analysis of ${file.original_name}: ${result.analysis}`;
      setInputValue((prev) => (prev ? `${prev}\n\n${analysisText}` : analysisText));
    } catch (error) {
      toast.error(`Analysis failed: ${error.message}`);
    }
  };

  const removeAttachedFile = (fileId) => {
    setAttachedFiles((prev) => prev.filter((file) => file.id !== fileId));
  };

  return (
    <>
      <div className="claude-input-area">
        <div className="input-container">
          {/* Attached Files */}
          {attachedFiles.length > 0 && (
            <div className="mb-3">
              <div className="text-xs text-gray-500 mb-2 font-medium">📎 Attached files:</div>
              <div className="flex flex-wrap gap-2">
                {attachedFiles.map((file) => (
                  <div
                    key={file.id}
                    className="flex items-center gap-2 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-800 px-3 py-2 rounded-xl text-sm border border-blue-200 shadow-sm"
                  >
                    {file.mime_type?.startsWith("image/") ? (
                      <Image size={16} className="text-blue-600" />
                    ) : (
                      <FileText size={16} className="text-blue-600" />
                    )}
                    <span className="truncate max-w-32 font-medium">{file.original_name}</span>
                    <button
                      onClick={() => removeAttachedFile(file.id)}
                      className="text-blue-600 hover:text-blue-800 hover:bg-blue-200 rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold transition-all"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Modern Chat Input */}
          <div
            className="input-wrapper"
            style={{
              background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
              border: '2px solid #e2e8f0',
              borderRadius: '16px',
              padding: '16px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
              transition: 'all 0.3s ease',
              minHeight: '60px',
              overflow: 'visible',
              zIndex: 1,
              position: 'relative'
            }}
          >
            {/* Single Universal Upload Button */}
            <button
              type="button"
              onClick={() => setShowUploadModal(true)}
              disabled={isLoading}
              className="media-button-visible flex items-center justify-center w-12 h-12 bg-gradient-to-br from-emerald-400 to-green-500 text-white rounded-xl cursor-pointer transition-all duration-300 hover:from-emerald-500 hover:to-green-600 hover:scale-110 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
              title="📎 Attach Files & Images (PDFs, JPG, PNG, GIF, WEBP, BMP)"
              style={{
                zIndex: 1000,
                visibility: 'visible',
                opacity: 1,
                display: 'flex',
                position: 'relative',
                minWidth: '48px',
                minHeight: '48px'
              }}
            >
              <Paperclip size={22} />
            </button>

            {/* Enhanced Textarea */}
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isLoading ? "🤖 Processing request..." : "💬 Type your message..."}
              disabled={isLoading}
              rows={1}
              className="flex-1 resize-none bg-transparent px-4 py-3 text-base focus:outline-none placeholder-gray-400"
              style={{
                fontSize: '16px',
                lineHeight: '1.6',
                minHeight: '24px',
                maxHeight: '120px'
              }}
            />

            {/* Enhanced Send Button */}
            <button
              onClick={handleSend}
              disabled={(!inputValue.trim() && attachedFiles.length === 0) || isLoading}
              className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-xl transition-all duration-300 hover:from-blue-600 hover:to-purple-700 hover:scale-110 hover:shadow-lg disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed shadow-md"
              title={isLoading ? "Sending..." : "Send message"}
              style={{
                minWidth: '48px',
                minHeight: '48px'
              }}
            >
              {isLoading ? (
                <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Universal Upload Modal */}
      {showUploadModal && (
        <ImagePDFUpload
          onFileUpload={handleFileUpload}
          onAnalyze={handleFileAnalyze}
          onClose={() => setShowUploadModal(false)}
        />
      )}
    </>
  );
};

export default ChatInput;
