#!/bin/bash

set -e

echo "================================"
echo "Deploying MLflow Tracking Server"
echo "================================"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Deploy MLflow PersistentVolume
echo -e "${BLUE}Step 1: Deploying MLflow PersistentVolume...${NC}"
kubectl apply -f infra/k8s/mlflow-pv.yaml

# Step 2: Deploy MLflow Deployment
echo -e "${BLUE}Step 2: Deploying MLflow Deployment...${NC}"
kubectl apply -f infra/k8s/mlflow-deployment.yaml

# Step 3: Wait for MLflow to be ready
echo -e "${BLUE}Step 3: Waiting for MLflow to be ready...${NC}"
kubectl rollout status deployment/mlflow -n llmops --timeout=5m

# Step 4: Get service information
echo -e "${GREEN}✓ MLflow deployment successful!${NC}"
echo ""
echo -e "${BLUE}Access MLflow:${NC}"
echo ""
echo "Local port-forward:"
echo "  kubectl port-forward svc/mlflow-service 5000:5000 -n llmops"
echo "  http://localhost:5000"
echo ""
echo "Within cluster:"
echo "  MLFLOW_TRACKING_URI=http://mlflow-service:5000 (from pods in llmops namespace)"
echo ""
echo -e "${BLUE}Node IP (for NodePort):${NC}"
minikube ip
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Ensure API and Streamlit pods have MLFLOW_TRACKING_URI env var set"
echo "2. Configure applications to use: http://mlflow-service:5000"
echo "3. Set MLFLOW_TRACKING_URI in pod environment variables"
echo ""
