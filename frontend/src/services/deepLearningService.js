const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (window.location.hostname.includes('vercel.app') ?
    'https://ai-agent-with-frontend.onrender.com' :
    'http://localhost:5000');

class DeepLearningService {
    constructor() {
        this.baseURL = `${API_BASE_URL.replace(/\/$/, '')}/api/dl`;
    }

    async makeRequest(endpoint, data = null, method = 'GET') {
        try {
            const config = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Include cookies for session management
            };

            if (data && method !== 'GET') {
                config.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`Error making request to ${endpoint}:`, error);
            throw error;
        }
    }

    // Get list of loaded models
    async getLoadedModels() {
        return this.makeRequest('/models');
    }

    // Image classification
    async classifyImage(imageBase64, modelName = 'image_classifier', classLabels = null) {
        const data = {
            image: imageBase64,
            model_name: modelName
        };

        if (classLabels) {
            data.class_labels = classLabels;
        }

        return this.makeRequest('/image/classify', data, 'POST');
    }

    // OCR - Extract text from image
    async extractTextFromImage(imageBase64) {
        const data = {
            image: imageBase64
        };

        return this.makeRequest('/image/ocr', data, 'POST');
    }

    // Sentiment analysis
    async analyzeSentiment(text, modelName = 'sentiment_analyzer') {
        const data = {
            text: text,
            model_name: modelName
        };

        return this.makeRequest('/text/sentiment', data, 'POST');
    }

    // Text generation
    async generateText(prompt, modelName = 'text_generator', maxLength = 100) {
        const data = {
            prompt: prompt,
            model_name: modelName,
            max_length: maxLength
        };

        return this.makeRequest('/text/generate', data, 'POST');
    }

    // Extract text from PDF
    async extractTextFromPDF(pdfBase64) {
        const data = {
            pdf_base64: pdfBase64
        };

        return this.makeRequest('/pdf/extract_text', data, 'POST');
    }

    // Health check
    async healthCheck() {
        return this.makeRequest('/health');
    }

    // Utility function to convert file to base64
    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                // Remove the data URL prefix to get just the base64 string
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = error => reject(error);
        });
    }

    // Utility function to convert file to base64 with data URL
    fileToBase64WithDataURL(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }
}

export default new DeepLearningService();

