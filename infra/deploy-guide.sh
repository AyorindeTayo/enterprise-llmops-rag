#!/bin/bash

# Enterprise LLMOps RAG System - Deployment Guide
# This script helps you set up your deployment infrastructure

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Enterprise LLMOps RAG - Setup Guide${NC}"
echo -e "${BLUE}========================================${NC}"

# Check for required tools
echo ""
echo -e "${BLUE}Checking prerequisites...${NC}"

check_tool() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓ $1 is installed${NC}"
        return 0
    else
        echo -e "${RED}✗ $1 is not installed${NC}"
        return 1
    fi
}

MISSING_TOOLS=0

check_tool docker || MISSING_TOOLS=1
check_tool docker-compose || MISSING_TOOLS=1
check_tool git || MISSING_TOOLS=1

if [ $MISSING_TOOLS -eq 1 ]; then
    echo -e "${RED}Some required tools are missing.${NC}"
    echo "Please install Docker, Docker Compose, and Git."
    exit 1
fi

echo ""
echo -e "${BLUE}Select deployment method:${NC}"
echo ""
echo "1. Docker Compose (Recommended for development)"
echo "2. Kubernetes with Minikube (Recommended for staging)"
echo "3. GitHub Actions CI/CD (For production)"
echo "4. Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "${YELLOW}Setting up Docker Compose...${NC}"
        echo ""
        echo "Prerequisites:"
        echo "  - Docker Desktop or Docker Engine + Docker Compose"
        echo "  - 4GB+ RAM available"
        echo "  - Ports 8000 and 8501 available"
        echo ""
        echo "Steps:"
        echo "1. Set your OPENAI_API_KEY in .env:"
        echo "   export OPENAI_API_KEY='your-key-here'"
        echo ""
        echo "2. Build and start services:"
        echo "   bash infra/docker/build.sh"
        echo ""
        echo "3. Access services:"
        echo "   API: http://localhost:8000"
        echo "   UI: http://localhost:8501"
        echo ""
        echo "4. View logs:"
        echo "   docker-compose logs -f"
        echo ""
        echo "For more details, see: infra/DOCKER_GUIDE.md"
        ;;
    
    2)
        echo -e "${YELLOW}Setting up Kubernetes (Minikube)...${NC}"
        echo ""
        echo "Prerequisites:"
        echo "  - Docker or VirtualBox"
        echo "  - 4GB+ RAM available"
        echo "  - kubectl installed"
        echo "  - Minikube installed"
        echo ""
        echo "Installation:"
        echo "  # macOS"
        echo "  brew install minikube kubectl"
        echo ""
        echo "  # Linux"
        echo "  curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64"
        echo "  sudo install minikube-linux-amd64 /usr/local/bin/minikube"
        echo ""
        echo "Steps:"
        echo "1. Start Minikube:"
        echo "   minikube start --driver=docker --cpus=4 --memory=4096"
        echo ""
        echo "2. Deploy to Kubernetes:"
        echo "   bash infra/k8s/deploy.sh"
        echo ""
        echo "3. Access services:"
        echo "   kubectl port-forward svc/llmops-rag-api-service 8000:8000 -n llmops"
        echo "   kubectl port-forward svc/llmops-streamlit-service 8501:8501 -n llmops"
        echo ""
        echo "4. View status:"
        echo "   kubectl get pods -n llmops"
        echo "   kubectl logs -f deployment/llmops-rag-api -n llmops"
        echo ""
        echo "For more details, see: infra/KUBERNETES_GUIDE.md"
        ;;
    
    3)
        echo -e "${YELLOW}Setting up GitHub Actions CI/CD...${NC}"
        echo ""
        echo "Prerequisites:"
        echo "  - GitHub repository"
        echo "  - GitHub Actions enabled"
        echo "  - Docker registry access (DockerHub, GHCR, etc.)"
        echo ""
        echo "Setup steps:"
        echo "1. Add GitHub Secrets:"
        echo "   Settings → Secrets and variables → Actions"
        echo "   - OPENAI_API_KEY"
        echo "   - (Optional) SLACK_WEBHOOK"
        echo ""
        echo "2. Workflows will run on:"
        echo "   - Push to main/develop"
        echo "   - Pull requests"
        echo "   - Manual trigger (gh workflow run)"
        echo ""
        echo "3. Monitor pipeline:"
        echo "   - GitHub Actions tab"
        echo "   - GitHub CLI: gh run list"
        echo "   - Slack notifications (if configured)"
        echo ""
        echo "4. Workflows:"
        echo "   - ci-cd.yml: Test, build, deploy"
        echo "   - security.yml: Weekly security scans"
        echo ""
        echo "For more details, see: infra/CI_CD_GUIDE.md"
        ;;
    
    4)
        echo "Exiting..."
        exit 0
        ;;
    
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Setup guide completed!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Review the appropriate guide in infra/"
echo "2. Follow the detailed instructions"
echo "3. Test your deployment locally"
echo "4. Deploy to production"
echo ""
echo "Documentation:"
echo "  - infra/DOCKER_GUIDE.md"
echo "  - infra/KUBERNETES_GUIDE.md"
echo "  - infra/CI_CD_GUIDE.md"
echo "  - infra/README.md"
