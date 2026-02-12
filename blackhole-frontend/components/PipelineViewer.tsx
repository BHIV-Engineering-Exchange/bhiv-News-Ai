'use client'

import { CheckCircle, Clock, Loader2, AlertCircle } from 'lucide-react'

interface PipelineStep {
  status: 'completed' | 'processing' | 'pending' | 'failed'
  timestamp: string | null
}

interface PipelineData {
  fetched: PipelineStep
  filtered: PipelineStep
  summarized: PipelineStep
  verified: PipelineStep
  scripted: PipelineStep
  voiced: PipelineStep
}

interface PipelineViewerProps {
  pipeline: PipelineData
  compact?: boolean
}

const PIPELINE_STEPS = [
  { key: 'fetched', label: 'Fetched', description: 'News content retrieved', icon: '🌐' },
  { key: 'filtered', label: 'Filtered', description: 'Content cleaned & filtered', icon: '🔍' },
  { key: 'summarized', label: 'Summarized', description: 'AI summary generated', icon: '📝' },
  { key: 'verified', label: 'Verified', description: 'Authenticity checked', icon: '✓' },
  { key: 'scripted', label: 'Scripted', description: 'TTS script created', icon: '📄' },
  { key: 'voiced', label: 'Voiced', description: 'Audio generated', icon: '🔊' }
]

export default function PipelineViewer({ pipeline, compact = false }: PipelineViewerProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'processing':
        return <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-400" />
      case 'pending':
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-400 bg-green-400/10'
      case 'processing':
        return 'border-purple-400 bg-purple-400/10 animate-pulse'
      case 'failed':
        return 'border-red-400 bg-red-400/10'
      case 'pending':
      default:
        return 'border-gray-600 bg-gray-600/10'
    }
  }

  const getConnectorColor = (currentStatus: string, nextStatus: string) => {
    if (currentStatus === 'completed' && (nextStatus === 'completed' || nextStatus === 'processing')) {
      return 'bg-gradient-to-r from-green-400 to-purple-400'
    }
    if (currentStatus === 'completed') {
      return 'bg-green-400'
    }
    if (currentStatus === 'processing') {
      return 'bg-purple-400'
    }
    return 'bg-gray-600'
  }

  const formatTimestamp = (timestamp: string | null) => {
    if (!timestamp) return 'Pending'
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }

  if (compact) {
    return (
      <div className="flex items-center space-x-2">
        {PIPELINE_STEPS.map((step, index) => {
          const stepData = pipeline[step.key as keyof PipelineData]
          return (
            <div key={step.key} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full border-2 ${getStatusColor(stepData.status)} flex items-center justify-center`}
                title={`${step.label}: ${stepData.status}`}
              >
                <span className="text-xs">{step.icon}</span>
              </div>
              {index < PIPELINE_STEPS.length - 1 && (
                <div className={`w-4 h-0.5 ${getConnectorColor(stepData.status, pipeline[PIPELINE_STEPS[index + 1].key as keyof PipelineData].status)}`} />
              )}
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="glass-effect rounded-xl p-6 border border-white/20">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white mb-1">AI Processing Pipeline</h3>
        <p className="text-sm text-gray-400">Real-time workflow tracking</p>
      </div>

      {/* Pipeline Steps */}
      <div className="space-y-4">
        {PIPELINE_STEPS.map((step, index) => {
          const stepData = pipeline[step.key as keyof PipelineData]
          const isLast = index === PIPELINE_STEPS.length - 1

          return (
            <div key={step.key} className="relative">
              {/* Step Content */}
              <div className={`border-2 rounded-lg p-4 transition-all ${getStatusColor(stepData.status)}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {/* Icon */}
                    <div className="flex-shrink-0">
                      {getStatusIcon(stepData.status)}
                    </div>

                    {/* Text */}
                    <div>
                      <div className="flex items-center space-x-2">
                        <h4 className="font-semibold text-white">{step.label}</h4>
                        <span className="text-2xl">{step.icon}</span>
                      </div>
                      <p className="text-sm text-gray-400">{step.description}</p>
                    </div>
                  </div>

                  {/* Status & Time */}
                  <div className="text-right">
                    <div className={`text-xs font-semibold uppercase ${
                      stepData.status === 'completed' ? 'text-green-400' :
                      stepData.status === 'processing' ? 'text-purple-400' :
                      stepData.status === 'failed' ? 'text-red-400' :
                      'text-gray-500'
                    }`}>
                      {stepData.status}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {formatTimestamp(stepData.timestamp)}
                    </div>
                  </div>
                </div>

                {/* Progress bar for processing state */}
                {stepData.status === 'processing' && (
                  <div className="mt-3">
                    <div className="w-full bg-gray-700 rounded-full h-1 overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full animate-pulse" style={{ width: '60%' }} />
                    </div>
                  </div>
                )}
              </div>

              {/* Connector Line */}
              {!isLast && (
                <div className="flex justify-center my-2">
                  <div className={`w-0.5 h-4 ${getConnectorColor(
                    stepData.status,
                    pipeline[PIPELINE_STEPS[index + 1].key as keyof PipelineData].status
                  )}`} />
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 pt-6 border-t border-white/10">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-green-400">
              {PIPELINE_STEPS.filter(s => pipeline[s.key as keyof PipelineData].status === 'completed').length}
            </div>
            <div className="text-xs text-gray-500">Completed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-400">
              {PIPELINE_STEPS.filter(s => pipeline[s.key as keyof PipelineData].status === 'processing').length}
            </div>
            <div className="text-xs text-gray-500">Processing</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-500">
              {PIPELINE_STEPS.filter(s => pipeline[s.key as keyof PipelineData].status === 'pending').length}
            </div>
            <div className="text-xs text-gray-500">Pending</div>
          </div>
        </div>
      </div>
    </div>
  )
}

