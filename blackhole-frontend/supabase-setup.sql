-- Create User table
CREATE TABLE IF NOT EXISTS "User" (
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
CREATE TABLE IF NOT EXISTS "Session" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(255) UNIQUE NOT NULL,
    "userId" UUID NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create EmailVerification table
CREATE TABLE IF NOT EXISTS "EmailVerification" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(255) UNIQUE NOT NULL,
    "userId" UUID NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "usedAt" TIMESTAMP
);

-- Create PasswordReset table
CREATE TABLE IF NOT EXISTS "PasswordReset" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(255) UNIQUE NOT NULL,
    "userId" UUID NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "usedAt" TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_session_token ON "Session"(token);
CREATE INDEX IF NOT EXISTS idx_session_userId ON "Session"("userId");
CREATE INDEX IF NOT EXISTS idx_email_verification_token ON "EmailVerification"(token);
CREATE INDEX IF NOT EXISTS idx_email_verification_userId ON "EmailVerification"("userId");
CREATE INDEX IF NOT EXISTS idx_password_reset_token ON "PasswordReset"(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_userId ON "PasswordReset"("userId");
CREATE INDEX IF NOT EXISTS idx_user_email ON "User"(email);

-- Update ScrapedNews table to add user relation
ALTER TABLE "ScrapedNews" ADD COLUMN IF NOT EXISTS "userId" UUID REFERENCES "User"(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_scraped_news_userId ON "ScrapedNews"("userId");
