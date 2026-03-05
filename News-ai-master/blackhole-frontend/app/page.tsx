'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/Header'
import NewsAnalysisCard from '@/components/NewsAnalysisCard'
import VideoPlayer from '@/components/VideoPlayer'
import ResultsDisplay from '@/components/ResultsDisplay'
import BackendStatus from '@/components/BackendStatus'
import { checkBackendHealth } from '@/lib/api'

interface AnalysisResults {
  scraped_data?: {
    title?: string
    content_length?: number
    author?: string
    date?: string
    [key: string]: any
  }
  vetting_results?: {
    authenticity_score?: number
    credibility_rating?: string
    is_reliable?: boolean
    [key: string]: any
  }
  summary?: {
    text?: string
    original_length?: number
    summary_length?: number
    compression_ratio?: number
    [key: string]: any
  } | string
  video_prompt?: {
    prompt?: string
    for_video_creation?: boolean
    based_on_summary?: boolean
    [key: string]: any
  }
  sidebar_videos?: {
    videos?: Array<{
      title?: string
      url?: string
      thumbnail?: string
      duration?: string
      source?: string
      [key: string]: any
    }>
    total_found?: number
    ready_for_playback?: boolean
    [key: string]: any
  }
  total_processing_time?: number
  workflow_complete?: boolean
  steps_completed?: number
  [key: string]: any
}

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking')
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    checkBackend()
    const interval = setInterval(checkBackend, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const checkBackend = async () => {
    try {
      const isHealthy = await checkBackendHealth()
      setBackendStatus(isHealthy ? 'online' : 'offline')
    } catch (error) {
      setBackendStatus('offline')
    }
  }

  const handleAnalysisComplete = (results: AnalysisResults) => {
    console.log('📊 Analysis results received:', {
      hasResults: !!results,
      resultKeys: results ? Object.keys(results) : [],
      summary: results?.summary ? 'Present' : 'Missing',
      vettingResults: results?.vetting_results ? 'Present' : 'Missing',
      scrapedData: results?.scraped_data ? 'Present' : 'Missing',
      fullResults: results
    })
    setAnalysisResults(results)
    setIsAnalyzing(false)
    setCurrentStep(0)
  }

  const handleAnalysisStart = () => {
    setIsAnalyzing(true)
    setAnalysisResults(null)
    setCurrentStep(0)

    // Simulate workflow steps for UI feedback
    const steps = ['scraping', 'vetting', 'summarization', 'prompt_generation', 'video_search']
    steps.forEach((_, index) => {
      setTimeout(() => {
        setCurrentStep(index + 1)
      }, (index + 1) * 2000)
    })
  }

  return (
    <div className="min-h-screen">
      <Header backendStatus={backendStatus} />

      <main className="container mx-auto px-6 py-8">
        {/* Backend Status Alert */}
        <BackendStatus status={backendStatus} onRetry={checkBackend} />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          {/* Main Analysis Area */}
          <div className="xl:col-span-3 space-y-8">
            {!analysisResults ? (
              <>
                {/* Hero Section */}
                <div className="text-center space-y-4 mb-12">
                  <div className="relative w-20 h-20 bg-black rounded-full flex items-center justify-center overflow-hidden mx-auto mb-6">
                    <div className="absolute w-14 h-14 bg-white rounded-full transform -translate-x-1"></div>
                    <div className="absolute w-7 h-7 bg-black rounded-full z-10 transform -translate-x-1"></div>
                    <div className="absolute w-24 h-1 bg-gradient-to-r from-transparent via-white to-transparent transform -rotate-30 animate-spin"></div>
                  </div>
                  <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">
                    Blackhole Infiverse LLP
                  </h1>
                  <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                    Advanced AI-powered news analysis platform. Enter any news URL to get instant scraping,
                    authenticity verification, summarization, and related video content.
                  </p>
                </div>

                {/* News Analysis Card */}
                <NewsAnalysisCard
                  onAnalysisStart={handleAnalysisStart}
                  onAnalysisComplete={handleAnalysisComplete}
                  backendOnline={backendStatus === 'online'}
                  isAnalyzing={isAnalyzing}
                  currentStep={currentStep}
                />

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
                  <div className="glass-effect rounded-xl p-6 text-center">
                    <div className="text-3xl mb-4">🔧</div>
                    <h3 className="text-lg font-semibold text-white mb-2">Web Scraping</h3>
                    <p className="text-gray-300 text-sm">
                      Advanced news extraction with fallback mechanisms and dynamic content loading.
                    </p>
                  </div>

                  <div className="glass-effect rounded-xl p-6 text-center">
                    <div className="text-3xl mb-4">⚠️</div>
                    <h3 className="text-lg font-semibold text-white mb-2">Authenticity Vetting</h3>
                    <p className="text-gray-300 text-sm">
                      Enhanced AI-powered credibility analysis with bias detection, source verification, and 
                      intelligent content type detection (articles vs listing pages).
                    </p>
                    <div className="mt-3 flex flex-wrap gap-1 justify-center">
                      <span className="text-xs bg-green-500/20 text-green-300 px-2 py-1 rounded-full">
                        🛡️ Enhanced Analysis
                      </span>
                      <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full">
                        📋 Smart Detection
                      </span>
                    </div>
                  </div>

                  <div className="glass-effect rounded-xl p-6 text-center">
                    <div className="text-3xl mb-4">📝</div>
                    <h3 className="text-lg font-semibold text-white mb-2">Smart Summarization</h3>
                    <p className="text-gray-300 text-sm">
                      Multi-AI summarization using your custom LLM service with intelligent fallbacks.
                    </p>
                  </div>
                </div>
              </>
            ) : (
              /* Results Display */
              <ResultsDisplay results={analysisResults} />
            )}
          </div>

          {/* Video Sidebar */}
          <div className="xl:col-span-1">
            <VideoPlayer
              videos={(analysisResults?.sidebar_videos?.videos || []).filter(video => 
                video && video.title && video.source
              ).map(video => ({
                title: video.title!,
                url: video.url || '',
                thumbnail: video.thumbnail,
                duration: video.duration,
                source: video.source!
              }))}
              title={analysisResults ? "Related Videos" : "Demo Videos"}
            />
          </div>
        </div>

        {/* New Analysis Button (when results are shown) */}
        {analysisResults && (
          <div className="text-center mt-12">
            <button
              onClick={() => {
                setAnalysisResults(null)
                setCurrentStep(0)
              }}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-8 py-4 rounded-lg font-bold text-lg transition-all duration-200 hover:scale-105"
            >
              🔄 Analyze Another News Article
            </button>
          </div>
        )}
      </main>
    </div>
  )
}