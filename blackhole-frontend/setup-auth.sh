#!/bin/bash

echo "🔧 Setting up Blackhole Infiverse authentication system..."
echo ""

# Generate Prisma client
echo "📦 Generating Prisma client..."
npx prisma generate

# Push database schema
echo "🗄️  Pushing database schema..."
npx prisma db push

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting development server..."
npm run dev
