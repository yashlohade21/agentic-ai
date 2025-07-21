import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, Image, File, X, Copy, RotateCcw, 
  Loader2, CheckCircle, AlertCircle, Upload 
} from 'lucide-react';
import deepLearningService from '../services/deepLearningService';

const MediaProcessor = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [filePreview, setFilePreview] = useState(null);
    const [extractedText, setExtractedText] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [fileType, setFileType] = useState('');
    const [copied, setCopied] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            setExtractedText('');
            setError(null);
            setFileType(file.type);

            // Create preview for images
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    setFilePreview(e.target.result);
                };
                reader.readAsDataURL(file);
            } else {
                setFilePreview(null);
            }
        }
    };

    const processFile = async () => {
        if (!selectedFile) {
            setError('Please select a file first');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            let result;
            
            if (selectedFile.type.startsWith('image/')) {
                // Process image with OCR
                const base64Image = await deepLearningService.fileToBase64(selectedFile);
                result = await deepLearningService.extractTextFromImage(base64Image);
            } else if (selectedFile.type === 'application/pdf') {
                // Process PDF
                const base64PDF = await deepLearningService.fileToBase64(selectedFile);
                result = await deepLearningService.extractTextFromPDF(base64PDF);
            } else {
                setError('Unsupported file type. Please select an image or PDF file.');
                return;
            }
            
            if (result.success) {
                setExtractedText(result.text || 'No text found in the file.');
            } else {
                setError(result.error || 'Failed to process file');
            }
        } catch (err) {
            setError(err.message || 'An error occurred during file processing');
        } finally {
            setLoading(false);
        }
    };

    const resetProcessor = () => {
        setSelectedFile(null);
        setFilePreview(null);
        setExtractedText('');
        setError(null);
        setFileType('');
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(extractedText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <motion.div 
            className="max-w-4xl mx-auto p-6 bg-white rounded-xl shadow-md border border-gray-100"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
        >
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                    <FileText className="text-blue-600" size={24} />
                    Media Processor
                </h2>
                <p className="text-sm text-gray-500">
                    Extract text from images & PDFs
                </p>
            </div>

            {/* File Input */}
            <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Image or PDF file
                </label>
                <div className="flex items-center gap-4">
                    <label className="flex-1 cursor-pointer">
                        <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-blue-500 transition-colors">
                            <div className="flex flex-col items-center justify-center gap-2">
                                <Upload className="text-gray-400" size={24} />
                                <p className="text-sm text-gray-600">
                                    {selectedFile ? selectedFile.name : 'Click to browse or drag and drop'}
                                </p>
                                <p className="text-xs text-gray-500">
                                    Supported formats: JPG, PNG, GIF, BMP, PDF
                                </p>
                            </div>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*,.pdf"
                                onChange={handleFileSelect}
                                className="hidden"
                            />
                        </div>
                    </label>
                    {selectedFile && (
                        <button 
                            onClick={resetProcessor}
                            className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
                            title="Clear selection"
                        >
                            <X size={20} />
                        </button>
                    )}
                </div>
            </div>

            {/* File Preview */}
            {filePreview && (
                <div className="mb-6">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">File Preview</h3>
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <img
                            src={filePreview}
                            alt="Selected file"
                            className="max-w-full h-64 object-contain mx-auto rounded-md"
                        />
                    </div>
                </div>
            )}

            {/* File Info */}
            {selectedFile && (
                <div className="mb-6 bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">File Information</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                        <div className="flex items-center gap-2">
                            <File size={16} className="text-gray-500" />
                            <span className="truncate">{selectedFile.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-gray-500">Type:</span>
                            <span>{selectedFile.type}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-gray-500">Size:</span>
                            <span>{(selectedFile.size / 1024).toFixed(2)} KB</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 mb-6">
                <button
                    onClick={processFile}
                    disabled={!selectedFile || loading}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 px-6 rounded-lg font-medium transition-colors ${
                        !selectedFile || loading 
                            ? 'bg-gray-200 text-gray-500 cursor-not-allowed' 
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                >
                    {loading ? (
                        <>
                            <Loader2 className="animate-spin" size={18} />
                            Processing...
                        </>
                    ) : (
                        <>
                            {fileType.startsWith('image/') ? (
                                <Image size={18} />
                            ) : (
                                <FileText size={18} />
                            )}
                            Extract Text
                        </>
                    )}
                </button>
                <button
                    onClick={resetProcessor}
                    className="flex-1 flex items-center justify-center gap-2 py-3 px-6 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium transition-colors"
                >
                    <RotateCcw size={18} />
                    Reset
                </button>
            </div>

            {/* Error Display */}
            <AnimatePresence>
                {error && (
                    <motion.div 
                        className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3"
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                    >
                        <AlertCircle className="text-red-500 flex-shrink-0" size={18} />
                        <div>
                            <p className="font-medium text-red-800">Error</p>
                            <p className="text-sm text-red-600">{error}</p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Extracted Text Results */}
            <AnimatePresence>
                {extractedText && (
                    <motion.div 
                        className="bg-green-50 border border-green-200 rounded-xl overflow-hidden"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                    >
                        <div className="flex justify-between items-center p-4 border-b border-green-200">
                            <h3 className="font-medium text-green-800 flex items-center gap-2">
                                <CheckCircle size={18} className="text-green-600" />
                                Extracted Text
                            </h3>
                            <button
                                onClick={copyToClipboard}
                                className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
                            >
                                {copied ? (
                                    <>
                                        <Check size={16} />
                                        Copied!
                                    </>
                                ) : (
                                    <>
                                        <Copy size={16} />
                                        Copy
                                    </>
                                )}
                            </button>
                        </div>
                        
                        <div className="p-4 bg-white max-h-96 overflow-y-auto">
                            <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                                {extractedText}
                            </pre>
                        </div>
                        
                        <div className="p-3 bg-green-50 text-xs text-green-700 border-t border-green-200">
                            <span className="font-medium">Characters:</span> {extractedText.length} | 
                            <span className="font-medium ml-2">Words:</span> {extractedText.split(/\s+/).filter(word => word.length > 0).length}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default MediaProcessor;