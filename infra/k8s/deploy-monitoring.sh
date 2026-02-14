#!/bin/bash

set -e

echo "================================"
echo "Deploying Prometheus Monitoring"
echo "================================"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Deploy Prometheus ConfigMap
echo -e "${BLUE}Step 1: Deploying Prometheus ConfigMap...${NC}"
kubectl apply -f infra/k8s/prometheus-configmap.yaml

# Step 2: Deploy Prometheus AlertRules
echo -e "${BLUE}Step 2: Deploying Prometheus Alert Rules...${NC}"
kubectl apply -f infra/k8s/prometheus-alert-rules.yaml

# Step 3: Deploy Prometheus
echo -e "${BLUE}Step 3: Deploying Prometheus...${NC}"
kubectl apply -f infra/k8s/prometheus-deployment.yaml

# Step 4: Deploy Prometheus Service
echo -e "${BLUE}Step 4: Deploying Prometheus Service...${NC}"
kubectl apply -f infra/k8s/prometheus-service.yaml

# Step 5: Wait for Prometheus to be ready
echo -e "${BLUE}Step 5: Waiting for Prometheus to be ready...${NC}"
kubectl rollout status deployment/prometheus -n llmops --timeout=5m

# Step 6: Deploy Grafana
echo -e "${BLUE}Step 6: Deploying Grafana...${NC}"
kubectl apply -f infra/k8s/grafana-deployment.yaml

# Step 7: Wait for Grafana to be ready
echo -e "${BLUE}Step 7: Waiting for Grafana to be ready...${NC}"
kubectl rollout status deployment/grafana -n llmops --timeout=5m

# Step 8: Get service information
echo -e "${GREEN}✓ Monitoring deployment successful!${NC}"
echo ""
echo -e "${BLUE}Access your monitoring services:${NC}"
echo ""
echo "Prometheus:"
echo "  kubectl port-forward svc/prometheus-service 9090:9090 -n llmops"
echo "  http://localhost:9090"
echo ""
echo "Grafana:"
echo "  kubectl port-forward svc/grafana-service 3000:3000 -n llmops"
echo "  http://localhost:3000"
echo "  (Default credentials: admin/admin)"
echo ""
echo -e "${BLUE}Node IPs (for NodePort access):${NC}"
minikube ip
echo ""
echo "Prometheus NodePort: http://$(minikube ip):30090"
echo "Grafana NodePort: http://$(minikube ip):30300"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure Grafana datasources if not auto-discovered"
echo "2. Import dashboards from https://grafana.com/dashboards"
echo "3. Set up alerting rules and notifications"
