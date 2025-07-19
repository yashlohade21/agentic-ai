import React, { useState, useRef } from 'react';
import deepLearningService from '../services/deepLearningService';

const MediaProcessor = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [filePreview, setFilePreview] = useState(null);
    const [extractedText, setExtractedText] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [fileType, setFileType] = useState('');
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
    };

    return (
        <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
            <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">
                📄 Media Processor - Extract Text from Images & PDFs
            </h2>

            {/* File Input */}
            <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Image or PDF file:
                </label>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*,.pdf"
                    onChange={handleFileSelect}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                <p className="text-xs text-gray-500 mt-1">
                    Supported formats: JPG, PNG, GIF, BMP, PDF
                </p>
            </div>

            {/* File Preview */}
            {filePreview && (
                <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-2 text-gray-700">Preview:</h3>
                    <img
                        src={filePreview}
                        alt="Selected file"
                        className="max-w-full h-64 object-contain mx-auto rounded-lg border border-gray-300"
                    />
                </div>
            )}

            {/* File Info */}
            {selectedFile && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                    <h3 className="text-lg font-semibold mb-2 text-gray-700">File Information:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                            <span className="font-medium">Name:</span> {selectedFile.name}
                        </div>
                        <div>
                            <span className="font-medium">Type:</span> {selectedFile.type}
                        </div>
                        <div>
                            <span className="font-medium">Size:</span> {(selectedFile.size / 1024).toFixed(2)} KB
                        </div>
                    </div>
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4 mb-6">
                <button
                    onClick={processFile}
                    disabled={!selectedFile || loading}
                    className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
                >
                    {loading ? (
                        <div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                            Processing...
                        </div>
                    ) : (
                        `Extract Text from ${fileType.startsWith('image/') ? 'Image' : 'PDF'}`
                    )}
                </button>
                <button
                    onClick={resetProcessor}
                    className="flex-1 bg-gray-600 text-white py-3 px-6 rounded-lg hover:bg-gray-700 font-medium"
                >
                    Reset
                </button>
            </div>

            {/* Error Display */}
            {error && (
                <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                    <div className="flex items-center">
                        <span className="text-red-500 mr-2">⚠️</span>
                        <strong>Error:</strong> {error}
                    </div>
                </div>
            )}

            {/* Extracted Text Results */}
            {extractedText && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold text-green-800">
                            📝 Extracted Text
                        </h3>
                        <button
                            onClick={copyToClipboard}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 text-sm font-medium"
                        >
                            📋 Copy to Clipboard
                        </button>
                    </div>
                    
                    <div className="bg-white border border-green-300 rounded-lg p-4 max-h-96 overflow-y-auto">
                        <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                            {extractedText}
                        </pre>
                    </div>
                    
                    <div className="mt-4 text-sm text-green-700">
                        <span className="font-medium">Characters:</span> {extractedText.length} | 
                        <span className="font-medium ml-2">Words:</span> {extractedText.split(/\s+/).filter(word => word.length > 0).length}
                    </div>
                </div>
            )}
        </div>
    );
};

export default MediaProcessor;

