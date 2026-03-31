#!/bin/bash

echo "🔧 Setting up Blackhole Infiverse authentication system..."
echo ""

# Generate Prisma client
echo "📦 Generating Prisma client..."
npx prisma@6.19.2 generate --schema=prisma/schema.prisma

# Push database schema
echo "🗄️  Pushing database schema..."
npx prisma@6.19.2 db push --schema=prisma/schema.prisma

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting development server..."
npm run dev
