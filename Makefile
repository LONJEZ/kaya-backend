.PHONY: help setup run test init-db load-data clean docker-build docker-run

help:
	@echo "Kaya AI Backend - Available Commands"
	@echo "====================================="
	@echo "setup        - Install dependencies"
	@echo "init-db      - Initialize BigQuery tables"
	@echo "load-data    - Load sample data"
	@echo "run          - Start development server"
	@echo "test         - Run API tests"
	@echo "docker-build - Build Docker image"
	@echo "docker-run   - Run with Docker Compose"
	@echo "clean        - Remove generated files"

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

init-db:
	python3 scripts/init_bigquery.py

load-data:
	python3 scripts/load_sample_data.py

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	python3 scripts/test_api.py

docker-build:
	docker build -t kaya-backend .

docker-run:
	docker-compose up -d

clean:
	rm -rf venv __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: phase3-demo phase3-test phase3-benchmark

phase3-demo:
	@echo "Running Phase 3 demo..."
	@chmod +x demo_phase3.sh
	@./demo_phase3.sh

phase3-test:
	@echo "Running Phase 3 tests..."
	@python3 scripts/test_analytics.py
	@python3 scripts/test_cache.py

phase3-benchmark:
	@echo "Running performance benchmarks..."
	@python3 scripts/benchmark_analytics.py

phase3-integration:
	@echo "Running integration test..."
	@python3 scripts/integration_test.py

# Complete test suite
test-all: phase3-test phase3-benchmark phase3-integration
	@echo "✅ All tests complete"
