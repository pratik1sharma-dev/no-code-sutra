#!/bin/bash

echo "🚀 Starting Docker build test..."
echo "⏰ Build started at: $(date)"

# Build with timing and verbose output
time docker build -t no-code-sutra-test . --progress=plain

echo "✅ Build completed at: $(date)"

# Check image size
echo "📦 Image size:"
docker images no-code-sutra-test

# Test container startup
echo "🧪 Testing container startup..."
docker run --rm -d --name test-container -p 8001:8000 no-code-sutra-test

# Wait a few seconds and check if it's running
sleep 5
if docker ps | grep -q test-container; then
    echo "✅ Container started successfully"
    docker stop test-container
else
    echo "❌ Container failed to start"
    docker logs test-container 2>/dev/null || echo "No logs available"
fi

echo "🎯 Build test complete!"
