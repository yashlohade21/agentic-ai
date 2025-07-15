import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, Users, Zap, RefreshCw, Trash2, LogOut, 
  Server, Cpu, HardDrive, Wifi, WifiOff, AlertTriangle,
  CheckCircle, Clock, TrendingUp, BarChart3
} from 'lucide-react';

const AgentStatus = ({ 
  systemStatus, 
  connectionStatus, 
  user, 
  onRefresh, 
  onClearHistory, 
  onLogout, 
  isLoading 
}) => {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'agents', label: 'Agents', icon: Users },
    { id: 'system', label: 'System', icon: Server },
    { id: 'user', label: 'Profile', icon: Users }
  ];

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Wifi size={16} className="text-success-500" />;
      case 'mock':
        return <AlertTriangle size={16} className="text-warning-500" />;
      default:
        return <WifiOff size={16} className="text-error-500" />;
    }
  };

  const getConnectionColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'text-success-600 bg-success-50 dark:bg-success-900/20';
      case 'mock':
        return 'text-warning-600 bg-warning-50 dark:bg-warning-900/20';
      default:
        return 'text-error-600 bg-error-50 dark:bg-error-900/20';
    }
  };

  const mockSystemMetrics = {
    cpu: 45,
    memory: 62,
    storage: 38,
    uptime: '2h 34m'
  };

  const renderOverview = () => (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Connection Status */}
      <div className={`p-4 rounded-lg ${getConnectionColor()}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getConnectionIcon()}
            <div>
              <h4 className="font-semibold capitalize">{connectionStatus}</h4>
              <p className="text-sm opacity-80">
                {connectionStatus === 'connected' ? 'All systems operational' :
                 connectionStatus === 'mock' ? 'Running in offline mode' :
                 'Connection unavailable'}
              </p>
            </div>
          </div>
          <motion.button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 rounded-lg hover:bg-black/10 transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <motion.div
              animate={isLoading ? { rotate: 360 } : {}}
              transition={isLoading ? { duration: 1, repeat: Infinity, ease: "linear" } : {}}
            >
              <RefreshCw size={16} />
            </motion.div>
          </motion.button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <Users size={16} className="text-primary-600" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Active Agents</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {systemStatus.agents?.length || 0}
          </p>
        </div>

        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp size={16} className="text-success-600" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Requests</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {systemStatus.session_requests || 0}
          </p>
        </div>
      </div>

      {/* System Health */}
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-900 dark:text-white">System Health</h4>
        
        {Object.entries(mockSystemMetrics).map(([key, value]) => (
          <div key={key} className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="capitalize text-gray-700 dark:text-gray-300">{key}</span>
              <span className="text-gray-900 dark:text-white font-medium">
                {typeof value === 'number' ? `${value}%` : value}
              </span>
            </div>
            {typeof value === 'number' && (
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <motion.div
                  className={`h-2 rounded-full ${
                    value > 80 ? 'bg-error-500' :
                    value > 60 ? 'bg-warning-500' : 'bg-success-500'
                  }`}
                  initial={{ width: 0 }}
                  animate={{ width: `${value}%` }}
                  transition={{ duration: 1, delay: 0.2 }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </motion.div>
  );

  const renderAgents = () => (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {systemStatus.agents?.map((agent, index) => (
        <motion.div
          key={agent}
          className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <motion.div
                className="w-3 h-3 bg-success-500 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity, delay: index * 0.3 }}
              />
              <div>
                <h5 className="font-medium text-gray-900 dark:text-white capitalize">
                  {agent.replace(/_/g, ' ')}
                </h5>
                <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {Math.floor(Math.random() * 100)}%
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Load</p>
            </div>
          </div>
        </motion.div>
      )) || (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <Users size={32} className="mx-auto mb-2 opacity-50" />
          <p>No agents available</p>
        </div>
      )}
    </motion.div>
  );

  const renderSystem = () => (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* System Info */}
      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">System Information</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Version</span>
            <span className="text-gray-900 dark:text-white font-medium">v1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Uptime</span>
            <span className="text-gray-900 dark:text-white font-medium">{mockSystemMetrics.uptime}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Status</span>
            <span className="text-success-600 font-medium flex items-center">
              <CheckCircle size={14} className="mr-1" />
              Operational
            </span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-900 dark:text-white">Actions</h4>
        
        <motion.button
          onClick={onRefresh}
          disabled={isLoading}
          className="w-full flex items-center justify-center space-x-2 p-3 bg-primary-600 text-grey rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <RefreshCw size={16} />
          <span>Refresh System</span>
        </motion.button>

        <motion.button
          onClick={onClearHistory}
          className="w-full flex items-center justify-center space-x-2 p-3 bg-warning-600 text-grey rounded-lg hover:bg-warning-700 transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Trash2 size={16} />
          <span>Clear History</span>
        </motion.button>

        <motion.button
          onClick={onLogout}
          className="w-full flex items-center justify-center space-x-2 p-3 bg-error-600 text-grey rounded-lg hover:bg-error-700 transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <LogOut size={16} />
          <span>Logout</span>
        </motion.button>
      </div>
    </motion.div>
  );

  const renderUser = () => (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* User Info */}
      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
        <div className="flex items-center space-x-4 mb-4">
          <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center">
            <Users size={24} className="text-grey" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-grey">
              {user?.username || 'User'}
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {user?.email || 'No email provided'}
            </p>
          </div>
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Member since</span>
            <span className="text-gray-900 dark:text-white font-medium">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Sessions</span>
            <span className="text-gray-900 dark:text-white font-medium">
              {systemStatus.session_requests || 0}
            </span>
          </div>
        </div>
      </div>

      {/* User Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg text-center">
          <div className="text-2xl font-bold text-primary-600 mb-1">
            {Math.floor(Math.random() * 50) + 10}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Messages Sent</div>
        </div>
        
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg text-center">
          <div className="text-2xl font-bold text-success-600 mb-1">
            {Math.floor(Math.random() * 20) + 5}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Tasks Completed</div>
        </div>
      </div>
    </motion.div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'agents':
        return renderAgents();
      case 'system':
        return renderSystem();
      case 'user':
        return renderUser();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="h-full flex flex-col p-4 max-w-4xl mx-auto w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 md:mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
          <Activity size={20} className="mr-2 text-primary-600" />
          <span className="hidden sm:inline">System Dashboard</span>
          <span className="sm:hidden">Dashboard</span>
        </h3>
        <div className="flex items-center space-x-1 text-xs text-gray-500 dark:text-gray-400">
          <Clock size={12} />
          <span className="hidden xs:inline">Live</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex mb-4 md:mb-6 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg overflow-x-auto">
        <div className="flex space-x-1 min-w-max">
          {tabs.map((tab) => (
            <motion.button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center justify-center space-x-2 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-white dark:bg-gray-700 text-primary-600 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <tab.icon size={16} />
              <span className="hidden sm:inline">{tab.label}</span>
              <span className="sm:hidden">{tab.label.charAt(0)}</span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto pb-4">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {renderTabContent()}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default AgentStatus;