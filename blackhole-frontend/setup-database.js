const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://postgres.pihfretaiaaammcwihes:AKD6bJVt7HPPp0x8@aws-0-ap-south-1.pooler.supabase.com:6543/postgres',
  ssl: {
    rejectUnauthorized: false
  }
});

const setupSQL = `
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (clean slate)
DROP TABLE IF EXISTS "PasswordReset" CASCADE;
DROP TABLE IF EXISTS "EmailVerification" CASCADE;
DROP TABLE IF EXISTS "Session" CASCADE;
DROP TABLE IF EXISTS "ScrapedNews" CASCADE;
DROP TABLE IF EXISTS "User" CASCADE;

-- Create User table
CREATE TABLE "User" (
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
);

-- Create Session table
CREATE TABLE "Session" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(255) UNIQUE NOT NULL,
    "userId" UUID NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create EmailVerification table
CREATE TABLE "EmailVerification" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(255) UNIQUE NOT NULL,
    "userId" UUID NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "usedAt" TIMESTAMP
);

-- Create PasswordReset table
CREATE TABLE "PasswordReset" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(255) UNIQUE NOT NULL,
    "userId" UUID NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "usedAt" TIMESTAMP
);

-- Create ScrapedNews table
CREATE TABLE "ScrapedNews" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "customId" VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    url VARCHAR(1000) UNIQUE NOT NULL,
    source VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    "imageUrl" VARCHAR(1000),
    "publishedAt" VARCHAR(255),
    "readTime" VARCHAR(50),
    "scrapedAt" VARCHAR(255),
    "scrapedData" JSONB,
    summary TEXT,
    insights JSONB,
    "relatedVideos" JSONB,
    "storedAt" VARCHAR(255),
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "userId" UUID REFERENCES "User"(id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX idx_session_token ON "Session"(token);
CREATE INDEX idx_session_userId ON "Session"("userId");
CREATE INDEX idx_email_verification_token ON "EmailVerification"(token);
CREATE INDEX idx_email_verification_userId ON "EmailVerification"("userId");
CREATE INDEX idx_password_reset_token ON "PasswordReset"(token);
CREATE INDEX idx_password_reset_userId ON "PasswordReset"("userId");
CREATE INDEX idx_user_email ON "User"(email);
CREATE INDEX idx_scraped_news_userId ON "ScrapedNews"("userId");

-- Verify tables were created
SELECT 'User table created' as status;
SELECT 'Session table created' as status;
SELECT 'EmailVerification table created' as status;
SELECT 'PasswordReset table created' as status;
SELECT 'ScrapedNews table created' as status;
`;

async function setupDatabase() {
  try {
    console.log('🔌 Connecting to database...');
    const client = await pool.connect();
    console.log('✅ Connected successfully!');
    
    console.log('📦 Setting up database tables...');
    await client.query(setupSQL);
    console.log('✅ Database setup complete!');
    
    client.release();
    process.exit(0);
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

setupDatabase();
