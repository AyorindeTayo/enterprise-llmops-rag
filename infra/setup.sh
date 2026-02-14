#!/bin/bash

# Make all scripts executable
chmod +x infra/docker/build.sh
chmod +x infra/k8s/deploy.sh
chmod +x infra/docker/test-api.sh

echo "✓ All scripts are now executable"
