'use client'

import { useEffect, useRef, useState } from 'react'
import Header from '@/components/Header'
import {
  AlertCircle,
  CheckCircle,
  Clipboard,
  Download,
  FileAudio,
  Loader2,
  Mic,
  Square,
  Upload,
} from 'lucide-react'

type TranscriptSegment = {
  start?: number
  end?: number
  start_time?: number
  end_time?: number
  text?: string
  [key: string]: unknown
}

type TranscriptionResult = {
  text?: string
  transcript?: string
  language?: string
  duration?: number
  segments?: TranscriptSegment[]
  [key: string]: unknown
}

const AUDIO_API_URL = process.env.VITE_STT_API_URL || 'http://163.128.209.18:8020'

function formatTime(value: unknown) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '--:--'
  const minutes = Math.floor(value / 60)
  const seconds = Math.floor(value % 60).toString().padStart(2, '0')
  return `${minutes}:${seconds}`
}

function formatDuration(value: unknown) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return 'Unknown'
  return `${value.toFixed(2)}s`
}

export default function STTPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [result, setResult] = useState<TranscriptionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isCopied, setIsCopied] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const recordingStreamRef = useRef<MediaStream | null>(null)
  const recordingChunksRef = useRef<Blob[]>([])

  useEffect(() => {
    return () => {
      recordingStreamRef.current?.getTracks().forEach((track) => track.stop())
    }
  }, [])

  const resetResult = () => {
    setResult(null)
    setError(null)
    setIsCopied(false)
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null
    resetResult()

    if (!file) {
      setSelectedFile(null)
      return
    }

    const extension = file.name.split('.').pop()?.toLowerCase()
    if (!extension || !['mp3', 'wav'].includes(extension)) {
      setSelectedFile(null)
      setError('Unsupported audio format. Choose an MP3 or WAV file.')
      event.target.value = ''
      return
    }

    if (file.size === 0) {
      setSelectedFile(null)
      setError('The selected audio file is empty.')
      event.target.value = ''
      return
    }

    setSelectedFile(file)
  }

  const startRecording = async () => {
    resetResult()
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      recordingStreamRef.current = stream
      mediaRecorderRef.current = recorder
      recordingChunksRef.current = []

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) recordingChunksRef.current.push(event.data)
      }
      recorder.onstop = () => {
        const recording = new Blob(recordingChunksRef.current, {
          type: recorder.mimeType || 'audio/webm',
        })
        setSelectedFile(new File([recording], 'browser-recording.webm', { type: recording.type }))
        stream.getTracks().forEach((track) => track.stop())
        recordingStreamRef.current = null
        mediaRecorderRef.current = null
      }

      recorder.start()
      setIsRecording(true)
    } catch (recordingError) {
      setError(recordingError instanceof DOMException && recordingError.name === 'NotAllowedError'
        ? 'Microphone access was denied. Please allow microphone access and try again.'
        : 'Unable to access the microphone. Please check your browser permissions.')
    }
  }

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current
    if (!recorder || recorder.state === 'inactive') return
    recorder.stop()
    setIsRecording(false)
  }

  const handleTranscribe = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!selectedFile) {
      setError('Choose an MP3 or WAV file, or record audio before transcribing.')
      return
    }

    setError(null)
    setResult(null)
    setIsCopied(false)
    setIsTranscribing(true)

    try {
      const formData = new FormData()
      formData.append('audio', selectedFile)
      const response = await fetch(`${AUDIO_API_URL}/api/v1/transcribe`, {
        method: 'POST',
        body: formData,
      })
      const payload: unknown = await response.json().catch(() => null)

      if (!response.ok) {
        const detail = payload && typeof payload === 'object' && 'detail' in payload
          ? (payload as { detail?: unknown }).detail
          : payload && typeof payload === 'object' && 'message' in payload
            ? (payload as { message?: unknown }).message
            : null
        throw new Error(typeof detail === 'string' ? detail : `Transcription failed with status ${response.status}.`)
      }

      if (!payload || typeof payload !== 'object') {
        throw new Error('The transcription service returned an invalid response.')
      }
      setResult(payload as TranscriptionResult)
    } catch (transcriptionError) {
      setError(transcriptionError instanceof Error
        ? transcriptionError.message
        : 'Unable to transcribe the selected audio.')
    } finally {
      setIsTranscribing(false)
    }
  }

  const transcriptText = result?.text || result?.transcript || ''
  const copyTranscript = async () => {
    if (!transcriptText) return
    try {
      await navigator.clipboard.writeText(transcriptText)
      setIsCopied(true)
      window.setTimeout(() => setIsCopied(false), 2000)
    } catch {
      setError('Unable to copy the transcript to the clipboard.')
    }
  }

  const downloadTranscript = () => {
    if (!transcriptText) return
    const link = document.createElement('a')
    link.href = URL.createObjectURL(new Blob([transcriptText], { type: 'text/plain' }))
    link.download = 'transcript.txt'
    link.click()
    URL.revokeObjectURL(link.href)
  }

  return (
    <div className="min-h-screen">
      <Header backendStatus="online" />
      <main className="container mx-auto px-6 py-8">
        <div className="mx-auto max-w-5xl">
          <div className="mb-8 text-center">
            <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 shadow-2xl">
              <Mic className="h-8 w-8 text-white" />
            </div>
            <h1 className="mb-2 text-4xl font-bold text-white">Speech-to-Text</h1>
            <p className="text-gray-400">Upload or record audio to generate a transcript.</p>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <section className="glass-effect rounded-2xl border border-white/10 p-6">
              <h2 className="mb-2 text-xl font-semibold text-white">Audio input</h2>
              <p className="mb-6 text-sm text-gray-400">Supported uploads: MP3 and WAV.</p>

              <form onSubmit={handleTranscribe} className="space-y-5">
                <label
                  htmlFor="stt-audio"
                  className="flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-purple-400/50 bg-black/20 px-6 text-center transition-colors hover:border-purple-300 hover:bg-purple-500/10"
                >
                  <Upload className="mb-3 h-9 w-9 text-purple-400" />
                  <span className="text-sm font-medium text-white">
                    {selectedFile ? selectedFile.name : 'Choose an audio file'}
                  </span>
                  <span className="mt-2 text-xs text-gray-400">
                    {selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB selected` : 'Click to browse your device'}
                  </span>
                  <input id="stt-audio" type="file" accept=".mp3,.wav,audio/mpeg,audio/wav" onChange={handleFileChange} className="sr-only" />
                </label>

                <div className="flex items-center gap-3">
                  <div className="h-px flex-1 bg-white/10" />
                  <span className="text-xs uppercase tracking-wider text-gray-500">or</span>
                  <div className="h-px flex-1 bg-white/10" />
                </div>

                <button
                  type="button"
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={isTranscribing}
                  className={`flex w-full items-center justify-center gap-2 rounded-lg border px-4 py-3 font-medium transition-all disabled:cursor-not-allowed disabled:opacity-50 ${isRecording ? 'border-red-400/50 bg-red-500/20 text-red-200 hover:bg-red-500/30' : 'border-purple-400/40 bg-purple-500/10 text-purple-200 hover:bg-purple-500/20'}`}
                >
                  {isRecording ? <Square className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                  {isRecording ? 'Stop recording' : 'Record from microphone'}
                </button>

                {error && (
                  <div className="flex items-start gap-3 rounded-lg border border-red-500/50 bg-red-500/20 p-4 text-sm text-red-200">
                    <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-400" />
                    <span>{error}</span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={!selectedFile || isRecording || isTranscribing}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-3 font-medium text-white transition-all hover:from-purple-600 hover:to-pink-600 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isTranscribing ? <><Loader2 className="h-5 w-5 animate-spin" />Transcribing audio...</> : <><FileAudio className="h-5 w-5" />Transcribe audio</>}
                </button>
              </form>
            </section>

            <section className="glass-effect rounded-2xl border border-white/10 p-6">
              <div className="mb-5 flex items-center gap-3">
                <CheckCircle className="h-6 w-6 text-green-400" />
                <h2 className="text-xl font-semibold text-white">Transcription result</h2>
              </div>

              {result ? (
                <div className="space-y-5">
                  <div className="flex items-center gap-2 rounded-lg border border-green-500/30 bg-green-500/10 p-3 text-sm text-green-200">
                    <CheckCircle className="h-4 w-4 text-green-400" />
                    Transcription completed successfully.
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-lg bg-black/30 p-3"><p className="text-xs text-gray-500">Language</p><p className="mt-1 text-white">{result.language || 'Unknown'}</p></div>
                    <div className="rounded-lg bg-black/30 p-3"><p className="text-xs text-gray-500">Duration</p><p className="mt-1 text-white">{formatDuration(result.duration)}</p></div>
                  </div>
                  <div>
                    <div className="mb-2 flex items-center justify-between">
                      <h3 className="font-medium text-white">Transcript</h3>
                      <div className="flex gap-2">
                        <button type="button" onClick={copyTranscript} disabled={!transcriptText} className="flex items-center gap-1 rounded-md border border-white/10 px-2 py-1 text-xs text-gray-300 hover:bg-white/10 disabled:opacity-50"><Clipboard className="h-3.5 w-3.5" />{isCopied ? 'Copied' : 'Copy'}</button>
                        <button type="button" onClick={downloadTranscript} disabled={!transcriptText} className="flex items-center gap-1 rounded-md border border-white/10 px-2 py-1 text-xs text-gray-300 hover:bg-white/10 disabled:opacity-50"><Download className="h-3.5 w-3.5" />Download</button>
                      </div>
                    </div>
                    <div className="max-h-48 overflow-y-auto rounded-lg bg-black/30 p-4 text-sm leading-6 text-gray-200">{transcriptText || 'No transcript text was returned.'}</div>
                  </div>
                  {Array.isArray(result.segments) && result.segments.length > 0 && (
                    <div>
                      <h3 className="mb-2 font-medium text-white">Segments</h3>
                      <div className="max-h-48 space-y-2 overflow-y-auto">
                        {result.segments.map((segment, index) => (
                          <div key={`${segment.start}-${segment.end}-${index}`} className="flex gap-3 rounded-lg bg-black/30 p-3 text-sm">
                            <span className="whitespace-nowrap text-purple-300">{formatTime(segment.start ?? segment.start_time)} - {formatTime(segment.end ?? segment.end_time)}</span>
                            <span className="text-gray-300">{segment.text || 'No segment text'}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex min-h-64 items-center justify-center rounded-xl border border-dashed border-white/20 bg-black/20 p-6 text-center text-gray-500">
                  Your transcript and timestamped segments will appear here.
                </div>
              )}
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}
