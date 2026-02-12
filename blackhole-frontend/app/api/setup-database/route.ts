import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

// This endpoint initializes the database tables
// Call it once after deployment: POST /api/setup-database
export async function POST(request: NextRequest) {
  try {
    // Create tables using Prisma's raw queries
    const setupQueries = [
      // Enable UUID extension
      `CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`,
      
      // Create User table
      `CREATE TABLE IF NOT EXISTS "User" (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(255),
        "isEmailVerified" BOOLEAN DEFAULT false,
        "emailVerifiedAt" TIMESTAMP,
        "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        "lastLoginAt" TIMESTAMP,
        "isActive" BOOLEAN DEFAULT true
      )`,
      
      // Create Session table
      `CREATE TABLE IF NOT EXISTS "Session" (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        token VARCHAR(255) UNIQUE NOT NULL,
        "userId" UUID NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
        "expiresAt" TIMESTAMP NOT NULL,
        "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )`,
      
      // Create EmailVerification table
      `CREATE TABLE IF NOT EXISTS "EmailVerification" (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        token VARCHAR(255) UNIQUE NOT NULL,
        "userId" UUID NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
        "expiresAt" TIMESTAMP NOT NULL,
        "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        "usedAt" TIMESTAMP
      )`,
      
      // Create PasswordReset table
      `CREATE TABLE IF NOT EXISTS "PasswordReset" (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        token VARCHAR(255) UNIQUE NOT NULL,
        "userId" UUID NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
        "expiresAt" TIMESTAMP NOT NULL,
        "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        "usedAt" TIMESTAMP
      )`,
      
      // Create indexes
      `CREATE INDEX IF NOT EXISTS idx_session_token ON "Session"(token)`,
      `CREATE INDEX IF NOT EXISTS idx_session_userId ON "Session"("userId")`,
      `CREATE INDEX IF NOT EXISTS idx_email_verification_token ON "EmailVerification"(token)`,
      `CREATE INDEX IF NOT EXISTS idx_password_reset_token ON "PasswordReset"(token)`,
      `CREATE INDEX IF NOT EXISTS idx_user_email ON "User"(email)`
    ]

    // Execute all queries
    for (const query of setupQueries) {
      try {
        await prisma.$executeRawUnsafe(query)
      } catch (error: any) {
        // Ignore "already exists" errors
        if (!error.message?.includes('already exists')) {
          console.error('Query failed:', query, error.message)
        }
      }
    }

    return NextResponse.json({
      success: true,
      message: 'Database setup complete! You can now sign up and login.'
    })
  } catch (error) {
    console.error('Database setup error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to setup database',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

// GET endpoint to check if database is setup
export async function GET(request: NextRequest) {
  try {
    // Try to query the User table
    await prisma.$queryRaw`SELECT 1 FROM "User" LIMIT 1`
    
    return NextResponse.json({
      success: true,
      setup: true,
      message: 'Database is already setup'
    })
  } catch (error) {
    return NextResponse.json({
      success: true,
      setup: false,
      message: 'Database needs setup'
    })
  }
}
