.PHONY: test test-verbose test-watch test-coverage help

help:
	@echo "Available targets:"
	@echo "  make test           - Run all tests (quiet)"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make test-watch     - Run tests, stopping on first failure"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make test-single    - Run a single test (use TEST=path/file.py::func)"

test:
	./llmops-env/bin/python -m pytest tests/ -q

test-verbose:
	./llmops-env/bin/python -m pytest tests/ -vv

test-watch:
	./llmops-env/bin/python -m pytest tests/ -x --tb=short

test-coverage:
	./llmops-env/bin/python -m pytest tests/ --cov=services --cov=agents --cov=embeddings --cov=vector_store --cov-report=html --cov-report=term

test-single:
	@[ -n "$(TEST)" ] || (echo "Usage: make test-single TEST=tests/test_api.py::test_ask_endpoint_mocked" && exit 1)
	./llmops-env/bin/python -m pytest $(TEST) -vv

.DEFAULT_GOAL := help
