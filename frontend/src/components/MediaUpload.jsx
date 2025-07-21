import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, X, File, Image, Video, Music, FileText, 
  Check, AlertCircle, Trash2, Eye, Download, Loader2
} from 'lucide-react';
import { toast } from 'react-hot-toast';

const MediaUpload = ({ onFileUpload, onClose, maxFiles = 5 }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const fileInputRef = useRef(null);

  const fileTypeIcons = {
    images: Image,
    documents: FileText,
    audio: Music,
    video: Video,
    default: File
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateFile = (file) => {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
      'application/pdf', 'text/plain', 'text/markdown',
      'audio/mpeg', 'audio/wav', 'audio/ogg',
      'video/mp4', 'video/webm', 'video/quicktime'
    ];

    if (file.size > maxSize) {
      throw new Error(`File "${file.name}" is too large. Maximum size is 16MB.`);
    }

    if (!allowedTypes.includes(file.type)) {
      throw new Error(`File type "${file.type}" is not supported.`);
    }

    return true;
  };

  const uploadFile = async (file) => {
    try {
      validateFile(file);

      const formData = new FormData();
      formData.append('file', file);

      // Simulate progress for better UX
      const fileId = Date.now() + Math.random();
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));

      const progressInterval = setInterval(() => {
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: Math.min(prev[fileId] + Math.random() * 30, 90)
        }));
      }, 200);

      const response = await fetch('/api/media/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }

      const result = await response.json();
      
      setUploadProgress(prev => ({ ...prev, [fileId]: 100 }));
      
      setTimeout(() => {
        setUploadProgress(prev => {
          const newProgress = { ...prev };
          delete newProgress[fileId];
          return newProgress;
        });
      }, 1000);

      return {
        id: fileId,
        original_name: file.name,
        file_type: file.type.startsWith('image/') ? 'images' : 
                  file.type.startsWith('video/') ? 'video' :
                  file.type.startsWith('audio/') ? 'audio' : 'documents',
        size_human: formatFileSize(file.size),
        url: URL.createObjectURL(file)
      };
    } catch (error) {
      toast.error(error.message);
      throw error;
    }
  };

  const handleFiles = async (files) => {
    if (uploadedFiles.length + files.length > maxFiles) {
      toast.error(`Maximum ${maxFiles} files allowed`);
      return;
    }

    setUploading(true);
    const newFiles = [];

    try {
      for (const file of files) {
        try {
          const uploadedFile = await uploadFile(file);
          newFiles.push(uploadedFile);
          toast.success(`${file.name} uploaded successfully`);
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error);
        }
      }

      setUploadedFiles(prev => [...prev, ...newFiles]);
      
      if (onFileUpload) {
        newFiles.forEach(file => onFileUpload(file));
      }
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  }, []);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const getFileIcon = (fileType) => {
    const IconComponent = fileTypeIcons[fileType] || fileTypeIcons.default;
    return <IconComponent size={18} className="text-gray-600" />;
  };

  return (
    <motion.div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={(e) => e.target === e.currentTarget && onClose?.()}
    >
      <motion.div
        className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[90vh] flex flex-col overflow-hidden"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        transition={{ type: "spring", damping: 20 }}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h3 className="font-semibold text-lg text-gray-800">Upload Media</h3>
          <button 
            className="p-1 rounded-full hover:bg-gray-100 transition-colors"
            onClick={onClose}
          >
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {/* Upload Area */}
          <div
            className={`relative border-2 border-dashed rounded-xl p-6 text-center transition-colors ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
            } ${uploading ? 'cursor-not-allowed' : 'cursor-pointer'}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => !uploading && fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*,video/*,audio/*,.pdf,.txt,.md"
              onChange={handleFileSelect}
              className="hidden"
              disabled={uploading}
            />

            <motion.div
              className="flex flex-col items-center justify-center gap-3"
              animate={{ scale: dragActive ? 1.02 : 1 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <motion.div
                animate={{ 
                  rotate: uploading ? 360 : 0,
                  scale: dragActive ? 1.1 : 1
                }}
                transition={{ 
                  rotate: { duration: 2, repeat: uploading ? Infinity : 0, ease: "linear" },
                  scale: { type: "spring", stiffness: 300 }
                }}
              >
                {uploading ? (
                  <Loader2 className="text-blue-500 animate-spin" size={32} />
                ) : (
                  <Upload className="text-gray-400" size={32} />
                )}
              </motion.div>
              
              <h4 className="font-medium text-gray-800">
                {uploading ? 'Uploading files...' : 
                 dragActive ? 'Drop files here' : 'Click to upload or drag and drop'}
              </h4>
              
              <p className="text-sm text-gray-500">
                Supports images, videos, audio, and documents<br />
                <span className="text-xs">(Max 16MB per file)</span>
              </p>
            </motion.div>
          </div>

          {/* Upload Progress */}
          <AnimatePresence>
            {Object.keys(uploadProgress).length > 0 && (
              <motion.div
                className="mt-4 space-y-2"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                {Object.entries(uploadProgress).map(([fileId, progress]) => (
                  <div key={fileId} className="flex items-center gap-3">
                    <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-blue-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-600 w-10">
                      {Math.round(progress)}%
                    </span>
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Uploaded Files */}
          {uploadedFiles.length > 0 && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-800">
                  Uploaded Files ({uploadedFiles.length}/{maxFiles})
                </h4>
                {uploadedFiles.length > 0 && (
                  <button 
                    onClick={() => setUploadedFiles([])}
                    className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1"
                  >
                    <Trash2 size={14} />
                    Clear all
                  </button>
                )}
              </div>
              <div className="space-y-2">
                <AnimatePresence>
                  {uploadedFiles.map((file) => (
                    <motion.div
                      key={file.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="p-2 bg-white rounded-md border border-gray-200">
                          {getFileIcon(file.file_type)}
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-gray-800 truncate">
                            {file.original_name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {file.size_human} • {file.file_type}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => window.open(file.url, '_blank')}
                          className="p-1.5 text-gray-500 hover:text-blue-600 transition-colors"
                          title="View file"
                        >
                          <Eye size={16} />
                        </button>
                        <button
                          onClick={() => removeFile(file.id)}
                          className="p-1.5 text-gray-500 hover:text-red-600 transition-colors"
                          title="Remove file"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              toast.success(`${uploadedFiles.length} files ready to use`);
              onClose?.();
            }}
            disabled={uploadedFiles.length === 0}
            className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
              uploadedFiles.length === 0
                ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <Check size={16} />
            Done ({uploadedFiles.length})
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default MediaUpload;