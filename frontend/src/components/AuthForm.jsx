import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, User, Mail, Lock, Eye, EyeOff, Sparkles, Shield } from 'lucide-react';
import { toast } from 'react-hot-toast';

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
    // Clear error when user starts typing
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

    if (!isLoginMode && !formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!isLoginMode && !/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
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
      toast.error('Please fix the errors below', {
        icon: '❌',
        duration: 3000,
      });
      return;
    }

    setIsSubmitting(true);

    try {
      if (isLoginMode) {
        await onLogin({
          username: formData.username,
          password: formData.password
        });
      } else {
        await onRegister({
          username: formData.username,
          email: formData.email,
          password: formData.password
        });
      }
    } catch (error) {
      toast.error(error.message || 'Authentication failed', {
        icon: '❌',
        duration: 4000,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleMode = () => {
    setIsLoginMode(!isLoginMode);
    setFormData({ username: '', email: '', password: '' });
    setErrors({});
  };

  const containerVariants = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut",
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: "easeOut" }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 via-primary-600 to-secondary-600 flex items-center justify-center p-4 sm:p-6">
      {/* Background Animation */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1.5 h-1.5 sm:w-2 sm:h-2 bg-white/10 rounded-full"
            animate={{
              x: [0, Math.random() * 100 - 50],
              y: [0, Math.random() * 100 - 50],
              opacity: [0, 1, 0]
            }}
            transition={{
              duration: Math.random() * 3 + 2,
              repeat: Infinity,
              delay: Math.random() * 2
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`
            }}
          />
        ))}
      </div>

      <motion.div
        className="w-full max-w-xs sm:max-w-sm md:max-w-md"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Card */}
        <motion.div
          className="bg-white/10 backdrop-blur-lg rounded-2xl sm:rounded-3xl p-6 sm:p-8 shadow-2xl border border-white/20"
          variants={itemVariants}
        >
          {/* Header */}
          <motion.div className="text-center mb-6 sm:mb-8" variants={itemVariants}>
            <motion.div
              className="inline-flex items-center justify-center w-12 h-12 sm:w-16 sm:h-16 bg-white/20 rounded-full mb-3 sm:mb-4"
              animate={{ 
                rotate: [0, 5, -5, 0],
                scale: [1, 1.1, 1]
              }}
              transition={{ 
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <Bot size={24} className="sm:w-8 sm:h-8 text-white" />
            </motion.div>
            
            <h1 className="text-2xl sm:text-3xl font-bold text-white mb-1 sm:mb-2">
              BinaryBrained AI
            </h1>
            
            <AnimatePresence mode="wait">
              <motion.p
                key={isLoginMode ? 'login' : 'register'}
                className="text-white/80 text-sm sm:text-base"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                {isLoginMode ? 'Welcome back! Sign in to continue.' : 'Join us and start your AI journey.'}
              </motion.p>
            </AnimatePresence>
          </motion.div>

          {/* Form */}
          <motion.form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6" variants={itemVariants}>
            {/* Username Field */}
            <motion.div variants={itemVariants}>
              <label className="block text-white/90 text-xs sm:text-sm font-medium mb-1 sm:mb-2">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User size={16} className="sm:w-[18px] sm:h-[18px] text-white/60" />
                </div>
                <motion.input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className={`w-full pl-9 sm:pl-10 pr-3 sm:pr-4 py-2 sm:py-3 bg-white/10 border ${
                    errors.username ? 'border-red-400' : 'border-white/30'
                  } rounded-lg sm:rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/50 focus:border-transparent transition-all duration-200 text-sm sm:text-base`}
                  placeholder="Enter your username"
                  whileFocus={{ scale: 1.02 }}
                />
              </div>
              <AnimatePresence>
                {errors.username && (
                  <motion.p
                    className="text-red-300 text-xs sm:text-sm mt-1"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                  >
                    {errors.username}
                  </motion.p>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Email Field (Register only) */}
            <AnimatePresence>
              {!isLoginMode && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <label className="block text-white/90 text-xs sm:text-sm font-medium mb-1 sm:mb-2">
                    Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Mail size={16} className="sm:w-[18px] sm:h-[18px] text-white/60" />
                    </div>
                    <motion.input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className={`w-full pl-9 sm:pl-10 pr-3 sm:pr-4 py-2 sm:py-3 bg-white/10 border ${
                        errors.email ? 'border-red-400' : 'border-white/30'
                      } rounded-lg sm:rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/50 focus:border-transparent transition-all duration-200 text-sm sm:text-base`}
                      placeholder="Enter your email"
                      whileFocus={{ scale: 1.02 }}
                    />
                  </div>
                  <AnimatePresence>
                    {errors.email && (
                      <motion.p
                        className="text-red-300 text-xs sm:text-sm mt-1"
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                      >
                        {errors.email}
                      </motion.p>
                    )}
                  </AnimatePresence>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Password Field */}
            <motion.div variants={itemVariants}>
              <label className="block text-white/90 text-xs sm:text-sm font-medium mb-1 sm:mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock size={16} className="sm:w-[18px] sm:h-[18px] text-white/60" />
                </div>
                <motion.input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={`w-full pl-9 sm:pl-10 pr-10 sm:pr-12 py-2 sm:py-3 bg-white/10 border ${
                    errors.password ? 'border-red-400' : 'border-white/30'
                  } rounded-lg sm:rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/50 focus:border-transparent transition-all duration-200 text-sm sm:text-base`}
                  placeholder="Enter your password"
                  whileFocus={{ scale: 1.02 }}
                />
                <motion.button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  {showPassword ? (
                    <EyeOff size={16} className="sm:w-[18px] sm:h-[18px] text-white/60" />
                  ) : (
                    <Eye size={16} className="sm:w-[18px] sm:h-[18px] text-white/60" />
                  )}
                </motion.button>
              </div>
              <AnimatePresence>
                {errors.password && (
                  <motion.p
                    className="text-red-300 text-xs sm:text-sm mt-1"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                  >
                    {errors.password}
                  </motion.p>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-white/20 hover:bg-white/30 disabled:bg-white/10 text-white font-semibold py-2.5 sm:py-3 px-4 rounded-lg sm:rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 backdrop-blur-sm border border-white/30 text-sm sm:text-base"
              variants={itemVariants}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isSubmitting ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    <div className="w-4 h-4 sm:w-5 sm:h-5 border-2 border-white border-t-transparent rounded-full" />
                  </motion.div>
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  {isLoginMode ? <Shield size={18} className="sm:w-5 sm:h-5" /> : <Sparkles size={18} className="sm:w-5 sm:h-5" />}
                  <span>{isLoginMode ? 'Sign In' : 'Create Account'}</span>
                </>
              )}
            </motion.button>
          </motion.form>

          {/* Toggle Mode */}
          <motion.div className="mt-4 sm:mt-6 text-center" variants={itemVariants}>
            <p className="text-white/80 text-xs sm:text-sm">
              {isLoginMode ? "Don't have an account?" : "Already have an account?"}
            </p>
            <motion.button
              type="button"
              onClick={toggleMode}
              className="text-white font-semibold hover:text-white/80 transition-colors mt-1 text-sm sm:text-base"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isLoginMode ? 'Create one now' : 'Sign in instead'}
            </motion.button>
          </motion.div>

          {/* Footer */}
          <motion.div 
            className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-white/20 text-center"
            variants={itemVariants}
          >
            <p className="text-white/60 text-xs">
              By continuing, you agree to our Terms of Service and Privacy Policy
            </p>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default AuthForm;