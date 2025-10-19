.PHONY: help install run dev test clean docker-build docker-up docker-down docker-logs docker-shell format lint

# Variables
PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker-compose
APP_NAME := fastapi-backend

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	$(PIP) install -r requirements.txt

run: ## Run the application locally
	$(PYTHON) -m uvicorn main:app --host 0.0.0.0 --port 8000

dev: ## Run the application in development mode with auto-reload
	$(PYTHON) -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run tests
	$(PYTHON) -m pytest tests/ -v

clean: ## Clean up cache files and databases
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.db" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

docker-build: ## Build Docker image
	$(DOCKER_COMPOSE) build

docker-up: ## Start Docker containers
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop Docker containers
	$(DOCKER_COMPOSE) down

docker-logs: ## View Docker container logs
	$(DOCKER_COMPOSE) logs -f

docker-shell: ## Open a shell in the Docker container
	$(DOCKER_COMPOSE) exec backend sh

docker-restart: ## Restart Docker containers
	$(DOCKER_COMPOSE) restart

format: ## Format code with black
	$(PYTHON) -m black .

lint: ## Lint code with flake8
	$(PYTHON) -m flake8 .

init-db: ## Initialize the database
	$(PYTHON) -c "from database import init_db; init_db()"

create-dummy-model: ## Create a dummy ML model for testing
	$(PYTHON) -c "from ml_engine import create_dummy_model; create_dummy_model()"

env: ## Create .env file from .env.example
	cp .env.example .env
	@echo ".env file created. Please update it with your configuration."

setup: env install init-db ## Complete setup: create env, install deps, init db
	@echo "Setup complete! Run 'make dev' to start the application."

all: clean install docker-build ## Clean, install, and build Docker image
