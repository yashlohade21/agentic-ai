import React from 'react';
import { 
  Bot, Code, Search, FileText, Brain, MessageCircle, 
  TrendingUp, BarChart3, Users, Briefcase, Sparkles,
  Image, Upload, Camera, File
} from 'lucide-react';

const WelcomeMessage = ({ onExampleClick }) => {
  const quickStarters = [
    {
      title: "📸 Upload & Analyze Images",
      prompt: "Upload an image and I'll analyze it for you",
      icon: Image,
      gradient: "from-blue-500 to-cyan-500",
      featured: true
    },
    {
      title: "📄 Upload Documents & PDFs",
      prompt: "Upload documents and I'll help you analyze them",
      icon: File,
      gradient: "from-emerald-500 to-teal-500",
      featured: true
    },
    {
      title: "Code & Development",
      prompt: "Help me build a React component with TypeScript",
      icon: Code,
      gradient: "from-purple-500 to-indigo-500"
    },
    {
      title: "Data Analysis", 
      prompt: "Analyze this dataset and create visualizations",
      icon: BarChart3,
      gradient: "from-amber-500 to-orange-500"
    },
    {
      title: "Business Strategy",
      prompt: "Create a go-to-market strategy for my SaaS product",
      icon: Briefcase,
      gradient: "from-rose-500 to-pink-500"
    },
    {
      title: "Research & Writing",
      prompt: "Research market trends in artificial intelligence",
      icon: Search,
      gradient: "from-violet-500 to-purple-500"
    }
  ];

  return (
    <div className="welcome-container">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="welcome-icon">
          <Bot size={40} color="white" />
        </div>
        <h2 className="text-responsive-3xl font-bold mb-4 gradient-text">
          How can I help you today?
        </h2>
        <p className="text-responsive-lg text-secondary max-w-2xl mx-auto">
          I'm your AI assistant with powerful media analysis capabilities. Upload images, documents, or PDFs for instant AI analysis, 
          or ask me about coding, research, writing, and much more.
        </p>
        
        {/* Upload Feature Highlight */}
        <div className="upload-feature-highlight">
          <div className="upload-highlight-content">
            <div className="upload-highlight-icons">
              <div className="upload-highlight-icon">
                <Camera size={20} />
              </div>
              <div className="upload-highlight-icon">
                <Upload size={20} />
              </div>
            </div>
            <div className="upload-highlight-text">
              <strong>✨ New: AI-Powered File Analysis</strong>
              <p>Click the 📎 or 📸 buttons below to upload and analyze your files instantly!</p>
            </div>
          </div>
        </div>
      </div>

      {/* Bento Grid Layout */}
      <div className="example-prompts">
        {quickStarters.map((starter, index) => {
          const IconComponent = starter.icon;
          return (
            <div
              key={starter.title}
              className={`example-prompt group ${starter.featured ? 'featured-prompt' : ''}`}
              onClick={() => onExampleClick(starter.prompt)}
              style={{
                animationDelay: `${index * 100}ms`
              }}
            >
              <div className="example-prompt-icon">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${starter.gradient} flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                  <IconComponent size={24} />
                </div>
              </div>
              <div className="example-prompt-content">
                <h4 className="font-semibold text-primary mb-2">
                  {starter.title}
                </h4>
                <p className="text-sm text-secondary line-clamp-2">
                  {starter.prompt}
                </p>
              </div>
              <div className="absolute inset-0 bg-gradient-to-br from-transparent to-transparent group-hover:from-blue-50/50 group-hover:to-purple-50/50 rounded-xl transition-all duration-300 pointer-events-none" />
            </div>
          );
        })}
      </div>

      {/* Features */}
      <div className="welcome-features">
        <div className="welcome-feature">
          <Sparkles size={16} className="text-accent-primary" />
          <span>AI-Powered</span>
        </div>
        <div className="welcome-feature">
          <MessageCircle size={16} className="text-accent-primary" />
          <span>Conversational</span>
        </div>
        <div className="welcome-feature">
          <TrendingUp size={16} className="text-accent-primary" />
          <span>Always Learning</span>
        </div>
      </div>

      <p className="welcome-hint">
        💡 Tip: Try being specific about what you need help with for the best results
      </p>
    </div>
  );
};

export default WelcomeMessage;