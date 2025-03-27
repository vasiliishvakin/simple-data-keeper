# Makefile for local development
HOST ?= 0.0.0.0
PORT ?= 8000

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "Installing dev dependencies..."
	pip install -r requirements-dev.txt

run:
	@echo "Running app with uvicorn on $(HOST):$(PORT)..."
	uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

test:
	@echo "Running tests..."
	pytest -ra -q

lint:
	@echo "Running linters..."
	ruff check . --fix

format:
	@echo "Formatting code..."
	ruff format .

check: lint format test
	@echo "Linting, formatting, and tests completed."

clean:
	@echo "Cleaning up..."
	rm -rf *.pyc __pycache__
	rm -rf .ruff_cache
	rm -rf .pytest_cache
