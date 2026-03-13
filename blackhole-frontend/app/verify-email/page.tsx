'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { Loader2, CheckCircle, XCircle, Mail } from 'lucide-react'

export default function VerifyEmailPage() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const token = searchParams.get('token')
    
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
    const [message, setMessage] = useState('Verifying your email...')

    useEffect(() => {
        if (!token) {
            setStatus('error')
            setMessage('Invalid verification link')
            return
        }

        const verifyEmail = async () => {
            try {
                const response = await fetch(`/api/auth/verify-email?token=${token}`)
                const data = await response.json()

                if (data.success) {
                    setStatus('success')
                    setMessage('Your email has been verified successfully!')
                    
                    // Redirect to login after 3 seconds
                    setTimeout(() => {
                        router.push('/login')
                    }, 3000)
                } else {
                    setStatus('error')
                    setMessage(data.error || 'Failed to verify email')
                }
            } catch {
                setStatus('error')
                setMessage('An error occurred while verifying your email')
            }
        }

        verifyEmail()
    }, [token, router])

    return (
        <div className="min-h-screen flex flex-col">
            <main className="flex-1 flex items-center justify-center p-6 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-black to-pink-900/10"></div>
                
                <div className="w-full max-w-md relative z-10">
                    <div className="glass-effect p-8 rounded-2xl border border-white/10 shadow-2xl text-center">
                        {status === 'loading' && (
                            <>
                                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                                    <Loader2 className="w-8 h-8 text-white animate-spin" />
                                </div>
                                <h1 className="text-3xl font-bold text-white mb-2">Verifying...</h1>
                            </>
                        )}
                        
                        {status === 'success' && (
                            <>
                                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                                    <CheckCircle className="w-8 h-8 text-white" />
                                </div>
                                <h1 className="text-3xl font-bold text-white mb-2">Email Verified!</h1>
                            </>
                        )}
                        
                        {status === 'error' && (
                            <>
                                <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                                    <XCircle className="w-8 h-8 text-white" />
                                </div>
                                <h1 className="text-3xl font-bold text-white mb-2">Verification Failed</h1>
                            </>
                        )}
                        
                        <p className="text-gray-400 mb-6">{message}</p>
                        
                        {status === 'success' && (
                            <p className="text-sm text-gray-500">
                                Redirecting to login page...
                            </p>
                        )}
                        
                        {status === 'error' && (
                            <div className="space-y-3">
                                <Link
                                    href="/signup"
                                    className="block w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold py-3 rounded-xl transition-all"
                                >
                                    Back to Signup
                                </Link>
                                <p className="text-sm text-gray-500">
                                    If you need a new verification email, please sign up again.
                                </p>
                            </div>
                        )}
                        
                        {status === 'loading' && (
                            <div className="flex items-center justify-center space-x-2 text-gray-400">
                                <Mail className="w-5 h-5" />
                                <span>Please wait while we verify your email</span>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    )
}
