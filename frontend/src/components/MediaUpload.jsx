import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, X, File, Image, Video, Music, FileText, 
  Check, AlertCircle, Trash2, Eye, Download
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

      return result.file;
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
    return <IconComponent size={20} />;
  };

  return (
    <motion.div
      className="media-upload-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={(e) => e.target === e.currentTarget && onClose?.()}
    >
      <motion.div
        className="media-upload-modal"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ type: "spring", damping: 20 }}
      >
        <div className="modal-header">
          <h3>Upload Media</h3>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-content">
          {/* Upload Area */}
          <div
            className={`upload-area ${dragActive ? 'drag-active' : ''} ${uploading ? 'uploading' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*,video/*,audio/*,.pdf,.txt,.md"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />

            <motion.div
              className="upload-content"
              animate={{ scale: dragActive ? 1.05 : 1 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <motion.div
                className="upload-icon"
                animate={{ 
                  rotate: uploading ? 360 : 0,
                  scale: dragActive ? 1.2 : 1
                }}
                transition={{ 
                  rotate: { duration: 2, repeat: uploading ? Infinity : 0, ease: "linear" },
                  scale: { type: "spring", stiffness: 300 }
                }}
              >
                <Upload size={48} />
              </motion.div>
              
              <h4>
                {uploading ? 'Uploading...' : 
                 dragActive ? 'Drop files here' : 'Upload Media Files'}
              </h4>
              
              <p>
                Drag and drop files here, or click to select<br />
                <small>Supports images, videos, audio, documents (max 16MB each)</small>
              </p>
            </motion.div>
          </div>

          {/* Upload Progress */}
          <AnimatePresence>
            {Object.keys(uploadProgress).length > 0 && (
              <motion.div
                className="upload-progress-section"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                {Object.entries(uploadProgress).map(([fileId, progress]) => (
                  <div key={fileId} className="progress-item">
                    <div className="progress-bar">
                      <motion.div
                        className="progress-fill"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                    <span>{Math.round(progress)}%</span>
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Uploaded Files */}
          {uploadedFiles.length > 0 && (
            <div className="uploaded-files-section">
              <h4>Uploaded Files ({uploadedFiles.length}/{maxFiles})</h4>
              <div className="files-list">
                <AnimatePresence>
                  {uploadedFiles.map((file, index) => (
                    <motion.div
                      key={file.id}
                      className="file-item"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <div className="file-info">
                        <div className="file-icon">
                          {getFileIcon(file.file_type)}
                        </div>
                        <div className="file-details">
                          <span className="file-name">{file.original_name}</span>
                          <span className="file-meta">
                            {file.size_human} • {file.file_type}
                          </span>
                        </div>
                      </div>
                      
                      <div className="file-actions">
                        <motion.button
                          className="action-btn view-btn"
                          onClick={() => window.open(file.url, '_blank')}
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          title="View file"
                        >
                          <Eye size={16} />
                        </motion.button>
                        
                        <motion.button
                          className="action-btn delete-btn"
                          onClick={() => removeFile(file.id)}
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          title="Remove file"
                        >
                          <Trash2 size={16} />
                        </motion.button>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <motion.button
            className="btn btn-secondary"
            onClick={onClose}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Close
          </motion.button>
          
          {uploadedFiles.length > 0 && (
            <motion.button
              className="btn btn-primary"
              onClick={() => {
                toast.success(`${uploadedFiles.length} files ready to use`);
                onClose?.();
              }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Check size={16} />
              Done ({uploadedFiles.length})
            </motion.button>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default MediaUpload;

