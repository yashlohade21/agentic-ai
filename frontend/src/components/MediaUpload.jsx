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
  const [uploadErrors, setUploadErrors] = useState({});
  const [previewFile, setPreviewFile] = useState(null);
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

      // Create a local preview for images
      let localPreview = null;
      if (file.type.startsWith('image/')) {
        localPreview = URL.createObjectURL(file);
      }

      // Simulate progress for better UX
      const fileId = Date.now() + Math.random();
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));

      const progressInterval = setInterval(() => {
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: Math.min(prev[fileId] + Math.random() * 30, 90)
        }));
      }, 200);

      const response = await fetch('http://localhost:5001/api/media/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      clearInterval(progressInterval);
      setUploadProgress(prev => ({ ...prev, [fileId]: 95 }));

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
        size: file.size,
        mime_type: file.type,
        url: result.file?.url || localPreview || URL.createObjectURL(file),
        localPreview: localPreview,
        serverData: result.file
      };
    } catch (error) {
      const errorMsg = error.message || 'Upload failed';
      toast.error(errorMsg);
      setUploadErrors(prev => ({ ...prev, [file.name]: errorMsg }));
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

  const handlePreview = (file) => {
    if (file.file_type === 'images') {
      setPreviewFile(file);
    } else {
      window.open(file.url, '_blank');
    }
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
        className="bg-gradient-to-br from-white via-gray-50 to-blue-50 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden border border-gray-200"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        transition={{ type: "spring", damping: 20 }}
      >
        <div className="flex items-center justify-between p-5 border-b border-gray-200 bg-white/80 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
              <Upload size={20} className="text-white" />
            </div>
            <div>
              <h3 className="font-bold text-xl text-gray-800">Upload Files</h3>
              <p className="text-sm text-gray-500">Share images, documents, and media</p>
            </div>
          </div>
          <button
            className="p-2 rounded-xl hover:bg-gray-100 transition-all duration-200 hover:scale-105"
            onClick={onClose}
          >
            <X size={22} className="text-gray-600" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Upload Area */}
          <div
            className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
              dragActive
                ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-indigo-50 scale-[1.02] shadow-lg'
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50 bg-white'
            } ${uploading ? 'cursor-not-allowed opacity-75' : 'cursor-pointer'}`}
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
              className="flex flex-col items-center justify-center gap-4"
              animate={{ scale: dragActive ? 1.05 : 1 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <motion.div
                className="relative"
                animate={{
                  rotate: uploading ? 360 : 0,
                  scale: dragActive ? 1.2 : 1
                }}
                transition={{
                  rotate: { duration: 2, repeat: uploading ? Infinity : 0, ease: "linear" },
                  scale: { type: "spring", stiffness: 300 }
                }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-600 rounded-full blur-2xl opacity-30 animate-pulse" />
                {uploading ? (
                  <Loader2 className="text-blue-600 animate-spin relative z-10" size={48} />
                ) : (
                  <div className="relative z-10 p-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-lg">
                    <Upload className="text-white" size={32} />
                  </div>
                )}
              </motion.div>
              
              <div>
                <h4 className="font-bold text-lg text-gray-800 mb-2">
                  {uploading ? 'Processing your files...' :
                   dragActive ? 'Release to upload' : 'Drop files here or click to browse'}
                </h4>

                <p className="text-sm text-gray-600 mb-3">
                  Supports images, videos, PDFs, and documents
                </p>

                <div className="flex flex-wrap gap-2 justify-center">
                  <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">JPG/PNG/GIF</span>
                  <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">PDF/DOC</span>
                  <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">MP4/MP3</span>
                  <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-medium">Max 16MB</span>
                </div>
              </div>
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
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Check className="text-green-500" size={20} />
                  <h4 className="font-semibold text-gray-800">
                    Uploaded Successfully ({uploadedFiles.length}/{maxFiles})
                  </h4>
                </div>
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
              <div className="grid gap-3">
                <AnimatePresence>
                  {uploadedFiles.map((file) => (
                    <motion.div
                      key={file.id}
                      className="group relative flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all duration-200"
                      initial={{ opacity: 0, y: 20, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, x: 50, scale: 0.9 }}
                      transition={{ duration: 0.3, type: "spring" }}
                      whileHover={{ x: 4 }}
                    >
                      <div className="flex items-center gap-4 min-w-0 flex-1">
                        <div className="relative">
                          {file.file_type === 'images' && file.localPreview ? (
                            <div className="w-12 h-12 rounded-lg overflow-hidden border-2 border-gray-200">
                              <img
                                src={file.localPreview}
                                alt={file.original_name}
                                className="w-full h-full object-cover"
                              />
                            </div>
                          ) : (
                            <div className="p-3 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border border-gray-200">
                              {getFileIcon(file.file_type)}
                            </div>
                          )}
                          <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white">
                            <Check size={8} className="text-white absolute top-0.5 left-0.5" />
                          </div>
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-semibold text-gray-800 truncate mb-1">
                            {file.original_name}
                          </p>
                          <div className="flex items-center gap-3 text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                              <File size={12} />
                              {file.size_human}
                            </span>
                            <span className="px-2 py-0.5 bg-gray-100 rounded-full capitalize">
                              {file.file_type}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <motion.button
                          onClick={() => handlePreview(file)}
                          className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
                          title="Preview file"
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Eye size={18} />
                        </motion.button>
                        {file.serverData?.url && (
                          <motion.button
                            onClick={() => window.open(file.serverData.url, '_blank')}
                            className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all duration-200"
                            title="Download"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <Download size={18} />
                          </motion.button>
                        )}
                        <motion.button
                          onClick={() => removeFile(file.id)}
                          className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200"
                          title="Remove"
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Trash2 size={18} />
                        </motion.button>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>
          )}
        </div>

        {/* Error Messages */}
        {Object.keys(uploadErrors).length > 0 && (
          <div className="mx-6 mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="text-red-500 mt-0.5" size={16} />
              <div className="flex-1">
                <p className="text-sm font-medium text-red-800 mb-1">Upload Errors:</p>
                {Object.entries(uploadErrors).map(([filename, error]) => (
                  <p key={filename} className="text-xs text-red-600">
                    {filename}: {error}
                  </p>
                ))}
              </div>
              <button
                onClick={() => setUploadErrors({})}
                className="text-red-500 hover:text-red-700"
              >
                <X size={16} />
              </button>
            </div>
          </div>
        )}

        <div className="p-5 border-t border-gray-200 bg-gray-50/50 backdrop-blur-sm">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              {uploadedFiles.length > 0 && (
                <span className="flex items-center gap-2">
                  <Check className="text-green-500" size={16} />
                  {uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''} uploaded
                </span>
              )}
            </div>
            <div className="flex gap-3">
              <motion.button
                onClick={onClose}
                className="px-5 py-2.5 text-gray-700 bg-white hover:bg-gray-100 border border-gray-300 rounded-xl transition-all duration-200 font-medium"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Cancel
              </motion.button>
              <motion.button
                onClick={() => {
                  if (uploadedFiles.length > 0) {
                    toast.success(`${uploadedFiles.length} file${uploadedFiles.length !== 1 ? 's' : ''} ready to use!`);
                  }
                  onClose?.();
                }}
                disabled={uploadedFiles.length === 0}
                className={`px-5 py-2.5 rounded-xl transition-all duration-200 flex items-center gap-2 font-medium shadow-lg ${
                  uploadedFiles.length === 0
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-blue-500/25'
                }`}
                whileHover={{ scale: uploadedFiles.length > 0 ? 1.02 : 1 }}
                whileTap={{ scale: uploadedFiles.length > 0 ? 0.98 : 1 }}
              >
                <Check size={18} />
                Finish Upload{uploadedFiles.length > 0 && ` (${uploadedFiles.length})`}
              </motion.button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Image Preview Modal */}
      <AnimatePresence>
        {previewFile && (
          <motion.div
            className="fixed inset-0 bg-black/80 backdrop-blur-md z-[60] flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setPreviewFile(null)}
          >
            <motion.div
              className="relative max-w-4xl max-h-[90vh]"
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setPreviewFile(null)}
                className="absolute -top-12 right-0 p-2 bg-white/10 backdrop-blur-sm rounded-lg text-white hover:bg-white/20 transition-colors"
              >
                <X size={24} />
              </button>
              <img
                src={previewFile.localPreview || previewFile.url}
                alt={previewFile.original_name}
                className="w-full h-full object-contain rounded-lg shadow-2xl"
              />
              <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/70 to-transparent rounded-b-lg">
                <p className="text-white font-medium">{previewFile.original_name}</p>
                <p className="text-white/80 text-sm">{previewFile.size_human}</p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default MediaUpload;