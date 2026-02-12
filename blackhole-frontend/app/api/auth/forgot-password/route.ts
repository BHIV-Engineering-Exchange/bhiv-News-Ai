import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'
import { v4 as uuidv4 } from 'uuid'
import { sendEmail, generatePasswordResetEmail } from '@/lib/email'

export async function POST(request: NextRequest) {
  try {
    const { email } = await request.json()

    if (!email) {
      return NextResponse.json(
        { success: false, error: 'Email is required' },
        { status: 400 }
      )
    }

    // Find user
    const user = await prisma.user.findUnique({
      where: { email }
    })

    // Don't reveal if user exists for security
    if (!user) {
      return NextResponse.json({
        success: true,
        message: 'If an account exists with this email, you will receive a password reset link'
      })
    }

    // Invalidate any existing unused tokens
    await prisma.passwordReset.updateMany({
      where: {
        userId: user.id,
        usedAt: null
      },
      data: {
        usedAt: new Date() // Mark as used to invalidate
      }
    })

    // Generate reset token
    const resetToken = uuidv4()
    await prisma.passwordReset.create({
      data: {
        token: resetToken,
        userId: user.id,
        expiresAt: new Date(Date.now() + 60 * 60 * 1000) // 1 hour
      }
    })

    // Send reset email
    const resetLink = `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/reset-password?token=${resetToken}`
    await sendEmail({
      to: email,
      subject: 'Reset your password - Blackhole Infiverse',
      html: generatePasswordResetEmail(user.name || email.split('@')[0], resetLink)
    })

    return NextResponse.json({
      success: true,
      message: 'If an account exists with this email, you will receive a password reset link'
    })
  } catch (error) {
    console.error('Password reset request error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
