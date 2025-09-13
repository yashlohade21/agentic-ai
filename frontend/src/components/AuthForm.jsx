import React, { useState } from 'react';
import { User, Mail, Lock, Eye, EyeOff, Bot, ArrowRight } from 'lucide-react';
import { toast } from 'react-hot-toast';
import './AuthForm.css';

const AuthForm = ({ onLogin, onRegister, isLoading }) => {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    // Only validate email for signup
    if (!isLoginMode) {
      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = 'Please enter a valid email';
      }
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      if (isLoginMode) {
        // Sign in with only username and password
        await onLogin({
          username: formData.username,
          password: formData.password
        });
      } else {
        // Sign up with username, email, and password
        await onRegister({
          username: formData.username,
          email: formData.email,
          password: formData.password
        });
      }
    } catch (error) {
      console.error('Auth error:', error);
      toast.error(error.message || 'Authentication failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const switchMode = (loginMode) => {
    setIsLoginMode(loginMode);
    setErrors({});
    setFormData({ username: '', email: '', password: '' });
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-container">
        <div className="auth-card">
          {/* Header */}
          <div className="auth-header">
            <div className="auth-logo">
              <Bot size={36} />
            </div>
            <h1 className="auth-title">
              {isLoginMode ? 'Welcome Back' : 'Create Account'}
            </h1>
            <p className="auth-subtitle">
              {isLoginMode 
                ? 'Sign in to continue to AI Assistant' 
                : 'Get started with your AI-powered assistant'
              }
            </p>
          </div>

          {/* Form */}
          <div className="auth-form">

          <form onSubmit={handleSubmit}>
              {/* Username Field */}
              <div className="form-group">
                <label htmlFor="username" className="form-label">
                  Username
                </label>
                <div className="input-wrapper">
                  <User className="input-icon" size={18} />
                  <input
                    id="username"
                    name="username"
                    type="text"
                    value={formData.username}
                    onChange={handleInputChange}
                    className={`form-input ${errors.username ? 'error' : ''}`}
                    placeholder="Enter your username"
                    autoComplete="username"
                  />
                </div>
                {errors.username && (
                  <span className="error-message">{errors.username}</span>
                )}
              </div>

              {/* Email Field - Only for signup */}
              {!isLoginMode && (
                <div className="form-group">
                  <label htmlFor="email" className="form-label">
                    Email Address
                  </label>
                  <div className="input-wrapper">
                    <Mail className="input-icon" size={18} />
                    <input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className={`form-input ${errors.email ? 'error' : ''}`}
                      placeholder="you@example.com"
                      autoComplete="email"
                    />
                  </div>
                  {errors.email && (
                    <span className="error-message">{errors.email}</span>
                  )}
                </div>
              )}

              {/* Password Field */}
              <div className="form-group">
                <label htmlFor="password" className="form-label">
                  Password
                </label>
                <div className="input-wrapper">
                  <Lock className="input-icon" size={18} />
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange}
                    className={`form-input ${errors.password ? 'error' : ''}`}
                    placeholder={isLoginMode ? 'Enter your password' : 'Create a password'}
                    autoComplete={isLoginMode ? 'current-password' : 'new-password'}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
                {errors.password && (
                  <span className="error-message">{errors.password}</span>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting || isLoading}
                className="submit-button"
              >
                {isSubmitting || isLoading ? (
                  <div className="button-loading">
                    <div className="spinner" />
                    <span>{isLoginMode ? 'Signing in...' : 'Creating account...'}</span>
                  </div>
                ) : (
                  <>
                    <span>{isLoginMode ? 'Sign in' : 'Create account'}</span>
                    <ArrowRight size={18} />
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Footer */}
          <div className="auth-footer">
            <p className="footer-text">
              {isLoginMode ? "Don't have an account?" : "Already have an account?"}
              <button
                type="button"
                className="mode-toggle"
                onClick={() => switchMode(!isLoginMode)}
                disabled={isSubmitting}
              >
                {isLoginMode ? 'Sign up' : 'Sign in'}
              </button>
            </p>
          </div>
        </div>

        {/* Features Section - Left Side */}
        <div className="features-section">
          <div className="features-header">
            <h2 className="features-title">Welcome to AI Assistant</h2>
            <p className="features-subtitle">Experience the power of intelligent conversation</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">✨</div>
            <div className="feature-text">
              <h3>Intelligent AI</h3>
              <p>Powered by advanced language models</p>
            </div>
          </div>
          <div className="feature-item">
            <div className="feature-icon">🔒</div>
            <div className="feature-text">
              <h3>Secure & Private</h3>
              <p>Your conversations are encrypted and safe</p>
            </div>
          </div>
          <div className="feature-item">
            <div className="feature-icon">⚡</div>
            <div className="feature-text">
              <h3>Lightning Fast</h3>
              <p>Get instant, accurate responses</p>
            </div>
          </div>
          <div className="feature-item">
            <div className="feature-icon">🎯</div>
            <div className="feature-text">
              <h3>Context Aware</h3>
              <p>Maintains conversation context</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthForm;