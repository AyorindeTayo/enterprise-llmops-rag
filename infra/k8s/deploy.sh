#!/bin/bash

set -e

echo "================================"
echo "Deploying to Kubernetes (Minikube)"
echo "================================"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Check Minikube status
echo -e "${BLUE}Step 1: Checking Minikube status...${NC}"
minikube status || {
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start --driver=docker --cpus=4 --memory=4096
}

# Step 2: Set Minikube Docker environment
echo -e "${BLUE}Step 2: Setting Docker environment for Minikube...${NC}"
eval $(minikube docker-env)

# Step 3: Build Docker images in Minikube
echo -e "${BLUE}Step 3: Building Docker images in Minikube...${NC}"
docker build -f infra/docker/Dockerfile -t llmops-rag-api:latest .
docker build -f infra/docker/Dockerfile.streamlit -t llmops-streamlit:latest .

# Step 4: Create namespace
echo -e "${BLUE}Step 4: Creating Kubernetes namespace...${NC}"
kubectl apply -f infra/k8s/namespace.yaml

# Step 5: Creating directories for persistent volumes
echo -e "${BLUE}Step 5: Creating directories for persistent volumes...${NC}"
minikube ssh "sudo mkdir -p /mnt/data/vector-store /mnt/data/logs"
minikube ssh "sudo chmod 777 /mnt/data/vector-store /mnt/data/logs"

# Step 6: Deploy persistent volumes
echo -e "${BLUE}Step 6: Deploying persistent volumes...${NC}"
kubectl apply -f infra/k8s/persistent-volumes.yaml

# Step 7: Deploy services
echo -e "${BLUE}Step 7: Deploying Kubernetes services...${NC}"
kubectl apply -f infra/k8s/service.yaml
kubectl apply -f infra/k8s/deployment.yaml

# Step 8: Wait for deployment to be ready
echo -e "${BLUE}Step 8: Waiting for deployments to be ready...${NC}"
kubectl rollout status deployment/llmops-rag-api -n llmops --timeout=5m
kubectl rollout status deployment/llmops-streamlit -n llmops --timeout=5m

# Step 9: Show deployment status
echo -e "${BLUE}Step 9: Deployment status...${NC}"
kubectl get all -n llmops

# Step 10: Port forwarding info
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "To access your services, run:"
echo ""
echo -e "${YELLOW}For API Gateway:${NC}"
echo "  kubectl port-forward svc/llmops-rag-api-service 8000:8000 -n llmops"
echo "  Then access: http://localhost:8000"
echo ""
echo -e "${YELLOW}For Streamlit UI:${NC}"
echo "  kubectl port-forward svc/llmops-streamlit-service 8501:8501 -n llmops"
echo "  Then access: http://localhost:8501"
echo ""
echo -e "${YELLOW}Or use Minikube service:${NC}"
echo "  minikube service llmops-streamlit-service -n llmops"
echo ""
echo "Useful kubectl commands:"
echo "  kubectl get pods -n llmops              # List all pods"
echo "  kubectl logs -f <pod-name> -n llmops    # Follow pod logs"
echo "  kubectl describe pod <pod-name> -n llmops"
echo "  kubectl delete -f infra/k8s/            # Delete all k8s resources"