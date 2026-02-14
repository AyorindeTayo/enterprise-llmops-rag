#!/bin/bash

# RAG API test suite
# Tests API endpoints and RAG functionality

set -e

echo "================================"
echo "Testing RAG API"
echo "================================"

API_URL=${1:-"http://localhost:8000"}
echo "Testing API at: $API_URL"

# Wait for API to be ready
echo "Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo "✓ API is ready"
        break
    fi
    echo "Attempt $i/30..."
    sleep 1
done

# Test 1: Health check
echo ""
echo "Test 1: Health Check"
curl -s "$API_URL/health" | jq .

# Test 2: Root endpoint
echo ""
echo "Test 2: Root Endpoint"
curl -s "$API_URL/" | jq .

# Test 3: Stats endpoint
echo ""
echo "Test 3: Stats Endpoint"
curl -s "$API_URL/stats" | jq .

# Test 4: Ask question
echo ""
echo "Test 4: Ask Question"
curl -s -X POST "$API_URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is today date?"}' | jq .

# Test 5: Index documents
echo ""
echo "Test 5: Index Documents"
curl -s -X POST "$API_URL/index" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "Machine learning is a subset of AI",
      "Kubernetes orchestrates containers",
      "FAISS enables fast similarity search"
    ]
  }' | jq .

# Test 6: Search
echo ""
echo "Test 6: Search Knowledge Base"
curl -s -X POST "$API_URL/search" \
  -H "Content-Type: application/json" \
  -d '{"query":"machine learning","k":2}' | jq .

# Test 7: Get updated stats
echo ""
echo "Test 7: Updated Stats"
curl -s "$API_URL/stats" | jq .

echo ""
echo "================================"
echo "✓ All tests completed!"
echo "================================"
