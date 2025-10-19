.PHONY: help setup install test clean run docker-build docker-run deploy

help:
	@echo "Kaya AI Backend - Available Commands"
	@echo "====================================="
	@echo "setup        - Setup Phase 6"
	@echo "install      - Install dependencies"
	@echo "run          - Start development server"
	@echo "test         - Run all tests"
	@echo "test-phase6  - Test Phase 6 features"
	@echo "lint         - Lint code"
	@echo "clean        - Clean generated files"
	@echo "docker-build - Build Docker image"
	@echo "docker-run   - Run with Docker"
	@echo "deploy       - Deploy to production"
	@echo "health       - Check system health"

setup:
	chmod +x setup_phase6.sh
	./setup_phase6.sh

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app

test-phase6:
	python3 scripts/test_advanced_analytics.py
	python3 scripts/pre_launch_checklist.py http://localhost:8007

lint:
	black app/ --check
	flake8 app/ --max-line-length=100

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

docker-build:
	docker build -t kaya-backend:latest -f Dockerfile.prod .

docker-run:
	docker-compose -f docker-compose.prod.yml up -d

deploy:
	chmod +x launch.sh
	./launch.sh

health:
	curl http://localhost:8007/health | jq
	curl http://localhost:8007/api/monitoring/health/detailed | jq
