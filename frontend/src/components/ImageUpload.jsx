import React, { useState, useRef, useCallback } from 'react';
import { Upload, X, Image as ImageIcon, Check, Trash2, Eye, Loader2 } from 'lucide-react';
import { toast } from 'react-hot-toast';

const ImageUpload = ({ onFileUpload, onClose, onAnalyze }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedImages, setUploadedImages] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const fileInputRef = useRef(null);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateImage = (file) => {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'
    ];

    if (file.size > maxSize) {
      throw new Error(`Image "${file.name}" is too large. Maximum size is 16MB.`);
    }

    if (!allowedTypes.includes(file.type)) {
      throw new Error(`File type "${file.type}" is not supported. Please upload JPG, PNG, GIF, WEBP, or BMP images.`);
    }

    return true;
  };

  const uploadImage = async (file) => {
    try {
      validateImage(file);

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/media/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }

      const result = await response.json();

      return {
        id: result.file.id,
        original_name: result.file.original_name,
        file_type: result.file.file_type,
        size_human: result.file.size_human,
        url: result.file.url,
        mime_type: result.file.mime_type
      };
    } catch (error) {
      toast.error(error.message);
      throw error;
    }
  };

  const handleFiles = async (files) => {
    // Filter only images
    const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));

    if (imageFiles.length === 0) {
      toast.error('Please select image files only (JPG, PNG, GIF, WEBP, BMP)');
      return;
    }

    if (uploadedImages.length + imageFiles.length > 5) {
      toast.error('Maximum 5 images allowed');
      return;
    }

    setUploading(true);
    const newImages = [];

    try {
      for (const file of imageFiles) {
        try {
          const uploadedImage = await uploadImage(file);
          newImages.push(uploadedImage);
          toast.success(`📸 ${file.name} uploaded successfully`);
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error);
        }
      }

      setUploadedImages(prev => [...prev, ...newImages]);

      if (onFileUpload) {
        newImages.forEach(image => onFileUpload(image));
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
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const removeImage = (imageId) => {
    setUploadedImages(prev => prev.filter(image => image.id !== imageId));
  };

  const analyzeImage = async (image) => {
    if (!onAnalyze) return;

    setAnalyzing(true);
    try {
      await onAnalyze(image);
      toast.success(`🔍 Analysis completed for ${image.original_name}`);
    } catch (error) {
      toast.error(`Analysis failed: ${error.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[90vh] flex flex-col overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div>
            <h3 className="font-semibold text-lg text-gray-800 flex items-center gap-2">
              📸 Upload Images
            </h3>
            <p className="text-sm text-blue-600">JPG, PNG, GIF, WEBP, BMP</p>
          </div>
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
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-blue-300 hover:border-blue-400 bg-blue-25'
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
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
              disabled={uploading}
            />

            <div className="flex flex-col items-center justify-center gap-3">
              <div className="flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full">
                {uploading ? (
                  <Loader2 className="text-blue-500 animate-spin" size={28} />
                ) : (
                  <ImageIcon className="text-blue-500" size={28} />
                )}
              </div>

              <h4 className="font-medium text-gray-800">
                {uploading ? 'Uploading images...' :
                 dragActive ? '📸 Drop your images here' : '📸 Upload Images'}
              </h4>

              <p className="text-sm text-gray-500">
                <strong>Supported:</strong> JPG, PNG, GIF, WEBP, BMP<br />
                <span className="text-xs">(Max 16MB per image, 5 images total)</span>
              </p>

              <div className="text-xs text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
                ✨ AI will analyze your images with Groq vision
              </div>
            </div>
          </div>

          {/* Uploaded Images */}
          {uploadedImages.length > 0 && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-800">
                  📸 Uploaded Images ({uploadedImages.length}/5)
                </h4>
                {uploadedImages.length > 0 && (
                  <button
                    onClick={() => setUploadedImages([])}
                    className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1"
                  >
                    <Trash2 size={14} />
                    Clear all
                  </button>
                )}
              </div>
              <div className="space-y-2">
                {uploadedImages.map((image) => (
                  <div
                    key={image.id}
                    className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200"
                  >
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <div className="p-2 bg-white rounded-md border border-blue-200">
                        <ImageIcon size={18} className="text-blue-600" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-800 truncate">
                          📸 {image.original_name}
                        </p>
                        <p className="text-xs text-blue-600">
                          {image.size_human} • Image
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {onAnalyze && (
                        <button
                          onClick={() => analyzeImage(image)}
                          disabled={analyzing}
                          className="p-1.5 text-blue-500 hover:text-blue-700 transition-colors disabled:opacity-50"
                          title="🔍 Analyze with AI"
                        >
                          {analyzing ? (
                            <Loader2 size={16} className="animate-spin" />
                          ) : (
                            <Eye size={16} />
                          )}
                        </button>
                      )}
                      <button
                        onClick={() => removeImage(image.id)}
                        className="p-1.5 text-gray-500 hover:text-red-600 transition-colors"
                        title="Remove image"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
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
              if (uploadedImages.length > 0) {
                toast.success(`📸 ${uploadedImages.length} images ready to analyze!`);
              }
              onClose?.();
            }}
            disabled={uploadedImages.length === 0}
            className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
              uploadedImages.length === 0
                ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <Check size={16} />
            Done ({uploadedImages.length} 📸)
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImageUpload;