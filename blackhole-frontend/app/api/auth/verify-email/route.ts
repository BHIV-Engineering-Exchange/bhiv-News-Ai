import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const token = searchParams.get('token')

    if (!token) {
      return NextResponse.json(
        { success: false, error: 'Token is required' },
        { status: 400 }
      )
    }

    // Find verification record
    const verification = await prisma.emailVerification.findUnique({
      where: { token },
      include: { user: true }
    })

    if (!verification) {
      return NextResponse.json(
        { success: false, error: 'Invalid or expired token' },
        { status: 400 }
      )
    }

    // Check if already used
    if (verification.usedAt) {
      return NextResponse.json(
        { success: false, error: 'Token already used' },
        { status: 400 }
      )
    }

    // Check if expired
    if (verification.expiresAt < new Date()) {
      return NextResponse.json(
        { success: false, error: 'Token has expired' },
        { status: 400 }
      )
    }

    // Mark as used
    await prisma.emailVerification.update({
      where: { id: verification.id },
      data: { usedAt: new Date() }
    })

    // Verify user email
    await prisma.user.update({
      where: { id: verification.userId },
      data: {
        isEmailVerified: true,
        emailVerifiedAt: new Date()
      }
    })

    return NextResponse.json({
      success: true,
      message: 'Email verified successfully'
    })
  } catch (error) {
    console.error('Email verification error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
