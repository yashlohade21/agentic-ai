import React, { useState, useRef, useCallback } from 'react';
import { Upload, X, Image, FileText, Check, AlertCircle, Trash2, Eye, Loader2 } from 'lucide-react';
import { toast } from 'react-hot-toast';

const ImagePDFUpload = ({ onFileUpload, onClose, onAnalyze }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const fileInputRef = useRef(null);

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
      'application/pdf'
    ];

    if (file.size > maxSize) {
      throw new Error(`File "${file.name}" is too large. Maximum size is 16MB.`);
    }

    if (!allowedTypes.includes(file.type)) {
      throw new Error(`File type "${file.type}" is not supported. Please upload images (JPG, PNG, GIF, WEBP, BMP) or PDF files.`);
    }

    return true;
  };

  const uploadFile = async (file) => {
    try {
      validateFile(file);

      // Mock upload for now (when backend is not available)
      const mockFile = {
        id: Date.now() + Math.random(),
        original_name: file.name,
        file_type: file.type.includes('image') ? 'image' : 'pdf',
        size_human: formatFileSize(file.size),
        url: URL.createObjectURL(file),
        mime_type: file.type
      };

      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      return mockFile;
    } catch (error) {
      toast.error(error.message);
      throw error;
    }
  };

  const handleFiles = async (files) => {
    if (uploadedFiles.length + files.length > 3) {
      toast.error('Maximum 3 files allowed');
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

  const analyzeFile = async (file) => {
    if (!onAnalyze) return;

    setAnalyzing(true);
    try {
      await onAnalyze(file);
      toast.success(`Analysis completed for ${file.original_name}`);
    } catch (error) {
      toast.error(`Analysis failed: ${error.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const getFileIcon = (fileType, mimeType) => {
    if (mimeType && mimeType.startsWith('image/')) {
      return <Image size={18} className="text-blue-600" />;
    } else if (mimeType === 'application/pdf') {
      return <FileText size={18} className="text-red-600" />;
    }
    return <FileText size={18} className="text-gray-600" />;
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden border border-gray-100">
        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
          <div>
            <h3 className="font-bold text-xl text-gray-800 flex items-center gap-2">
              📎 Upload Files
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              <span className="inline-flex items-center gap-1">
                📸 Images (JPG, PNG, GIF, WEBP, BMP) • 📄 PDFs
              </span>
            </p>
          </div>
          <button
            className="p-2 rounded-full hover:bg-white/60 transition-all duration-200 hover:scale-110"
            onClick={onClose}
          >
            <X size={22} className="text-gray-600" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {/* Modern Upload Area */}
          <div
            className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
              dragActive
                ? 'border-blue-400 bg-gradient-to-br from-blue-50 to-indigo-50 scale-105'
                : 'border-gray-300 hover:border-blue-300 hover:bg-gradient-to-br hover:from-gray-50 hover:to-blue-50'
            } ${uploading ? 'cursor-not-allowed opacity-75' : 'cursor-pointer hover:shadow-lg'}`}
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
              accept="image/*,.pdf"
              onChange={handleFileSelect}
              className="hidden"
              disabled={uploading}
            />

            <div className="flex flex-col items-center justify-center gap-4">
              <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl shadow-md">
                {uploading ? (
                  <Loader2 className="text-blue-500 animate-spin" size={32} />
                ) : (
                  <Upload className="text-blue-500" size={32} />
                )}
              </div>

              <div className="space-y-2">
                <h4 className="font-semibold text-lg text-gray-800">
                  {uploading ? 'Uploading files...' :
                   dragActive ? '📁 Drop your files here' : '📎 Choose Files to Upload'}
                </h4>

                <p className="text-gray-600">
                  Drag and drop or click to browse
                </p>
              </div>

              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-gray-200 shadow-sm">
                <div className="flex items-center justify-center gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
                    <span className="text-gray-600">Images: JPG, PNG, GIF, WEBP, BMP</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                    <span className="text-gray-600">Documents: PDF</span>
                  </div>
                </div>
                <div className="text-xs text-gray-500 mt-2 text-center">
                  Maximum 16MB per file • Up to 3 files total
                </div>
              </div>
            </div>
          </div>

          {/* Uploaded Files */}
          {uploadedFiles.length > 0 && (
            <div className="mt-8">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-lg text-gray-800 flex items-center gap-2">
                  ✅ Uploaded Files ({uploadedFiles.length}/3)
                </h4>
                {uploadedFiles.length > 0 && (
                  <button
                    onClick={() => setUploadedFiles([])}
                    className="text-sm text-red-500 hover:text-red-700 flex items-center gap-2 px-3 py-1 rounded-lg hover:bg-red-50 transition-all"
                  >
                    <Trash2 size={16} />
                    Clear all
                  </button>
                )}
              </div>
              <div className="space-y-3">
                {uploadedFiles.map((file) => (
                  <div
                    key={file.id}
                    className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all"
                  >
                    <div className="flex items-center gap-4 min-w-0 flex-1">
                      <div className="p-3 bg-white rounded-xl border border-gray-200 shadow-sm">
                        {getFileIcon(file.file_type, file.mime_type)}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-semibold text-gray-800 truncate">
                          {file.original_name}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          📦 {file.size_human} • {file.file_type.toUpperCase()}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {onAnalyze && (
                        <button
                          onClick={() => analyzeFile(file)}
                          disabled={analyzing}
                          className="p-2 text-blue-500 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-all disabled:opacity-50"
                          title="🔍 Analyze with AI"
                        >
                          {analyzing ? (
                            <Loader2 size={18} className="animate-spin" />
                          ) : (
                            <Eye size={18} />
                          )}
                        </button>
                      )}
                      <button
                        onClick={() => removeFile(file.id)}
                        className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-all"
                        title="🗑️ Remove file"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-gray-100 bg-gradient-to-r from-gray-50 to-white flex justify-between items-center gap-4">
          <button
            onClick={onClose}
            className="px-6 py-3 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-xl transition-all duration-200 font-medium"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              if (uploadedFiles.length > 0) {
                toast.success(`🎉 ${uploadedFiles.length} files ready to use!`, {
                  duration: 3000,
                });
              }
              onClose?.();
            }}
            disabled={uploadedFiles.length === 0}
            className={`px-6 py-3 rounded-xl transition-all duration-200 flex items-center gap-3 font-semibold ${
              uploadedFiles.length === 0
                ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:from-blue-600 hover:to-indigo-700 shadow-lg hover:shadow-xl hover:scale-105'
            }`}
          >
            <Check size={18} />
            {uploadedFiles.length === 0 ? 'Select Files First' : `Use ${uploadedFiles.length} File${uploadedFiles.length > 1 ? 's' : ''}`}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImagePDFUpload;