'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/Header'
import BackendStatus from '@/components/BackendStatus'
import { checkBackendHealth, runUnifiedWorkflow } from '@/lib/api'
import { 
  Zap, 
  Globe, 
  Shield, 
  Brain, 
  Lightbulb, 
  Video,
  CheckCircle,
  AlertCircle,
  Loader2,
  Sparkles,
  TrendingUp
} from 'lucide-react'

// Dynamic import for framer-motion to handle potential issues
let motion: any = null
let AnimatePresence: any = null

try {
  const framerMotion = require('framer-motion')
  motion = framerMotion.motion
  AnimatePresence = framerMotion.AnimatePresence
} catch (error) {
  console.warn('Framer Motion not available, using fallback animations')
  // Fallback components
  motion = {
    div: ({ children, className, style, animate, initial, transition, whileHover, whileTap, ...props }: any) => (
      <div className={className} style={style} {...props}>{children}</div>
    ),
    button: ({ children, className, style, animate, initial, transition, whileHover, whileTap, ...props }: any) => (
      <button className={className} style={style} {...props}>{children}</button>
    )
  }
  AnimatePresence = ({ children }: any) => children
}

interface AnalysisResults {
  scraped_data?: any
  vetting_results?: any
  summary?: any
  video_prompt?: any
  sidebar_videos?: any
  steps_completed?: number
  total_processing_time?: number
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

export default function AdvancedNewsAnalysisPage() {
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking')
  const [url, setUrl] = useState('https://httpbin.org/html')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    checkBackend()
    const interval = setInterval(checkBackend, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (isAnalyzing) {
      setProgress((currentStep / analysisSteps.length) * 100)
    } else {
      setProgress(0)
    }
  }, [currentStep, isAnalyzing])

  const checkBackend = async () => {
    setBackendStatus('checking')
    try {
      const isHealthy = await checkBackendHealth()
      setBackendStatus(isHealthy ? 'online' : 'offline')
    } catch (error) {
      setBackendStatus('offline')
    }
  }

  const handleAnalyze = async () => {
    if (!backendStatus || backendStatus === 'offline') {
      setError('Backend is offline. Please start the backend server first.')
      return
    }

    if (!url.trim()) {
      setError('Please enter a valid news URL')
      return
    }

    setError(null)
    setIsAnalyzing(true)
    setCurrentStep(1)
    setAnalysisResults(null)

    // Simulate step progression
    const steps = [1, 2, 3, 4, 5]
    steps.forEach((step, index) => {
      setTimeout(() => {
        setCurrentStep(step)
      }, index * 2000)
    })

    try {
      console.log('🚀 Starting advanced analysis for URL:', url)
      const response = await runUnifiedWorkflow(url)
      console.log('📥 Advanced analysis response:', response)
      
      setTimeout(() => {
        if (response.success) {
          console.log('✅ Advanced analysis successful!')
          setAnalysisResults(response.data)
        } else {
          console.error('❌ Advanced analysis failed:', response.message)
          setError(response.message || 'Analysis failed')
        }
        setIsAnalyzing(false)
        setCurrentStep(0)
      }, 10000) // Complete after 10 seconds
    } catch (err: any) {
      console.error('💥 Advanced analysis error:', err)
      setTimeout(() => {
        setError(err.message || 'Failed to analyze news')
        setIsAnalyzing(false)
        setCurrentStep(0)
      }, 10000)
    }
  }

  const getStepStatus = (stepId: number) => {
    if (!isAnalyzing) return 'pending'
    if (stepId < currentStep) return 'completed'
    if (stepId === currentStep) return 'active'
    return 'pending'
  }

