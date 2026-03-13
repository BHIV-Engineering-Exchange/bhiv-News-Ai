#!/bin/bash

# Render Build Script for Blackhole Frontend
# This script ensures a clean and successful build

set -e  # Exit on any error

echo "🚀 Starting Render build process..."

# 1. Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf .next
rm -rf node_modules/.cache

# 2. Install dependencies
echo "📦 Installing dependencies..."
npm ci --production=false

# 3. Run build
echo "🔨 Building Next.js application..."
npm run build

# 4. Verify build
echo "✅ Verifying build..."
if [ -d ".next" ]; then
  echo "✅ Build successful! .next directory created."
else
  echo "❌ Build failed! .next directory not found."
  exit 1
fi

echo "🎉 Build completed successfully!"
