#!/bin/bash
cd /app
export PYTHONPATH=/app:$PYTHONPATH
# Run with explicit python path handling
python -u -c "
import sys
import os
sys.path.insert(0, '/app')
os.chdir('/app')

# Now import and run uvicorn
from uvicorn.main import run
run('api_gateway.main:app', host='0.0.0.0', port=8000, log_level='info')
"
