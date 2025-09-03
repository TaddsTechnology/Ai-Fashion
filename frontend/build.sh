#!/bin/bash
# Frontend build script for Render deployment

echo "🎨 Building AI Fashion Frontend..."

# Ensure we're in the frontend directory
cd /opt/render/project/src/frontend || cd .

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the application
echo "🔨 Building application..."
npm run build

# Verify build output
if [ -d "dist" ]; then
    echo "✅ Build completed successfully!"
    echo "📁 Build output directory: dist"
    ls -la dist/
else
    echo "❌ Build failed - no dist directory found"
    exit 1
fi
