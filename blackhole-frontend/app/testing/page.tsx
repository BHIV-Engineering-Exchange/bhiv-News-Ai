'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/Header'
import BackendStatus from '@/components/BackendStatus'
import { checkBackendHealth, testIndividualTool } from '@/lib/api'
import { Play, CheckCircle, XCircle, Loader2, Globe, Shield, FileText, Lightbulb, Video } from 'lucide-react'

export default function Testing() {
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking')
  const [testResults, setTestResults] = useState<{ [key: string]: any }>({})
  const [runningTests, setRunningTests] = useState<{ [key: string]: boolean }>({})

  useEffect(() => {
    checkBackend()
    const interval = setInterval(checkBackend, 30000)
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

  const tools = [
    {
      id: 'scraping',
      name: 'Web Scraping',
      icon: Globe,
      description: 'Test news article scraping functionality',
      testPayload: { url: 'https://httpbin.org/html' },
      color: 'text-blue-400'
    },
    {
      id: 'vetting',
      name: 'Authenticity Vetting',
      icon: Shield,
      description: 'Test news authenticity verification',
      testPayload: { 
        data: {
          content: 'This is a test news article about technology. It discusses recent developments in artificial intelligence and machine learning. The article mentions various companies and their contributions to the field.',
          title: 'Test Technology Article',
          url: 'https://example.com/test-article',
          source: 'Test News Source'
        },
        criteria: {
          content_length: { min: 10, max: 10000 },
          check_sources: true,
          check_bias: true,
          check_authenticity: true
        }
      },
      color: 'text-orange-400'
    },
    {
      id: 'summarization',
      name: 'AI Summarization',
      icon: FileText,
      description: 'Test intelligent content summarization',
      testPayload: { 
        text: 'This is a comprehensive test article that needs to be summarized effectively. It contains multiple paragraphs discussing various aspects of technology, including artificial intelligence, machine learning, and their applications in different industries. The article explores how these technologies are transforming businesses and creating new opportunities for innovation. It also discusses the challenges and ethical considerations that come with implementing AI solutions in real-world scenarios. The content covers recent developments, future trends, and the impact on society as a whole.',
        max_length: 150
      },
      color: 'text-green-400'
    },
    {
      id: 'prompt',
      name: 'Prompt Generation',
      icon: Lightbulb,
      description: 'Test AI video prompt generation',
      testPayload: { 
        task_type: 'video_creation',
        subject: 'Recent developments in artificial intelligence and machine learning algorithms for business efficiency',
        style: 'professional',
        tone: 'neutral',
        length: 'medium',
        additional_context: 'Focus on creating engaging video content about AI technology trends',
        include_examples: false
      },
      color: 'text-yellow-400'
    },
    {
      id: 'video',
      name: 'Video Search',
      icon: Video,
      description: 'Test related video discovery',
      testPayload: {
        query: 'artificial intelligence technology news',
        max_results: 5,
        duration: 'any'
      },
      color: 'text-red-400'
    },
    {
      id: 'validate-video',
      name: 'Video Validation',
      icon: CheckCircle,
      description: 'Test video availability validation',
      testPayload: {
        video_id: 'dQw4w9WgXcQ',  // Rick Roll - should always be available
        video_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
      },
      color: 'text-purple-400'
    }
  ]

  const runTest = async (toolId: string) => {
    if (!backendStatus || backendStatus === 'offline') {
      alert('Backend is offline. Please start the backend server first.')
      return
    }

    const tool = tools.find(t => t.id === toolId)
    if (!tool) return

    setRunningTests(prev => ({ ...prev, [toolId]: true }))
    
    try {
      console.log(`🧪 Testing ${tool.name}...`)
      console.log(`📤 Sending payload:`, JSON.stringify(tool.testPayload, null, 2))
      
      const result = await testIndividualTool(toolId, tool.testPayload)
      console.log(`✅ ${tool.name} test result:`, result)
      
      setTestResults(prev => ({
        ...prev,
        [toolId]: {
          success: true,
          data: result,
          timestamp: new Date().toLocaleTimeString(),
          payload: tool.testPayload
        }
      }))
    } catch (error: any) {
      console.error(`❌ ${tool.name} test failed:`, error)
      console.error(`📤 Failed payload was:`, JSON.stringify(tool.testPayload, null, 2))
      
      setTestResults(prev => ({
        ...prev,
        [toolId]: {
          success: false,
          error: error.message || 'Test failed',
          timestamp: new Date().toLocaleTimeString(),
          payload: tool.testPayload
        }
      }))
    } finally {
      setRunningTests(prev => ({ ...prev, [toolId]: false }))
    }
  }

  const runAllTests = async () => {
    for (const tool of tools) {
      await runTest(tool.id)
      // Add a small delay between tests
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
  }

  const getTestStatus = (toolId: string) => {
    if (runningTests[toolId]) return 'running'
    if (!testResults[toolId]) return 'pending'
    return testResults[toolId].success ? 'success' : 'failed'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-gray-600" />
    }
  }

  return (
    <div className="min-h-screen">
      <Header backendStatus={backendStatus} />

      <main className="container mx-auto px-6 py-8">
        <BackendStatus status={backendStatus} onRetry={checkBackend} />

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🧪 Testing Suite</h1>
          <p className="text-gray-400">Test individual components of the AI news analysis system</p>
        </div>

        {/* Test Controls */}
        <div className="mb-8 glass-effect rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white mb-2">Test Controls</h2>
              <p className="text-gray-400">Run individual tests or test all components at once</p>
            </div>
            <button
              onClick={runAllTests}
              disabled={Object.values(runningTests).some(Boolean) || backendStatus !== 'online'}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-gray-600 disabled:to-gray-700 text-white px-6 py-3 rounded-lg font-bold transition-all duration-200 flex items-center space-x-2 disabled:cursor-not-allowed"
            >
              <Play className="w-5 h-5" />
              <span>Run All Tests</span>
            </button>
          </div>
        </div>

        {/* Test Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tools.map((tool) => {
            const status = getTestStatus(tool.id)
            const result = testResults[tool.id]

            return (
              <div key={tool.id} className="glass-effect rounded-xl p-6 border border-white/20">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <tool.icon className={`w-8 h-8 ${tool.color}`} />
                    <div>
                      <h3 className="text-lg font-semibold text-white">{tool.name}</h3>
                      <p className="text-sm text-gray-400">{tool.description}</p>
                    </div>
                  </div>
                  {getStatusIcon(status)}
                </div>

                {/* Test Payload Preview */}
                <div className="mb-4 p-3 bg-black/30 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Test Payload:</h4>
                  <pre className="text-xs text-gray-400 overflow-x-auto">
                    {JSON.stringify(tool.testPayload, null, 2)}
                  </pre>
                </div>

                {/* Test Result */}
                {result && (
                  <div className={`mb-4 p-3 rounded-lg ${
                    result.success ? 'bg-green-500/20 border border-green-500/50' : 'bg-red-500/20 border border-red-500/50'
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className={`font-medium ${result.success ? 'text-green-400' : 'text-red-400'}`}>
                        {result.success ? 'Test Passed' : 'Test Failed'}
                      </span>
                      <span className="text-xs text-gray-400">{result.timestamp}</span>
                    </div>
                    {result.error && (
                      <div>
                        <p className="text-sm text-red-300 mb-2">{result.error}</p>
                        <details className="text-xs">
                          <summary className="text-red-400 cursor-pointer">Show payload details</summary>
                          <pre className="mt-2 text-red-200 bg-red-900/20 p-2 rounded">
                            {JSON.stringify(result.payload, null, 2)}
                          </pre>
                        </details>
                      </div>
                    )}
                    {result.success && result.data && (
                      <div>
                        <p className="text-sm text-green-300 mb-2">Response received successfully</p>
                        <details className="text-xs">
                          <summary className="text-green-400 cursor-pointer">Show response details</summary>
                          <pre className="mt-2 text-green-200 bg-green-900/20 p-2 rounded max-h-32 overflow-y-auto">
                            {JSON.stringify(result.data, null, 2)}
                          </pre>
                        </details>
                      </div>
                    )}
                  </div>
                )}

                {/* Test Button */}
                <button
                  onClick={() => runTest(tool.id)}
                  disabled={runningTests[tool.id] || backendStatus !== 'online'}
                  className="w-full bg-black/50 hover:bg-black/70 disabled:bg-gray-800 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2 disabled:cursor-not-allowed"
                >
                  {runningTests[tool.id] ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Testing...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span>Run Test</span>
                    </>
                  )}
                </button>
              </div>
            )
          })}
        </div>

        {/* Test Logs */}
        <div className="mt-8 glass-effect rounded-xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-4">Test Logs</h2>
          <div className="bg-black/50 rounded-lg p-4 font-mono text-sm max-h-64 overflow-y-auto">
            <div className="text-gray-400">
              {Object.keys(testResults).length === 0 ? (
                'No tests run yet. Click "Run Test" on any component to start testing.'
              ) : (
                Object.entries(testResults).map(([toolId, result]) => {
                  const tool = tools.find(t => t.id === toolId)
                  return (
                    <div key={toolId} className="mb-2">
                      <span className="text-gray-500">[{result.timestamp}]</span>{' '}
                      <span className={result.success ? 'text-green-400' : 'text-red-400'}>
                        {tool?.name}: {result.success ? 'PASS' : 'FAIL'}
                      </span>
                      {result.error && (
                        <div className="ml-4 text-red-300">Error: {result.error}</div>
                      )}
                    </div>
                  )
                })
              )}
            </div>
          </div>
        </div>

        {/* API Documentation */}
        <div className="mt-8 glass-effect rounded-xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-4">API Endpoint Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            {tools.map((tool) => (
              <div key={tool.id} className="bg-black/30 rounded-lg p-4">
                <h3 className={`font-medium mb-2 ${tool.color}`}>{tool.name}</h3>
                <p className="text-gray-400 mb-2">
                  <strong>Endpoint:</strong> /api/{tool.id === 'vetting' ? 'vet' : tool.id === 'summarization' ? 'summarize' : tool.id === 'prompt' ? 'prompt' : tool.id === 'video' ? 'video-search' : tool.id === 'validate-video' ? 'validate-video' : 'scrape'}
                </p>
                <p className="text-gray-400">
                  <strong>Method:</strong> POST
                </p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}