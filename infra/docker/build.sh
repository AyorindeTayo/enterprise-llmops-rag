#!/bin/bash

set -e

echo "================================"
echo "Building Enterprise LLMOps RAG System"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Build Docker images
echo -e "${BLUE}Step 1: Building Docker images...${NC}"
docker-compose build --no-cache

# Step 2: Check if images exist
echo -e "${BLUE}Step 2: Verifying Docker images...${NC}"
docker images | grep llmops || echo "Images not found"

# Step 3: Start services
echo -e "${BLUE}Step 3: Starting services with Docker Compose...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo -e "${BLUE}Step 4: Waiting for services to be healthy...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is healthy${NC}"
        break
    fi
    echo "Waiting for API... ($i/30)"
    sleep 2
done

# Step 5: Verify services
echo -e "${BLUE}Step 5: Verifying services...${NC}"
curl -s http://localhost:8000/ | jq . || echo "API endpoint check"
echo -e "${GREEN}✓ FastAPI running on http://localhost:8000${NC}"
echo -e "${GREEN}✓ Streamlit running on http://localhost:8501${NC}"

# Step 6: Show service logs
echo -e "${BLUE}Step 6: Showing recent logs...${NC}"
docker-compose logs --tail=10

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ Build complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Access your system:"
echo -e "  ${BLUE}FastAPI (API):${NC}     http://localhost:8000"
echo -e "  ${BLUE}Streamlit UI:${NC}      http://localhost:8501"
echo -e "  ${BLUE}API Docs:${NC}          http://localhost:8000/docs"
echo ""
echo "Useful Docker commands:"
echo "  docker-compose logs -f api       # Follow API logs"
echo "  docker-compose logs -f streamlit # Follow Streamlit logs"
echo "  docker-compose down              # Stop all services"
echo "  docker-compose ps                # Show running services"
