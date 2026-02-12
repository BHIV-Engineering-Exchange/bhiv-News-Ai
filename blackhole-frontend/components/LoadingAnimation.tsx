'use client'

import { motion } from 'framer-motion'

interface LoadingAnimationProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
}

export default function LoadingAnimation({ size = 'md', text }: LoadingAnimationProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-16 h-16',
    lg: 'w-24 h-24'
  }

  const dotSizes = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  }

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      {/* Blackhole Animation */}
      <div className={`relative ${sizeClasses[size]}`}>
        {/* Event Horizon */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 rounded-full border-2 border-purple-500/30"
        />
        
        {/* Accretion Disk */}
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="absolute inset-1 rounded-full border border-pink-500/50"
        />
        
        {/* Inner Core */}
        <motion.div
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.8, 1, 0.8]
          }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="absolute inset-2 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full"
        />
        
        {/* Singularity */}
        <div className="absolute inset-1/2 w-1 h-1 bg-black rounded-full transform -translate-x-1/2 -translate-y-1/2" />
        
        {/* Orbiting Particles */}
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            animate={{ rotate: 360 }}
            transition={{ 
              duration: 1 + i * 0.5, 
              repeat: Infinity, 
              ease: "linear",
              delay: i * 0.2
            }}
            className="absolute inset-0"
          >
            <div 
              className={`absolute ${dotSizes[size]} bg-white rounded-full`}
              style={{
                top: '10%',
                left: '50%',
                transform: 'translateX(-50%)'
              }}
            />
          </motion.div>
        ))}
      </div>

      {/* Loading Text */}
      {text && (
        <motion.p
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="text-gray-400 text-sm font-medium"
        >
          {text}
        </motion.p>
      )}
    </div>
  )
}
