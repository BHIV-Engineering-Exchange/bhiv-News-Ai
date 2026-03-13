import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'
import bcrypt from 'bcryptjs'

export async function POST(request: NextRequest) {
  try {
    const { token, password } = await request.json()

    if (!token || !password) {
      return NextResponse.json(
        { success: false, error: 'Token and password are required' },
        { status: 400 }
      )
    }

    if (password.length < 8) {
      return NextResponse.json(
        { success: false, error: 'Password must be at least 8 characters' },
        { status: 400 }
      )
    }

    // Find reset record
    const reset = await prisma.passwordReset.findUnique({
      where: { token },
      include: { user: true }
    })

    if (!reset) {
      return NextResponse.json(
        { success: false, error: 'Invalid or expired token' },
        { status: 400 }
      )
    }

    // Check if already used
    if (reset.usedAt) {
      return NextResponse.json(
        { success: false, error: 'Token already used' },
        { status: 400 }
      )
    }

    // Check if expired
    if (reset.expiresAt < new Date()) {
      return NextResponse.json(
        { success: false, error: 'Token has expired' },
        { status: 400 }
      )
    }

    // Hash new password
    const hashedPassword = await bcrypt.hash(password, 10)

    // Update user password
    await prisma.user.update({
      where: { id: reset.userId },
      data: { password: hashedPassword }
    })

    // Mark reset token as used
    await prisma.passwordReset.update({
      where: { id: reset.id },
      data: { usedAt: new Date() }
    })

    // Delete all user sessions for security
    await prisma.session.deleteMany({
      where: { userId: reset.userId }
    })

    return NextResponse.json({
      success: true,
      message: 'Password reset successfully'
    })
  } catch (error) {
    console.error('Password reset error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
