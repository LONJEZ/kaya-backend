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