import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Activity, Zap, Sparkles, TrendingUp, Database, Cpu, BarChart3, FileText, Image, Layers, RefreshCw } from 'lucide-react';
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
        { id: 'overview', label: 'Overview', icon: BarChart3 },
        { id: 'media', label: 'Media Processing', icon: FileText },
    ];

    const features = [
        {
            icon: FileText,
            title: 'Media Processing',
            description: 'Extract text from images and PDF documents using advanced OCR technology.',
            capabilities: ['Image OCR (JPG, PNG, GIF, BMP)', 'PDF text extraction', 'Copy extracted text to clipboard'],
            gradient: 'from-blue-500 to-cyan-500',
            bgGradient: 'from-blue-50 to-cyan-50'
        },
        {
            icon: Brain,
            title: 'Neural Networks',
            description: 'Advanced AI features powered by state-of-the-art deep learning models.',
            capabilities: ['Image classification', 'Sentiment analysis', 'Text generation'],
            gradient: 'from-purple-500 to-pink-500',
            bgGradient: 'from-purple-50 to-pink-50'
        },
        {
            icon: Layers,
            title: 'Model Management',
            description: 'Efficient loading and management of multiple AI models for different tasks.',
            capabilities: ['Dynamic model loading', 'Resource optimization', 'Performance monitoring'],
            gradient: 'from-green-500 to-emerald-500',
            bgGradient: 'from-green-50 to-emerald-50'
        },
        {
            icon: Zap,
            title: 'Real-time Processing',
            description: 'Lightning-fast processing with optimized inference pipelines.',
            capabilities: ['Batch processing', 'Stream processing', 'Edge deployment'],
            gradient: 'from-orange-500 to-red-500',
            bgGradient: 'from-orange-50 to-red-50'
        }
    ];

    const renderTabContent = () => {
        switch (activeTab) {
            case 'overview':
                return (
                    <motion.div 
                        className="space-y-6 px-4 pb-6"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        {/* Status Card */}
                        <motion.div 
                            className="bg-white rounded-2xl shadow-md border border-gray-200 overflow-hidden"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.5 }}
                        >
                            <div className="p-6">
                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                                    <div className="flex items-center gap-4">
                                        <div className="p-3 bg-blue-100 rounded-2xl">
                                            <Activity className="w-6 h-6 text-blue-600" />
                                        </div>
                                        <div>
                                            <h3 className="text-xl font-bold text-gray-800">
                                                Deep Learning Service Status
                                            </h3>
                                            <p className="text-gray-600">Real-time system monitoring</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={checkModelStatus}
                                        className="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors flex-shrink-0"
                                    >
                                        <RefreshCw className="w-5 h-5" />
                                    </button>
                                </div>
                                
                                {loading ? (
                                    <div className="flex flex-col items-center justify-center py-8 gap-4">
                                        <div className="relative">
                                            <div className="w-12 h-12 border-4 border-blue-200 rounded-full animate-spin border-t-blue-600"></div>
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <Brain className="w-6 h-6 text-blue-600" />
                                            </div>
                                        </div>
                                        <span className="text-gray-600">Analyzing system status...</span>
                                    </div>
                                ) : error ? (
                                    <motion.div 
                                        className="bg-red-50 border border-red-200 rounded-2xl p-4"
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                    >
                                        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                                            <div className="p-2 bg-red-100 rounded-lg flex-shrink-0">
                                                <Zap className="w-5 h-5 text-red-600" />
                                            </div>
                                            <div className="flex-1">
                                                <h4 className="font-semibold text-red-800">System Error</h4>
                                                <p className="text-red-600">{error}</p>
                                            </div>
                                            <button
                                                onClick={checkModelStatus}
                                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex-shrink-0"
                                            >
                                                Retry
                                            </button>
                                        </div>
                                    </motion.div>
                                ) : (
                                    <div className="space-y-6">
                                        <div className="flex items-center gap-4">
                                            <div className={`w-3 h-3 rounded-full ${modelStatus?.health?.success ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
                                            <span className="text-gray-800">
                                                Status: {modelStatus?.health?.status || 'Unknown'}
                                            </span>
                                        </div>
                                        
                                        <div className="bg-gray-50 rounded-2xl p-4">
                                            <div className="flex items-center gap-3 mb-4">
                                                <Database className="w-5 h-5 text-blue-600" />
                                                <h4 className="text-gray-800">
                                                    Loaded Models ({modelStatus?.health?.model_count || 0})
                                                </h4>
                                            </div>
                                            {modelStatus?.models?.success && modelStatus.models.models.length > 0 ? (
                                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                                    {modelStatus.models.models.map((model, index) => (
                                                        <motion.div
                                                            key={index}
                                                            className="flex items-center gap-3 p-2 bg-white rounded-lg shadow-sm"
                                                            initial={{ opacity: 0, y: 10 }}
                                                            animate={{ opacity: 1, y: 0 }}
                                                            transition={{ delay: index * 0.1 }}
                                                        >
                                                            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                                            <span className="text-gray-700 truncate">{model}</span>
                                                        </motion.div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <div className="text-center py-4">
                                                    <Cpu className="w-10 h-10 text-gray-400 mx-auto mb-2" />
                                                    <p className="text-gray-500">No models loaded - Media processing uses built-in capabilities</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </motion.div>

                        {/* Features Grid */}
                        <motion.div 
                            className="grid grid-cols-1 md:grid-cols-2 gap-4"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.2 }}
                        >
                            {features.map((feature, index) => (
                                <motion.div
                                    key={index}
                                    className={`bg-white rounded-2xl shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-300`}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                >
                                    <div className="p-6">
                                        <div className="flex items-center gap-4 mb-4">
                                            <div className={`p-3 bg-gradient-to-br ${feature.gradient} rounded-2xl shadow-sm`}>
                                                <feature.icon className="w-6 h-6 text-white" />
                                            </div>
                                            <h4 className="text-lg font-bold text-gray-800">{feature.title}</h4>
                                        </div>
                                        <p className="text-gray-600 mb-4">{feature.description}</p>
                                        <div className="space-y-2">
                                            {feature.capabilities.map((capability, capIndex) => (
                                                <div key={capIndex} className="flex items-center gap-2">
                                                    <div className={`w-2 h-2 bg-gradient-to-r ${feature.gradient} rounded-full`}></div>
                                                    <span className="text-sm text-gray-600">{capability}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </motion.div>

                        {/* Getting Started Section */}
                        <motion.div 
                            className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-lg overflow-hidden"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.4 }}
                        >
                            <div className="p-6 text-white">
                                <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
                                    <div className="p-3 bg-white/20 rounded-2xl flex-shrink-0">
                                        <Sparkles className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold">Getting Started</h3>
                                        <p className="text-white/90">Begin your AI journey in three simple steps</p>
                                    </div>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {[
                                        { step: '01', title: 'Upload Media', desc: 'Click on "Media Processing" tab to upload images or PDF files.' },
                                        { step: '02', title: 'Extract Text', desc: 'Our AI will automatically extract text from your uploaded files.' },
                                        { step: '03', title: 'Use Results', desc: 'Copy the extracted text and use it in your projects or conversations.' }
                                    ].map((item, index) => (
                                        <motion.div
                                            key={index}
                                            className="bg-white/10 rounded-xl p-4 border border-white/20"
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.6 + index * 0.1 }}
                                        >
                                            <div className="text-2xl font-bold text-white/60 mb-2">{item.step}</div>
                                            <h4 className="font-semibold mb-1">{item.title}</h4>
                                            <p className="text-white/80 text-sm">{item.desc}</p>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                );
            case 'media':
                return (
                    <motion.div
                        className="px-4 pb-6"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        <MediaProcessor />
                    </motion.div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 overflow-auto">
            <div className="container mx-auto px-0">
                {/* Header */}
                <motion.div 
                    className="text-center py-8 px-4"
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <div className="flex flex-col items-center gap-4 mb-4">
                        <motion.div
                            className="p-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl shadow-lg"
                            animate={{ rotate: [0, 5, -5, 0] }}
                            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                        >
                            <Brain className="w-10 h-10 text-white" />
                        </motion.div>
                        <div>
                            <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                                AI Deep Learning Hub
                            </h1>
                        </div>
                    </div>
                    <p className="text-gray-600 max-w-2xl mx-auto">
                        Advanced AI capabilities for media processing, text extraction, and intelligent data analysis
                    </p>
                </motion.div>

                {/* Tab Navigation */}
                <motion.div 
                    className="flex justify-center mb-8 px-4"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                >
                    <div className="bg-white rounded-xl shadow-sm p-1">
                        <div className="flex">
                            {tabs.map((tab) => (
                                <motion.button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`relative px-6 py-2 rounded-lg text-sm font-medium transition-colors ${
                                        activeTab === tab.id
                                            ? 'bg-blue-600 text-white'
                                            : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                                    }`}
                                >
                                    <div className="flex items-center gap-2">
                                        <tab.icon className="w-4 h-4" />
                                        <span>{tab.label}</span>
                                    </div>
                                    {activeTab === tab.id && (
                                        <motion.div
                                            className="absolute inset-0 bg-blue-600 rounded-lg -z-10"
                                            layoutId="activeTab"
                                            transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                        />
                                    )}
                                </motion.button>
                            ))}
                        </div>
                    </div>
                </motion.div>

                {/* Tab Content */}
                <div className="max-w-7xl mx-auto">
                    <AnimatePresence mode="wait">
                        {renderTabContent()}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};

export default DeepLearningDashboard;