'use client'

import { useEffect, useRef, useState } from 'react'
import Header from '@/components/Header'
import { Video, Sparkles, Loader2, AlertCircle, RotateCcw } from 'lucide-react'

type JobStatus = {
  status?: string
  progress?: number
  progress_percent?: number
  video_id?: string
  videoId?: string
  job_id?: string
  jobId?: string
  error?: string
  message?: string
  detail?: string
  [key: string]: unknown
}

const TTV_API_URL = (process.env.NEXT_PUBLIC_TTV_API_URL || 'http://163.128.209.18:8019').replace(/\/$/, '')
const POLL_INTERVAL_MS = 3000
const MAX_POLL_ATTEMPTS = 200

function getErrorMessage(payload: JobStatus | null, fallback: string) {
  const message = payload?.error || payload?.message || payload?.detail
  return typeof message === 'string' && message.trim() ? message : fallback
}

async function readJson(response: Response) {
  return response.json().catch(() => null) as Promise<JobStatus | null>
}

async function startVideoGeneration(prompt: string) {
  const response = await fetch(`${TTV_API_URL}/api/v1/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  })
  const payload = await readJson(response)

  if (!response.ok) {
    throw new Error(getErrorMessage(payload, `Video generation failed with status ${response.status}.`))
  }

  const jobId = payload?.job_id || payload?.jobId
  if (typeof jobId !== 'string' || !jobId) {
    throw new Error('The video service did not return a job ID.')
  }
  return jobId
}

export default function TTVPage() {
  const [prompt, setPrompt] = useState('')
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [processingStatus, setProcessingStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const pollingCancelledRef = useRef(false)

  useEffect(() => {
    return () => {
      pollingCancelledRef.current = true
    }
  }, [])

  const handleGenerate = async () => {
    const trimmedPrompt = prompt.trim()
    if (!trimmedPrompt) return

    setError(null)
    setVideoUrl(null)
    setProgress(0)
    setProcessingStatus('Submitting prompt...')
    setIsGenerating(true)
    pollingCancelledRef.current = false

    try {
      const jobId = await startVideoGeneration(trimmedPrompt)
      setProcessingStatus('Video generation in progress...')

      for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt += 1) {
        if (pollingCancelledRef.current) return

        const response = await fetch(`${TTV_API_URL}/api/v1/jobs/${encodeURIComponent(jobId)}`)
        const payload = await readJson(response)
        if (!response.ok) {
          throw new Error(getErrorMessage(payload, `Unable to check video job status (${response.status}).`))
        }

        const status = (payload?.status || '').toLowerCase()
        const reportedProgress = payload?.progress_percent ?? payload?.progress
        if (typeof reportedProgress === 'number') {
          setProgress(Math.max(0, Math.min(100, reportedProgress <= 1 ? reportedProgress * 100 : reportedProgress)))
        }
        if (status) setProcessingStatus(`Status: ${status}`)

        const videoId = payload?.video_id || payload?.videoId
        if (videoId && (status === 'completed' || status === 'complete' || status === 'success' || !status)) {
          setProgress(100)
          setProcessingStatus('Video ready')
          setVideoUrl(`${TTV_API_URL}/api/v1/videos/${encodeURIComponent(String(videoId))}?stream=true`)
          return
        }

        if (['failed', 'error', 'cancelled', 'canceled'].includes(status)) {
          throw new Error(getErrorMessage(payload, 'The video generation job failed.'))
        }

        await new Promise((resolve) => window.setTimeout(resolve, POLL_INTERVAL_MS))
      }

      throw new Error('Video generation timed out while waiting for the backend.')
    } catch (generationError) {
      setError(generationError instanceof Error ? generationError.message : 'Video generation failed. Please try again later.')
    } finally {
      if (!pollingCancelledRef.current) setIsGenerating(false)
    }
  }

  const handleNewPrompt = () => {
    pollingCancelledRef.current = true
    setPrompt('')
    setVideoUrl(null)
    setProgress(0)
    setProcessingStatus(null)
    setError(null)
    setIsGenerating(false)
  }

  return (
    <div className="min-h-screen">
      <Header backendStatus="online" />

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <div className="inline-flex w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-3xl items-center justify-center shadow-2xl mb-5">
              <Video className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent mb-3">
              Text-To-Video
            </h1>
            <p className="text-lg text-gray-400">Generate videos from text descriptions.</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <section className="glass-effect rounded-3xl p-8 border border-white/20">
              <div className="flex items-center space-x-3 mb-6">
                <Sparkles className="w-7 h-7 text-purple-400" />
                <h2 className="text-2xl font-semibold text-white">Video Prompt</h2>
              </div>

              <textarea
                value={prompt}
                onChange={(event) => {
                  setPrompt(event.target.value)
                  setError(null)
                }}
                placeholder="Describe the video you want to generate..."
                rows={10}
                disabled={isGenerating}
                className="w-full resize-none bg-black/50 border-2 border-white/20 rounded-2xl px-5 py-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
              <div className="flex items-center justify-between mt-3 mb-6 text-sm text-gray-500">
                <span>{prompt.length} characters</span>
                <span>Describe the scene, style, and mood.</span>
              </div>

              <button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating}
                className="w-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-600 hover:from-purple-600 hover:via-pink-600 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white px-6 py-4 rounded-2xl font-bold text-lg transition-all flex items-center justify-center space-x-3 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    <span>Generating Video...</span>
                  </>
                ) : (
                  <>
                    <Video className="w-6 h-6" />
                    <span>Generate Video</span>
                  </>
                )}
              </button>

              {isGenerating && (
                <div className="mt-6 space-y-2">
                  <div className="flex items-center justify-between text-sm text-gray-400">
                    <span>{processingStatus || 'Processing...'}</span>
                    <span>{Math.round(progress)}%</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-black/50">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                      style={{ width: `${Math.max(progress, 5)}%` }}
                    />
                  </div>
                </div>
              )}

              {error && (
                <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-xl flex items-start space-x-3">
                  <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-yellow-200">{error}</p>
                </div>
              )}
            </section>

            <section className="glass-effect rounded-3xl p-8 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold text-white">Generated Video</h2>
                {(videoUrl || error) && (
                  <button
                    onClick={handleNewPrompt}
                    className="flex items-center space-x-2 text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>New prompt</span>
                  </button>
                )}
              </div>

              {videoUrl ? (
                <video
                  src={videoUrl}
                  controls
                  autoPlay
                  className="w-full aspect-video rounded-2xl bg-black object-contain"
                />
              ) : (
                <div className="aspect-video rounded-2xl border border-dashed border-white/20 bg-black/30 flex items-center justify-center text-center p-6">
                  <p className="text-gray-500">
                    {isGenerating ? 'Your video is being generated...' : 'Your generated video will appear here.'}
                  </p>
                </div>
              )}
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}
