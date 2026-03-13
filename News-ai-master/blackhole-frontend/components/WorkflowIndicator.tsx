'use client'

import { CheckCircle, Circle, Loader2 } from 'lucide-react'

interface WorkflowIndicatorProps {
  currentStep: number
  isActive: boolean
}

const steps = [
  { id: 1, name: 'Scrape URL', icon: '🔧', description: 'Extract news content' },
  { id: 2, name: 'Vet News', icon: '⚠️', description: 'Analyze authenticity' },
  { id: 3, name: 'Summarize', icon: '📝', description: 'Generate summary' },
  { id: 4, name: 'Generate Prompt', icon: '💡', description: 'Create video prompt' },
  { id: 5, name: 'Find Videos', icon: '📹', description: 'Search related videos' }
]

export default function WorkflowIndicator({ currentStep, isActive }: WorkflowIndicatorProps) {
  const getStepStatus = (stepId: number) => {
    if (!isActive) return 'pending'
    if (stepId < currentStep) return 'completed'
    if (stepId === currentStep) return 'active'
    return 'pending'
  }

  const getStepIcon = (step: typeof steps[0], status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'active':
        return <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
      default:
        return <Circle className="w-5 h-5 text-gray-500" />
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
    <div className="glass-effect rounded-xl p-6 border border-white/20">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Workflow Progress</h3>
        <div className="text-sm text-gray-400">
          {isActive ? `Step ${currentStep}/5` : 'Ready to start'}
        </div>
      </div>

      {/* Desktop View - Horizontal */}
      <div className="hidden md:block">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const status = getStepStatus(step.id)
            const isLast = index === steps.length - 1

            return (
              <div key={step.id} className="flex items-center flex-1">
                {/* Step Circle */}
                <div className={`
                  relative flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-500
                  ${getStepClasses(status)}
                `}>
                  {getStepIcon(step, status)}
                  
                  {/* Step Number */}
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-gray-800 border border-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-xs font-medium text-gray-400">{step.id}</span>
                  </div>
                </div>

                {/* Step Info */}
                <div className="ml-4 flex-1">
                  <div className={`font-medium transition-colors duration-300 ${
                    status === 'completed' ? 'text-green-400' :
                    status === 'active' ? 'text-purple-400' : 'text-gray-500'
                  }`}>
                    {step.icon} {step.name}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    {step.description}
                  </div>
                </div>

                {/* Connector Line */}
                {!isLast && (
                  <div className="flex-1 mx-4">
                    <div className={`h-0.5 transition-all duration-500 ${
                      status === 'completed' ? 'bg-green-500' :
                      status === 'active' ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-gray-700'
                    }`}></div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Mobile View - Vertical */}
      <div className="md:hidden space-y-4">
        {steps.map((step, index) => {
          const status = getStepStatus(step.id)
          const isLast = index === steps.length - 1

          return (
            <div key={step.id} className="flex items-start">
              {/* Step Circle and Line */}
              <div className="flex flex-col items-center mr-4">
                <div className={`
                  flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-500
                  ${getStepClasses(status)}
                `}>
                  {getStepIcon(step, status)}
                </div>
                
                {!isLast && (
                  <div className={`w-0.5 h-8 mt-2 transition-all duration-500 ${
                    status === 'completed' ? 'bg-green-500' :
                    status === 'active' ? 'bg-gradient-to-b from-purple-500 to-pink-500' : 'bg-gray-700'
                  }`}></div>
                )}
              </div>

              {/* Step Info */}
              <div className="flex-1 pb-4">
                <div className={`font-medium transition-colors duration-300 ${
                  status === 'completed' ? 'text-green-400' :
                  status === 'active' ? 'text-purple-400' : 'text-gray-500'
                }`}>
                  {step.icon} {step.name}
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {step.description}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Progress Summary */}
      <div className="mt-6 pt-4 border-t border-white/10">
        <div className="flex items-center justify-between text-sm">
          <div className="text-gray-400">
            {isActive ? 'Processing...' : 'Workflow Status'}
          </div>
          <div className={`font-medium ${
            isActive ? 'text-purple-400' : 'text-gray-500'
          }`}>
            {isActive ? `${Math.round((currentStep / steps.length) * 100)}% Complete` : 'Ready'}
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-500 ${
              isActive ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-gray-600'
            }`}
            style={{ 
              width: isActive ? `${(currentStep / steps.length) * 100}%` : '0%' 
            }}
          ></div>
        </div>
      </div>
    </div>
  )
}
