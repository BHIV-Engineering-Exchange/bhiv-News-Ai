'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, 
  Loader2, 
  AlertCircle, 
  CheckCircle, 
  Globe, 
  Shield, 
  FileText, 
  Lightbulb, 
  Video,
  Sparkles,
  Zap,
  Brain,
  Eye,
  Target
} from 'lucide-react'
import { runUnifiedWorkflow } from '@/lib/api'

interface AdvancedNewsAnalysisProps {
  onAnalysisStart: () => void
  onAnalysisComplete: (results: any) => void
  backendOnline: boolean
  isAnalyzing: boolean
  currentStep: number
}

const analysisSteps = [
  { 
    id: 1, 
    name: 'Web Scraping', 
    icon: Globe, 
    description: 'Extracting content from news sources',
    color: 'from-blue-500 to-cyan-500',
    bgColor: 'bg-blue-500/20'
  },
  { 
    id: 2, 
    name: 'Authenticity Vetting', 
    icon: Shield, 
    description: 'AI-powered credibility analysis',
    color: 'from-orange-500 to-red-500',
    bgColor: 'bg-orange-500/20'
  },
  { 
    id: 3, 
    name: 'Smart Summarization', 
    icon: Brain, 
    description: 'Neural network content processing',
    color: 'from-green-500 to-emerald-500',
    bgColor: 'bg-green-500/20'
  },
  { 
    id: 4, 
    name: 'Prompt Generation', 
    icon: Lightbulb, 
    description: 'Creating AI video prompts',
    color: 'from-yellow-500 to-amber-500',
    bgColor: 'bg-yellow-500/20'
  },
  { 
    id: 5, 
    name: 'Video Discovery', 
    icon: Video, 
    description: 'Finding related multimedia content',
    color: 'from-purple-500 to-pink-500',
    bgColor: 'bg-purple-500/20'
  }
]

