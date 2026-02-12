'use client'

import { AlertTriangle, CheckCircle, RefreshCw, Terminal, ExternalLink } from 'lucide-react'

interface BackendStatusProps {
  status: 'online' | 'offline' | 'checking'
  onRetry: () => void
}

export default function BackendStatus({ status, onRetry }: BackendStatusProps) {
  if (status === 'online') {
    return (
      <div className="mb-8 bg-green-500/20 border border-green-500/50 rounded-lg p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
          <div>
            <h4 className="text-green-400 font-medium">Backend Online</h4>
            <p className="text-green-300 text-sm">
              All services are operational and ready to process requests.
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-green-400 hover:text-green-300 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
          <button
            onClick={onRetry}
            className="text-green-400 hover:text-green-300 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>
    )
  }

  if (status === 'checking') {
    return (
      <div className="mb-8 bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <RefreshCw className="w-5 h-5 text-yellow-400 animate-spin flex-shrink-0" />
          <div>
            <h4 className="text-yellow-400 font-medium">Checking Backend Status</h4>
            <p className="text-yellow-300 text-sm">
              Connecting to backend services...
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Offline status
  return (
    <div className="mb-8 bg-red-500/20 border border-red-500/50 rounded-lg p-6">
      <div className="flex items-start space-x-3">
        <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="text-red-400 font-medium mb-2">Backend Offline</h4>
          <p className="text-red-300 text-sm mb-4">
            The Blackhole Infiverse LLP backend server is not responding. 
            Please start the backend to use the unified workflow.
          </p>
          
          {/* Instructions */}
          <div className="bg-black/30 rounded-lg p-4 mb-4">
            <h5 className="text-white font-medium mb-2 flex items-center">
              <Terminal className="w-4 h-4 mr-2" />
              Start Backend Server:
            </h5>
            <div className="space-y-2 text-sm font-mono">
              <div className="text-gray-300">
                <span className="text-gray-500">1.</span> cd unified_tools_backend
              </div>
              <div className="text-gray-300">
                <span className="text-gray-500">2.</span> pip install -r requirements.txt
              </div>
              <div className="text-gray-300">
                <span className="text-gray-500">3.</span> python -m uvicorn main:app --reload --port 8000
              </div>
            </div>
          </div>

          {/* Expected URLs */}
          <div className="bg-black/30 rounded-lg p-4 mb-4">
            <h5 className="text-white font-medium mb-2">Expected URLs:</h5>
            <div className="space-y-1 text-sm">
              <div className="text-gray-300">
                🌐 API: <code className="text-blue-400">http://localhost:8000</code>
              </div>
              <div className="text-gray-300">
                📚 Docs: <code className="text-blue-400">http://localhost:8000/docs</code>
              </div>
              <div className="text-gray-300">
                ❤️ Health: <code className="text-blue-400">http://localhost:8000/health</code>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onRetry}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Retry Connection</span>
            </button>
            
            <a
              href="http://localhost:8000"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
            >
              <ExternalLink className="w-4 h-4" />
              <span>Test Backend</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
