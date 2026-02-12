'use client'

import { useState, useEffect } from 'react'
import { Play, Loader2, AlertCircle, CheckCircle, Globe, Shield, FileText, Lightbulb, Video } from 'lucide-react'
import { runUnifiedWorkflow } from '@/lib/api'

interface NewsAnalysisCardProps {
  onAnalysisStart: (url: string) => void
  onAnalysisComplete: (results: any) => void
  backendOnline: boolean
  isAnalyzing: boolean
  currentStep: number
  initialUrl?: string
}

const steps = [
  { id: 1, name: 'Web Scraping', icon: Globe, description: 'Fetching news data from URL' },
  { id: 2, name: 'Vetting Agent', icon: Shield, description: 'Verifying authenticity and credibility' },
  { id: 3, name: 'Summarization', icon: FileText, description: 'Creating intelligent summary' },
  { id: 4, name: 'Prompt Generation', icon: Lightbulb, description: 'Generating video prompts' },
  { id: 5, name: 'Video Search', icon: Video, description: 'Finding related videos' }
]

export default function NewsAnalysisCard({ 
  onAnalysisStart, 
  onAnalysisComplete, 
  backendOnline, 
  isAnalyzing, 
  currentStep,
  initialUrl 
}: NewsAnalysisCardProps) {
  const [url, setUrl] = useState(initialUrl || 'https://httpbin.org/html')
  const [error, setError] = useState<string | null>(null)
  
  // Update URL when initialUrl prop changes
  useEffect(() => {
    if (initialUrl) {
      setUrl(initialUrl)
    }
  }, [initialUrl])

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
    onAnalysisStart(url)

    try {
      console.log('🚀 Starting analysis for URL:', url)
      const response = await runUnifiedWorkflow(url)
      console.log('📥 Analysis response received:', {
        success: response.success,
        message: response.message,
        hasData: !!response.data,
        dataKeys: response.data ? Object.keys(response.data) : []
      })
      
      if (response.success) {
        console.log('✅ Analysis successful!')
        if (response.data) {
          console.log('📊 Response data structure:', Object.keys(response.data))
          onAnalysisComplete(response.data)
        } else {
          console.warn('⚠️ Success but no data received')
          setError('Analysis completed but no data was returned')
          onAnalysisComplete(null)
        }
      } else {
        const errorMessage = response.message || 'Analysis failed'
        console.error('❌ Analysis failed:', errorMessage)
        console.error('📋 Full error response:', response)
        setError(errorMessage)
        onAnalysisComplete(null)
      }
    } catch (err: any) {
      console.error('💥 Analysis error caught:', err)
      console.error('🔍 Error type:', typeof err)
      console.error('📝 Error message:', err.message)
      const errorMessage = err.message || 'Failed to analyze news'
      setError(errorMessage)
      onAnalysisComplete(null)
    }
  }

  const getStepStatus = (stepId: number) => {
    if (!isAnalyzing) return 'pending'
    if (stepId < currentStep) return 'completed'
    if (stepId === currentStep) return 'active'
    return 'pending'
  }

  const getStepIcon = (step: typeof steps[0], status: string) => {
    const IconComponent = step.icon
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-400" />
      case 'active':
        return <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
      default:
        return <IconComponent className="w-6 h-6 text-gray-500" />
    }
  }

  const getStepClasses = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 border-green-500/50 text-green-400'
      case 'active':
        return 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 border-purple-500/50 text-purple-400 animate-pulse'
      default:
        return 'bg-gray-800/50 border-gray-700 text-gray-500'
    }
  }

  return (
    <div className="glass-effect rounded-2xl p-8 border border-white/20">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
            <span className="text-2xl">🕳️</span>
          </div>
          <div>
            <h2 className="text-3xl font-bold text-white">Blackhole Infiverse LLP</h2>
            <p className="text-gray-400">Advanced AI News Analysis System</p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-sm text-gray-400">System Status</div>
          <div className={`flex items-center space-x-2 ${backendOnline ? 'text-green-400' : 'text-red-400'}`}>
            <div className={`w-3 h-3 rounded-full ${backendOnline ? 'bg-green-400' : 'bg-red-400'} ${backendOnline ? 'animate-pulse' : ''}`}></div>
            <span className="text-sm font-medium">
              {backendOnline ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* URL Input */}
      <div className="mb-8">
        <label className="block text-lg font-medium text-white mb-3">
          📰 Enter News URL to Analyze
        </label>
        <div className="flex space-x-4">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.bbc.com/news/article-url"
            className="flex-1 bg-black/50 border border-white/20 rounded-lg px-6 py-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg"
            disabled={isAnalyzing}
          />
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || !backendOnline}
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-gray-600 disabled:to-gray-700 text-white px-10 py-4 rounded-lg font-bold text-lg transition-all duration-200 flex items-center space-x-3 disabled:cursor-not-allowed min-w-[200px] justify-center"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Play className="w-6 h-6" />
                <span>Analyze News</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-8 bg-red-500/20 border border-red-500/50 rounded-lg p-6 flex items-start space-x-4">
          <AlertCircle className="w-6 h-6 text-red-400 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="text-red-400 font-medium text-lg">Analysis Error</h4>
            <p className="text-red-300 mt-1">{error}</p>
            <p className="text-red-200 mt-2 text-sm">
              Try using a different URL or check the browser console for more details.
            </p>
          </div>
        </div>
      )}

      {/* Workflow Steps */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-white mb-6">AI Analysis Pipeline</h3>
        
        {/* Desktop View - Horizontal */}
        <div className="hidden md:flex items-center justify-between">
          {steps.map((step, index) => {
            const status = getStepStatus(step.id)
            const isLast = index === steps.length - 1

            return (
              <div key={step.id} className="flex items-center flex-1">
                {/* Step Circle */}
                <div className={`
                  relative flex items-center justify-center w-16 h-16 rounded-full border-2 transition-all duration-500
                  ${getStepClasses(status)}
                `}>
                  {getStepIcon(step, status)}
                  
                  {/* Step Number */}
                  <div className="absolute -top-2 -right-2 w-7 h-7 bg-gray-800 border border-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-gray-400">{step.id}</span>
                  </div>
                </div>

                {/* Step Info */}
                <div className="ml-6 flex-1">
                  <div className={`font-semibold text-lg transition-colors duration-300 ${
                    status === 'completed' ? 'text-green-400' :
                    status === 'active' ? 'text-purple-400' : 'text-gray-500'
                  }`}>
                    {step.name}
                  </div>
                  <div className="text-sm text-gray-400 mt-1">
                    {step.description}
                  </div>
                </div>

                {/* Connector Line */}
                {!isLast && (
                  <div className="flex-1 mx-6">
                    <div className={`h-1 transition-all duration-500 rounded ${
                      status === 'completed' ? 'bg-green-500' :
                      status === 'active' ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-gray-700'
                    }`}></div>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Mobile View - Vertical */}
        <div className="md:hidden space-y-6">
          {steps.map((step, index) => {
            const status = getStepStatus(step.id)
            const isLast = index === steps.length - 1

            return (
              <div key={step.id} className="flex items-start">
                {/* Step Circle and Line */}
                <div className="flex flex-col items-center mr-6">
                  <div className={`
                    flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-500
                    ${getStepClasses(status)}
                  `}>
                    {getStepIcon(step, status)}
                  </div>
                  
                  {!isLast && (
                    <div className={`w-1 h-12 mt-3 transition-all duration-500 rounded ${
                      status === 'completed' ? 'bg-green-500' :
                      status === 'active' ? 'bg-gradient-to-b from-purple-500 to-pink-500' : 'bg-gray-700'
                    }`}></div>
                  )}
                </div>

                {/* Step Info */}
                <div className="flex-1 pb-6">
                  <div className={`font-semibold text-lg transition-colors duration-300 ${
                    status === 'completed' ? 'text-green-400' :
                    status === 'active' ? 'text-purple-400' : 'text-gray-500'
                  }`}>
                    {step.name}
                  </div>
                  <div className="text-sm text-gray-400 mt-1">
                    {step.description}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Progress Summary */}
      {isAnalyzing && (
        <div className="bg-black/30 rounded-lg p-6">
          <div className="flex items-center justify-between text-lg mb-4">
            <div className="text-purple-400 font-semibold">
              🔄 Processing News Analysis...
            </div>
            <div className="text-purple-400 font-bold">
              {Math.round((currentStep / steps.length) * 100)}% Complete
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div 
              className="h-3 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
              style={{ 
                width: `${(currentStep / steps.length) * 100}%` 
              }}
            ></div>
          </div>
        </div>
      )}
    </div>
  )
}