export default function AdvancedNewsAnalysis({ 
  onAnalysisStart, 
  onAnalysisComplete, 
  backendOnline, 
  isAnalyzing, 
  currentStep 
}: AdvancedNewsAnalysisProps) {
  const [url, setUrl] = useState('https://www.bbc.com/news')
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (isAnalyzing) {
      setProgress((currentStep / analysisSteps.length) * 100)
    } else {
      setProgress(0)
    }
  }, [currentStep, isAnalyzing])

  const handleAnalyze = async () => {
    if (!backendOnline) {
      setError('Backend is offline. Please start the backend server first.')
      return
    }

    if (!url.trim()) {
      setError('Please enter a valid news URL')
      return
    }

    setError(null)
    onAnalysisStart()

    try {
      const response = await runUnifiedWorkflow(url)
      
      if (response.success) {
        onAnalysisComplete(response.data)
      } else {
        setError(response.message || 'Analysis failed')
        onAnalysisComplete(null)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to analyze news')
      onAnalysisComplete(null)
    }
  }

  const getStepStatus = (stepId: number) => {
    if (!isAnalyzing) return 'pending'
    if (stepId < currentStep) return 'completed'
    if (stepId === currentStep) return 'active'
    return 'pending'
  }

  return (
    <div className="relative">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-blue-900/20 to-pink-900/20 rounded-3xl blur-3xl"></div>
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative glass-effect rounded-3xl p-8 border border-white/20 overflow-hidden"
      >
        {/* Animated Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-purple-500 via-blue-500 to-pink-500 animate-pulse"></div>
        </div>

        {/* Header Section */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="relative z-10 flex items-center justify-between mb-8"
        >
          <div className="flex items-center space-x-6">
            {/* Animated Logo */}
            <motion.div 
              animate={{ rotate: isAnalyzing ? 360 : 0 }}
              transition={{ duration: 2, repeat: isAnalyzing ? Infinity : 0, ease: "linear" }}
              className="relative w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-2xl"
            >
              <div className="absolute inset-2 bg-black rounded-xl flex items-center justify-center">
                <div className="w-8 h-8 bg-white rounded-full transform -translate-x-1"></div>
                <div className="absolute w-4 h-4 bg-black rounded-full z-10 transform -translate-x-1"></div>
              </div>
              {isAnalyzing && (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 border-2 border-transparent border-t-white rounded-2xl"
                />
              )}
            </motion.div>
            
            <div>
              <motion.h2 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="text-4xl font-bold bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent"
              >
                Blackhole Infiverse LLP
              </motion.h2>
              <motion.p 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                className="text-gray-400 text-lg"
              >
                Advanced AI News Analysis Platform
              </motion.p>
            </div>
          </div>
          
          {/* Status Indicator */}
          <motion.div 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: "spring" }}
            className="text-right"
          >
            <div className="text-sm text-gray-400 mb-2">System Status</div>
            <div className={`flex items-center space-x-3 ${backendOnline ? 'text-green-400' : 'text-red-400'}`}>
              <motion.div 
                animate={{ scale: backendOnline ? [1, 1.2, 1] : 1 }}
                transition={{ duration: 2, repeat: backendOnline ? Infinity : 0 }}
                className={`w-4 h-4 rounded-full ${backendOnline ? 'bg-green-400' : 'bg-red-400'}`}
              />
              <span className="font-medium">
                {backendOnline ? 'Online' : 'Offline'}
              </span>
            </div>
          </motion.div>
        </motion.div>

        {/* URL Input Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="relative z-10 mb-8"
        >
          <label className="block text-xl font-semibold text-white mb-4 flex items-center space-x-2">
            <Globe className="w-6 h-6 text-blue-400" />
            <span>Enter News URL to Analyze</span>
          </label>
          
          <div className="relative">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.bbc.com/news/article-url"
              className="w-full bg-black/50 border-2 border-white/20 rounded-2xl px-6 py-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg transition-all duration-300"
              disabled={isAnalyzing}
            />
            <motion.div
              animate={{ opacity: isAnalyzing ? 0.5 : 1 }}
              className="absolute right-4 top-1/2 transform -translate-y-1/2"
            >
              <Sparkles className="w-6 h-6 text-purple-400" />
            </motion.div>
          </div>
        </motion.div>

        {/* Analysis Button */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="relative z-10 mb-8"
        >
          <motion.button
            whileHover={{ scale: isAnalyzing ? 1 : 1.02 }}
            whileTap={{ scale: isAnalyzing ? 1 : 0.98 }}
            onClick={handleAnalyze}
            disabled={isAnalyzing || !backendOnline}
            className="w-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-600 hover:from-purple-600 hover:via-pink-600 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white px-12 py-6 rounded-2xl font-bold text-xl transition-all duration-300 flex items-center justify-center space-x-4 disabled:cursor-not-allowed shadow-2xl"
          >
            {isAnalyzing ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <Loader2 className="w-8 h-8" />
                </motion.div>
                <span>Analyzing News...</span>
              </>
            ) : (
              <>
                <Zap className="w-8 h-8" />
                <span>Analyze News Article</span>
              </>
            )}
          </motion.button>
        </motion.div>

        {/* Error Display */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="relative z-10 mb-8 bg-red-500/20 border border-red-500/50 rounded-2xl p-6 flex items-start space-x-4"
            >
              <AlertCircle className="w-6 h-6 text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="text-red-400 font-medium text-lg">Analysis Error</h4>
                <p className="text-red-300 mt-1">{error}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Progress Bar */}
        {isAnalyzing && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="relative z-10 mb-8"
          >
            <div className="flex items-center justify-between text-sm text-gray-400 mb-3">
              <span>Analysis Progress</span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
              />
            </div>
          </motion.div>
        )}

        {/* Analysis Steps */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="relative z-10"
        >
          <h3 className="text-2xl font-semibold text-white mb-8 flex items-center space-x-3">
            <Brain className="w-8 h-8 text-purple-400" />
            <span>AI Analysis Pipeline</span>
          </h3>
          
          {/* Desktop View */}
          <div className="hidden lg:flex items-center justify-between space-x-4">
            {analysisSteps.map((step, index) => {
              const status = getStepStatus(step.id)
              const IconComponent = step.icon
              const isLast = index === analysisSteps.length - 1

              return (
                <div key={step.id} className="flex items-center flex-1">
                  {/* Step Card */}
                  <motion.div 
                    animate={{
                      scale: status === 'active' ? 1.05 : 1,
                      rotateY: status === 'completed' ? [0, 180, 0] : 0
                    }}
                    transition={{ duration: 0.6 }}
                    className={`
                      relative flex flex-col items-center p-6 rounded-2xl border-2 transition-all duration-500 min-w-[200px]
                      ${status === 'completed' ? 'border-green-500 bg-green-500/20' :
                        status === 'active' ? `border-purple-500 ${step.bgColor}` : 
                        'border-gray-700 bg-gray-800/50'}
                    `}
                  >
                    {/* Step Icon */}
                    <motion.div 
                      animate={{
                        rotate: status === 'active' ? 360 : 0,
                        scale: status === 'active' ? [1, 1.2, 1] : 1
                      }}
                      transition={{ 
                        rotate: { duration: 2, repeat: status === 'active' ? Infinity : 0, ease: "linear" },
                        scale: { duration: 1, repeat: status === 'active' ? Infinity : 0 }
                      }}
                      className={`
                        w-16 h-16 rounded-xl flex items-center justify-center mb-4 transition-all duration-500
                        ${status === 'completed' ? 'bg-green-500' :
                          status === 'active' ? `bg-gradient-to-br ${step.color}` : 
                          'bg-gray-700'}
                      `}
                    >
                      {status === 'completed' ? (
                        <CheckCircle className="w-8 h-8 text-white" />
                      ) : status === 'active' ? (
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        >
                          <IconComponent className="w-8 h-8 text-white" />
                        </motion.div>
                      ) : (
                        <IconComponent className="w-8 h-8 text-gray-400" />
                      )}
                    </motion.div>

                    {/* Step Info */}
                    <h4 className={`font-semibold text-lg mb-2 text-center transition-colors duration-300 ${
                      status === 'completed' ? 'text-green-400' :
                      status === 'active' ? 'text-purple-400' : 'text-gray-500'
                    }`}>
                      {step.name}
                    </h4>
                    <p className="text-sm text-gray-400 text-center leading-relaxed">
                      {step.description}
                    </p>

                    {/* Step Number */}
                    <div className="absolute -top-3 -right-3 w-8 h-8 bg-gray-800 border-2 border-gray-600 rounded-full flex items-center justify-center">
                      <span className="text-xs font-bold text-gray-400">{step.id}</span>
                    </div>
                  </motion.div>

                  {/* Connector */}
                  {!isLast && (
                    <div className="flex-1 mx-4">
                      <motion.div 
                        animate={{
                          background: status === 'completed' ? 
                            'linear-gradient(90deg, #22c55e, #22c55e)' :
                            status === 'active' ? 
                            'linear-gradient(90deg, #a855f7, #ec4899)' : 
                            'linear-gradient(90deg, #374151, #374151)'
                        }}
                        className="h-2 rounded-full transition-all duration-500"
                      />
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Mobile View */}
          <div className="lg:hidden space-y-6">
            {analysisSteps.map((step, index) => {
              const status = getStepStatus(step.id)
              const IconComponent = step.icon

              return (
                <motion.div 
                  key={step.id}
                  animate={{ x: status === 'active' ? 10 : 0 }}
                  className="flex items-center space-x-4"
                >
                  <motion.div 
                    animate={{
                      scale: status === 'active' ? 1.1 : 1,
                      rotate: status === 'active' ? 360 : 0
                    }}
                    transition={{ 
                      rotate: { duration: 2, repeat: status === 'active' ? Infinity : 0, ease: "linear" }
                    }}
                    className={`
                      w-14 h-14 rounded-xl flex items-center justify-center transition-all duration-500
                      ${status === 'completed' ? 'bg-green-500' :
                        status === 'active' ? `bg-gradient-to-br ${step.color}` : 
                        'bg-gray-700'}
                    `}
                  >
                    {status === 'completed' ? (
                      <CheckCircle className="w-7 h-7 text-white" />
                    ) : (
                      <IconComponent className="w-7 h-7 text-white" />
                    )}
                  </motion.div>

                  <div className="flex-1">
                    <h4 className={`font-semibold text-lg transition-colors duration-300 ${
                      status === 'completed' ? 'text-green-400' :
                      status === 'active' ? 'text-purple-400' : 'text-gray-500'
                    }`}>
                      {step.name}
                    </h4>
                    <p className="text-sm text-gray-400">
                      {step.description}
                    </p>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      </motion.div>
    </div>
  )
}
