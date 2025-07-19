import React, { useState, useEffect } from 'react';
import deepLearningService from '../services/deepLearningService';
import MediaProcessor from './MediaProcessor';

const DeepLearningDashboard = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [modelStatus, setModelStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        checkModelStatus();
    }, []);

    const checkModelStatus = async () => {
        try {
            setLoading(true);
            const healthCheck = await deepLearningService.healthCheck();
            const models = await deepLearningService.getLoadedModels();
            
            setModelStatus({
                health: healthCheck,
                models: models
            });
        } catch (err) {
            setError(err.message || 'Failed to check model status');
        } finally {
            setLoading(false);
        }
    };

    const tabs = [
        { id: 'overview', label: 'Overview', icon: '📊' },
        { id: 'media', label: 'Media Processing', icon: '📄' },
    ];

    const renderTabContent = () => {
        switch (activeTab) {
            case 'overview':
                return (
                    <div className="space-y-6">
                        <div className="bg-white rounded-lg shadow-lg p-6">
                            <h3 className="text-xl font-semibold mb-4 text-gray-800">
                                🤖 Deep Learning Service Status
                            </h3>
                            
                            {loading ? (
                                <div className="flex items-center justify-center py-8">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                    <span className="ml-2 text-gray-600">Checking status...</span>
                                </div>
                            ) : error ? (
                                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                                    <strong>Error:</strong> {error}
                                    <button
                                        onClick={checkModelStatus}
                                        className="ml-4 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                                    >
                                        🔄 Retry
                                    </button>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    <div className="flex items-center gap-2">
                                        <div className={`w-3 h-3 rounded-full ${
                                            modelStatus?.health?.success ? 'bg-green-500' : 'bg-red-500'
                                        }`}></div>
                                        <span className="font-medium">
                                            Status: {modelStatus?.health?.status || 'Unknown'}
                                        </span>
                                    </div>
                                    
                                    <div>
                                        <p className="font-medium text-gray-700 mb-2">
                                            🧠 Loaded Models ({modelStatus?.health?.model_count || 0}):
                                        </p>
                                        {modelStatus?.models?.success && modelStatus.models.models.length > 0 ? (
                                            <ul className="list-disc list-inside space-y-1 text-gray-600">
                                                {modelStatus.models.models.map((model, index) => (
                                                    <li key={index} className="flex items-center">
                                                        <span className="mr-2">🔹</span>
                                                        {model}
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <p className="text-gray-500 italic">No models loaded - Media processing uses built-in capabilities</p>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="bg-white rounded-lg shadow-lg p-6">
                            <h3 className="text-xl font-semibold mb-4 text-gray-800">
                                ✨ Available Features
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                    <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
                                        <span className="mr-2">📄</span>
                                        Media Processing
                                    </h4>
                                    <p className="text-gray-600 text-sm mb-3">
                                        Extract text from images and PDF documents using advanced OCR technology.
                                    </p>
                                    <div className="text-xs text-gray-500">
                                        <div>• Image OCR (JPG, PNG, GIF, BMP)</div>
                                        <div>• PDF text extraction</div>
                                        <div>• Copy extracted text to clipboard</div>
                                    </div>
                                </div>
                                
                                <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                    <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
                                        <span className="mr-2">🔮</span>
                                        Future Capabilities
                                    </h4>
                                    <p className="text-gray-600 text-sm mb-3">
                                        Advanced AI features coming soon with deep learning models.
                                    </p>
                                    <div className="text-xs text-gray-500">
                                        <div>• Image classification</div>
                                        <div>• Sentiment analysis</div>
                                        <div>• Text generation</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-lg p-6 border border-blue-200">
                            <h3 className="text-xl font-semibold mb-4 text-blue-800">
                                🚀 Getting Started
                            </h3>
                            <div className="space-y-3 text-blue-700">
                                <div className="flex items-start">
                                    <span className="mr-3 mt-1">1️⃣</span>
                                    <div>
                                        <strong>Upload Media:</strong> Click on "Media Processing" tab to upload images or PDF files.
                                    </div>
                                </div>
                                <div className="flex items-start">
                                    <span className="mr-3 mt-1">2️⃣</span>
                                    <div>
                                        <strong>Extract Text:</strong> Our AI will automatically extract text from your uploaded files.
                                    </div>
                                </div>
                                <div className="flex items-start">
                                    <span className="mr-3 mt-1">3️⃣</span>
                                    <div>
                                        <strong>Use Results:</strong> Copy the extracted text and use it in your projects or conversations.
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                );
            case 'media':
                return <MediaProcessor />;
            default:
                return null;
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
            <div className="container mx-auto px-4 py-8">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-800 mb-2">
                        🧠 AI Deep Learning Hub
                    </h1>
                    <p className="text-gray-600 text-lg">
                        Advanced AI capabilities for media processing and text extraction
                    </p>
                </div>

                {/* Tab Navigation */}
                <div className="flex justify-center mb-8">
                    <div className="bg-white rounded-lg shadow-lg p-1">
                        <div className="flex space-x-1">
                            {tabs.map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`px-6 py-3 rounded-md text-sm font-medium transition-all duration-200 ${
                                        activeTab === tab.id
                                            ? 'bg-blue-600 text-white shadow-md'
                                            : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                                    }`}
                                >
                                    <span className="mr-2">{tab.icon}</span>
                                    {tab.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Tab Content */}
                <div className="max-w-6xl mx-auto">
                    {renderTabContent()}
                </div>
            </div>
        </div>
    );
};

export default DeepLearningDashboard;

