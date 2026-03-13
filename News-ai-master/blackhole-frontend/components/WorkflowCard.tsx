'use client'

import { useState } from 'react'
import { Play, Loader2, ExternalLink, AlertCircle } from 'lucide-react'
import { runUnifiedWorkflow } from '@/lib/api'

interface WorkflowCardProps {
  onStart: () => void
  isActive: boolean
  backendOnline: boolean
}

export default function WorkflowCard({ onStart, isActive, backendOnline }: WorkflowCardProps) {
  const [url, setUrl] = useState('https://www.bbc.com/news')
  const [isRunning, setIsRunning] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleRunWorkflow = async () => {
    if (!backendOnline) {
      setError('Backend is offline. Please start the backend server first.')
      return
    }

    if (!url.trim()) {
      setError('Please enter a valid news URL')
      return
    }

    setIsRunning(true)
    setError(null)
    setResults(null)
    onStart()

    try {
      const result = await runUnifiedWorkflow(url)
      
      if (result.success) {
        setResults(result.data)
      } else {
        setError(result.message || 'Workflow failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred')
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="glass-effect rounded-2xl p-8 border border-white/20">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">
            🕳️ Unified News Analysis Workflow
          </h2>
          <p className="text-gray-300">
            Complete pipeline: Web Scraping → Vetting → Summarization → Video Prompts → Sidebar Videos
          </p>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-400">Response Time</div>
          <div className="text-2xl font-bold text-green-400">~12s</div>
        </div>
      </div>

      {/* URL Input */}
      <div className="mb-6">
        <label htmlFor="url" className="block text-sm font-medium text-gray-300 mb-2">
          News URL to Analyze
        </label>
        <div className="flex space-x-3">
          <input
            type="url"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.bbc.com/news/article-url"
            className="flex-1 px-4 py-3 bg-black/50 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            disabled={isRunning}
          />
          <button
            onClick={handleRunWorkflow}
            disabled={isRunning || !backendOnline}
            className={`px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 transition-all duration-200 ${
              isRunning || !backendOnline
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700 hover:scale-105'
            }`}
          >
            {isRunning ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                <span>Run Analysis</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="text-red-400 font-semibold">Error</h4>
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white border-b border-white/20 pb-2">
            Analysis Results
          </h3>
          
          {/* Scraped Data */}
          {results.scraped_data && (
            <div className="bg-black/30 rounded-lg p-4">
              <h4 className="text-purple-400 font-semibold mb-2">🔧 Web Scraping Results</h4>
              <div className="text-sm text-gray-300 space-y-1">
                <p><strong>Title:</strong> {results.scraped_data.title || 'N/A'}</p>
                <p><strong>Content Length:</strong> {results.scraped_data.content_length || 0} characters</p>
                <p><strong>Author:</strong> {results.scraped_data.author || 'N/A'}</p>
                <p><strong>Date:</strong> {results.scraped_data.date || 'N/A'}</p>
              </div>
            </div>
          )}

          {/* Vetting Results */}
          {results.vetting_results && (
            <div className="bg-black/30 rounded-lg p-4">
              <h4 className="text-yellow-400 font-semibold mb-2">⚠️ Authenticity Vetting</h4>
              <div className="text-sm text-gray-300 space-y-1">
                <p><strong>Authenticity Score:</strong> {results.vetting_results.authenticity_score || 0}/100</p>
                <p><strong>Credibility:</strong> {results.vetting_results.credibility_rating || 'N/A'}</p>
                <p><strong>Reliability Status:</strong> {results.vetting_results.reliability_status || (results.vetting_results.is_reliable ? 'Reliable' : 'Questionable')}</p>
                {results.vetting_results.authenticity_level && (
                  <p><strong>Level:</strong> {results.vetting_results.authenticity_level.replace('_', ' ')}</p>
                )}
                {results.vetting_results.confidence && (
                  <p><strong>Confidence:</strong> {Math.round(results.vetting_results.confidence * 100)}%</p>
                )}
              </div>
            </div>
          )}

          {/* Summary */}
          {results.summary && (
            <div className="bg-black/30 rounded-lg p-4">
              <h4 className="text-blue-400 font-semibold mb-2">📝 Summary</h4>
              <div className="text-sm text-gray-300 space-y-2">
                <p className="italic">"{results.summary.text || 'No summary available'}"</p>
                <div className="flex space-x-4 text-xs text-gray-400">
                  <span>Original: {results.summary.original_length || 0} chars</span>
                  <span>Summary: {results.summary.summary_length || 0} chars</span>
                  <span>Compression: {results.summary.compression_ratio || 0}%</span>
                </div>
              </div>
            </div>
          )}

          {/* Video Prompt */}
          {results.video_prompt && (
            <div className="bg-black/30 rounded-lg p-4">
              <h4 className="text-green-400 font-semibold mb-2">💡 Video Generation Prompt</h4>
              <p className="text-sm text-gray-300 italic">
                "{results.video_prompt.prompt?.substring(0, 200) || 'No prompt generated'}..."
              </p>
            </div>
          )}

          {/* Performance Stats */}
          <div className="bg-black/30 rounded-lg p-4">
            <h4 className="text-cyan-400 font-semibold mb-2">⏱️ Performance</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm text-gray-300">
              <div>
                <span className="text-gray-400">Total Time:</span>
                <div className="font-semibold">{results.total_processing_time || 0}s</div>
              </div>
              <div>
                <span className="text-gray-400">Steps:</span>
                <div className="font-semibold">{results.steps_completed || 0}/5</div>
              </div>
              <div>
                <span className="text-gray-400">Videos Found:</span>
                <div className="font-semibold">{results.sidebar_videos?.total_found || 0}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Status Indicators */}
      <div className="flex items-center justify-between mt-6 pt-4 border-t border-white/20">
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-gray-400">
              {backendOnline ? 'Backend Online' : 'Backend Offline'}
            </span>
          </div>
          {isActive && (
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
              <span className="text-purple-400">Workflow Active</span>
            </div>
          )}
        </div>
        
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center space-x-1 text-sm text-gray-400 hover:text-white transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          <span>API Docs</span>
        </a>
      </div>
    </div>
  )
}
