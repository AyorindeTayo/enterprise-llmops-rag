#!/bin/bash
# Quick test runner script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$PROJECT_ROOT/llmops-env"

if [ ! -d "$VENV" ]; then
    echo "❌ Virtual environment not found at $VENV"
    exit 1
fi

case "${1:-help}" in
    "quick")
        echo "🧪 Running quick tests..."
        "$VENV/bin/python" -m pytest tests/ -q
        ;;
    "verbose")
        echo "🧪 Running tests (verbose)..."
        "$VENV/bin/python" -m pytest tests/ -vv
        ;;
    "watch")
        echo "🧪 Running tests (stop on first failure)..."
        "$VENV/bin/python" -m pytest tests/ -x --tb=short
        ;;
    "coverage")
        echo "🧪 Running tests with coverage..."
        "$VENV/bin/python" -m pytest tests/ \
            --cov=services --cov=agents --cov=embeddings --cov=vector_store \
            --cov-report=html --cov-report=term
        echo "✅ Coverage report: htmlcov/index.html"
        ;;
    *)
        echo "Usage: ./scripts/run-tests.sh [quick|verbose|watch|coverage]"
        echo ""
        echo "  quick      - Run all tests (quiet mode)"
        echo "  verbose    - Run all tests with detailed output"
        echo "  watch      - Run tests, stop on first failure"
        echo "  coverage   - Run tests with coverage report (htmlcov/)"
        exit 1
        ;;
esac
