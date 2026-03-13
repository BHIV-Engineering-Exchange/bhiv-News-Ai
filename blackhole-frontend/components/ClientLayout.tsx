'use client'

import { usePathname } from 'next/navigation'
import { AuthProvider, useAuth } from '@/lib/auth'
import ProtectedRoute from '@/components/ProtectedRoute'

function LayoutContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { isLoading } = useAuth()
  
  // Public routes that don't require authentication
  const publicRoutes = ['/login', '/signup', '/forgot-password', '/reset-password', '/verify-email', '/setup']
  const isPublicRoute = publicRoutes.some(route => pathname?.startsWith(route))
  
  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blackhole-950 via-blackhole-900 to-infiverse-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="min-h-screen">
      {isPublicRoute ? (
        children
      ) : (
        <ProtectedRoute>{children}</ProtectedRoute>
      )}
    </div>
  )
}

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <LayoutContent>
        {children}
      </LayoutContent>
    </AuthProvider>
  )
}