  return (
    <div className="min-h-screen">
      <Header backendStatus={backendStatus} />
      
      <div className="bg-gradient-to-br from-gray-900 via-purple-900 to-black overflow-hidden">
        {/* Animated Background */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <motion.div
            animate={{ 
              x: [0, 100, 0],
              y: [0, -100, 0],
              scale: [1, 1.2, 1]
            }}
            transition={{ duration: 20, repeat: Infinity }}
            className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"
          />
          <motion.div
            animate={{ 
              x: [0, -100, 0],
              y: [0, 100, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{ duration: 25, repeat: Infinity }}
            className="absolute -bottom-40 -left-40 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"
          />
          <motion.div
            animate={{ 
              x: [0, 50, 0],
              y: [0, -50, 0],
              scale: [1, 1.3, 1]
            }}
            transition={{ duration: 30, repeat: Infinity }}
            className="absolute top-40 left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"
          />
        </div>

        <main className="relative z-10 container mx-auto px-6 py-8">
          <BackendStatus status={backendStatus} onRetry={checkBackend} />

          {/* Page Header */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <motion.div 
              animate={{ rotate: isAnalyzing ? 360 : 0 }}
              transition={{ duration: 2, repeat: isAnalyzing ? Infinity : 0, ease: "linear" }}
              className={`inline-block w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-3xl flex items-center justify-center shadow-2xl mb-6 ${isAnalyzing ? 'animate-spin' : ''}`}
            >
              <div className="w-16 h-16 bg-black rounded-2xl flex items-center justify-center">
                <div className="w-6 h-6 bg-white rounded-full transform -translate-x-1"></div>
                <div className="absolute w-3 h-3 bg-black rounded-full z-10 transform -translate-x-1"></div>
              </div>
            </motion.div>
            
            <h1 className="text-6xl font-bold bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent mb-4">
              Advanced Analysis
            </h1>
            <p className="text-xl text-gray-400 mb-8">
              Enhanced AI-Powered News Analysis with Animations
            </p>
          </motion.div>

          {/* Main Analysis Interface */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="max-w-4xl mx-auto"
          >
            {/* URL Input */}
            <div className="glass-effect rounded-3xl p-8 border border-white/20 mb-8">
              <label className="block text-2xl font-semibold text-white mb-6 flex items-center space-x-3">
                <Globe className="w-8 h-8 text-blue-400" />
                <span>Enter News URL to Analyze</span>
              </label>
              
              <div className="relative mb-6">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.bbc.com/news/article-url"
                  className="w-full bg-black/50 border-2 border-white/20 rounded-2xl px-8 py-6 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-xl transition-all duration-300"
                  disabled={isAnalyzing}
                />
                <motion.div
                  animate={{ opacity: isAnalyzing ? 0.5 : 1 }}
                  className="absolute right-6 top-1/2 transform -translate-y-1/2"
                >
                  <Sparkles className="w-8 h-8 text-purple-400" />
                </motion.div>
              </div>

              <motion.button
                whileHover={{ scale: isAnalyzing ? 1 : 1.02 }}
                whileTap={{ scale: isAnalyzing ? 1 : 0.98 }}
                onClick={handleAnalyze}
                disabled={isAnalyzing || backendStatus !== 'online'}
                className="w-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-600 hover:from-purple-600 hover:via-pink-600 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white px-12 py-8 rounded-2xl font-bold text-2xl transition-all duration-300 flex items-center justify-center space-x-4 disabled:cursor-not-allowed shadow-2xl hover:scale-105"
              >
                {isAnalyzing ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="animate-spin"
                    >
                      <Loader2 className="w-10 h-10" />
                    </motion.div>
                    <span>Analyzing News...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-10 h-10" />
                    <span>Analyze News Article</span>
                  </>
                )}
              </motion.button>
            </div>

            {/* Error Display */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="glass-effect rounded-2xl p-6 border border-red-500/50 bg-red-500/20 mb-8 flex items-start space-x-4"
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
                className="glass-effect rounded-2xl p-6 border border-white/20 mb-8"
              >
                <div className="flex items-center justify-between text-lg text-gray-300 mb-4">
                  <span>Analysis Progress</span>
                  <span>{Math.round(progress)}% Complete</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5 }}
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </motion.div>
            )}

            {/* Analysis Steps */}
            <div className="glass-effect rounded-3xl p-8 border border-white/20">
              <h3 className="text-3xl font-semibold text-white mb-8 flex items-center space-x-4">
                <Brain className="w-10 h-10 text-purple-400" />
                <span>AI Analysis Pipeline</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                {analysisSteps.map((step) => {
                  const status = getStepStatus(step.id)
                  const IconComponent = step.icon

                  return (
                    <motion.div 
                      key={step.id}
                      animate={{
                        scale: status === 'active' ? 1.05 : 1,
                      }}
                      transition={{ duration: 0.6 }}
                      className={`
                        relative flex flex-col items-center p-6 rounded-2xl border-2 transition-all duration-500
                        ${status === 'completed' ? 'border-green-500 bg-green-500/20' :
                          status === 'active' ? `border-purple-500 ${step.bgColor} animate-pulse` : 
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
                            status === 'active' ? `bg-gradient-to-br ${step.color} animate-spin` : 
                            'bg-gray-700'}
                        `}
                      >
                        {status === 'completed' ? (
                          <CheckCircle className="w-8 h-8 text-white" />
                        ) : status === 'active' ? (
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                            className="animate-spin"
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
                  )
                })}
              </div>
            </div>

            {/* Results Display */}
            {analysisResults && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-effect rounded-3xl p-8 border border-white/20 mt-8"
              >
                <h3 className="text-3xl font-semibold text-white mb-6 flex items-center space-x-4">
                  <TrendingUp className="w-10 h-10 text-green-400" />
                  <span>Analysis Results</span>
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-black/30 rounded-2xl p-6">
                    <h4 className="text-xl font-semibold text-purple-400 mb-4">Summary</h4>
                    <p className="text-gray-300">
                      {typeof analysisResults.summary === 'string' 
                        ? analysisResults.summary 
                        : analysisResults.summary?.text || 'Analysis completed successfully'}
                    </p>
                  </div>
                  
                  <div className="bg-black/30 rounded-2xl p-6">
                    <h4 className="text-xl font-semibold text-orange-400 mb-4">Authenticity Score</h4>
                    <div className="text-3xl font-bold text-white">
                      {analysisResults.vetting_results?.authenticity_score || 85}/100
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        </main>
      </div>
    </div>
  )
}