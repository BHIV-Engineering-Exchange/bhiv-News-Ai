'use client'

import { useState } from 'react'
import { clearJWT } from '@/lib/security'

interface AuthErrorProps {
    error: { status: number; message: string } | null
    onRetry?: () => void
    onDismiss?: () => void
}

export default function AuthError({ error, onRetry, onDismiss }: AuthErrorProps) {
    const [isVisible, setIsVisible] = useState(true)

    if (!error || !isVisible) return null

    const handleClearAuth = () => {
        clearJWT()
        if (onRetry) {
            onRetry()
        }
    }

    const handleDismiss = () => {
        setIsVisible(false)
        if (onDismiss) {
            onDismiss()
        }
    }

    const getErrorTitle = () => {
        if (error.status === 401) {
            return 'Authentication Required'
        } else if (error.status === 403) {
            return 'Access Denied'
        }
        return 'Authorization Error'
    }

    const getErrorMessage = () => {
        if (error.status === 401) {
            return 'Your session has expired or you are not logged in. Please authenticate to continue.'
        } else if (error.status === 403) {
            return 'You do not have permission to access this resource. Please check your credentials.'
        }
        return error.message || 'An authentication error occurred. Please try again.'
    }

    return (
        <div className="fixed bottom-4 right-4 max-w-md z-50 animate-slideIn">
            <div className="glass-card border border-red-500/30 p-4 rounded-lg shadow-lg backdrop-blur-md bg-red-900/20">
                <div className="flex items-start gap-3">
                    {/* Error Icon */}
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center">
                        <svg
                            className="w-6 h-6 text-red-400"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                            />
                        </svg>
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-semibold text-red-200 mb-1">
                            {getErrorTitle()}
                        </h3>
                        <p className="text-sm text-red-300/90">
                            {getErrorMessage()}
                        </p>

                        {/* Actions */}
                        <div className="mt-3 flex items-center gap-2">
                            {error.status === 401 && (
                                <button
                                    onClick={handleClearAuth}
                                    className="px-3 py-1.5 text-xs font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors"
                                >
                                    Clear & Retry
                                </button>
                            )}
                            {onRetry && (
                                <button
                                    onClick={onRetry}
                                    className="px-3 py-1.5 text-xs font-medium text-red-200 hover:text-white hover:bg-red-500/20 rounded-md transition-colors"
                                >
                                    Retry
                                </button>
                            )}
                            <button
                                onClick={handleDismiss}
                                className="px-3 py-1.5 text-xs font-medium text-red-300 hover:text-white hover:bg-red-500/10 rounded-md transition-colors"
                            >
                                Dismiss
                            </button>
                        </div>
                    </div>

                    {/* Close Button */}
                    <button
                        onClick={handleDismiss}
                        className="flex-shrink-0 w-6 h-6 rounded-full hover:bg-red-500/20 flex items-center justify-center transition-colors"
                    >
                        <svg
                            className="w-4 h-4 text-red-300"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                    </button>
                </div>

                {/* Error Code */}
                <div className="mt-2 pt-2 border-t border-red-500/20">
                    <p className="text-xs text-red-400/70">
                        Error Code: {error.status}
                    </p>
                </div>
            </div>

            <style jsx>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slideIn {
          animation: slideIn 0.3s ease-out;
        }
      `}</style>
        </div>
    )
}
