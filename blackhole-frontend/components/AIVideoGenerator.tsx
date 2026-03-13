'use client'

import React, { useState, useEffect } from 'react'
import { Play, Download, Settings, Zap, Video, Clock, CheckCircle, AlertCircle, ExternalLink } from 'lucide-react'

interface AIVideoGeneratorProps {
  newsData: any
  onVideoGenerated?: (videoData: any) => void
}

interface AIVideoStatus {
  services: {
    ngrok_tunnel: { url: string; status: string }
    local_ai: { url: string; status: string }
    web_interface: { url: string; status: string }
  }
  capabilities: string[]
  supported_styles: string[]
}

export default function AIVideoGenerator({ newsData, onVideoGenerated }: AIVideoGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedVideo, setGeneratedVideo] = useState<any>(null)
  const [selectedStyle, setSelectedStyle] = useState('news_report')
  const [aiStatus, setAiStatus] = useState<AIVideoStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showAdvanced, setShowAdvanced] = useState(false)

  useEffect(() => {
    checkAIStatus()
  }, [])

  const checkAIStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/ai-video-status')
      const result = await response.json()
      if (result.success) {
        setAiStatus(result.data)
      }
    } catch (error) {
      console.error('Failed to check AI status:', error)
    }
  }

  const generateAIVideo = async () => {
    if (!newsData) {
      setError('No news data available for video generation')
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/api/generate-ai-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          news_data: newsData,
          style: selectedStyle
        })
      })

      const result = await response.json()
      
      if (result.success && result.data.success) {
        setGeneratedVideo(result.data)
        onVideoGenerated?.(result.data)
      } else {
        setError(result.data.error || 'Video generation failed')
      }
    } catch (error) {
      setError('Failed to generate AI video')
      console.error('AI video generation error:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'offline':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      default:
        return <Clock className="w-4 h-4 text-yellow-400" />
    }
  }

  const getStyleDescription = (style: string) => {
    const descriptions = {
      news_report: 'Professional news presentation with formal graphics',
      breaking_news: 'Urgent, attention-grabbing style with dynamic elements',
      documentary: 'In-depth analysis with slower pacing and detailed explanations',
      social_media: 'Vertical format optimized for social platforms'
    }
    return descriptions[style as keyof typeof descriptions] || 'Standard video style'
  }

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-600/20 rounded-lg">
            <Zap className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">AI Video Generator</h3>
            <p className="text-gray-400 text-sm">Create AI-powered videos from news content</p>
          </div>
        </div>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
        >
          <Settings className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      {/* AI Service Status */}
      {aiStatus && (
        <div className="mb-6 p-4 bg-gray-800/50 rounded-lg">
          <h4 className="text-sm font-semibold text-white mb-3">AI Services Status</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {Object.entries(aiStatus.services).map(([key, service]) => (
              <div key={key} className="flex items-center justify-between p-2 bg-gray-700/30 rounded">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(service.status)}
                  <span className="text-sm text-gray-300 capitalize">
                    {key.replace('_', ' ')}
                  </span>
                </div>
                {service.status === 'online' && key === 'web_interface' && (
                  <a
                    href={service.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Video Style Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-3">Video Style</label>
        <div className="grid grid-cols-2 gap-3">
          {aiStatus?.supported_styles.map((style) => (
            <button
              key={style}
              onClick={() => setSelectedStyle(style)}
              className={`p-3 rounded-lg border text-left transition-all ${
                selectedStyle === style
                  ? 'border-purple-500 bg-purple-500/20 text-white'
                  : 'border-gray-600 bg-gray-800/50 text-gray-300 hover:border-gray-500'
              }`}
            >
              <div className="font-medium capitalize">{style.replace('_', ' ')}</div>
              <div className="text-xs text-gray-400 mt-1">
                {getStyleDescription(style)}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="mb-6 p-4 bg-gray-800/30 rounded-lg">
          <h4 className="text-sm font-semibold text-white mb-3">Advanced Options</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Duration</label>
              <select className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white text-sm">
                <option value="30">30 seconds</option>
                <option value="60">1 minute</option>
                <option value="90">1.5 minutes</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Resolution</label>
              <select className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white text-sm">
                <option value="720p">720p HD</option>
                <option value="1080p">1080p Full HD</option>
                <option value="4k">4K Ultra HD</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Generation Button */}
      <button
        onClick={generateAIVideo}
        disabled={isGenerating || !newsData}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center space-x-2 ${
          isGenerating
            ? 'bg-purple-600/50 text-purple-200 cursor-not-allowed'
            : 'bg-purple-600 hover:bg-purple-700 text-white'
        }`}
      >
        {isGenerating ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-purple-200 border-t-transparent"></div>
            <span>Generating AI Video...</span>
          </>
        ) : (
          <>
            <Video className="w-4 h-4" />
            <span>Generate AI Video</span>
          </>
        )}
      </button>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-3 bg-red-900/30 border border-red-700 rounded-lg">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <span className="text-red-300 text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* Generated Video Display */}
      {generatedVideo && (
        <div className="mt-6 p-4 bg-green-900/20 border border-green-700 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span className="text-green-300 font-medium">Video Generated Successfully!</span>
            </div>
            <span className="text-xs text-gray-400">
              {generatedVideo.generation_method}
            </span>
          </div>
          
          {generatedVideo.video_data?.video_url ? (
            <div className="space-y-3">
              <video
                controls
                className="w-full rounded-lg"
                src={generatedVideo.video_data.video_url}
              >
                Your browser does not support the video tag.
              </video>
              <div className="flex space-x-2">
                <button className="flex items-center space-x-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                  <Play className="w-4 h-4" />
                  <span>Play</span>
                </button>
                <button className="flex items-center space-x-2 px-3 py-2 bg-gray-600 hover:bg-gray-700 rounded text-sm">
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="p-3 bg-gray-800/50 rounded">
                <h5 className="text-sm font-medium text-white mb-2">Video Instructions Generated</h5>
                <p className="text-xs text-gray-400">
                  AI video creation instructions have been generated. Use the provided script and directions to create your video.
                </p>
              </div>
              {generatedVideo.video_instructions && (
                <div className="text-xs text-gray-300">
                  <strong>Style:</strong> {generatedVideo.video_instructions.style}<br/>
                  <strong>Duration:</strong> {generatedVideo.video_instructions.duration}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
