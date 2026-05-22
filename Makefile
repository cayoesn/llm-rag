.PHONY: help up down restart ps logs shell test lint format clean

# Variables
DC=docker compose
PYTHON=.venv/Scripts/python

help:
	@echo "LLM-RAG Platform Makefile"
	@echo "Usage:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make ps          - List running services"
	@echo "  make logs        - Show logs from all services"
	@echo "  make shell       - Open a shell in the API container"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linter"
	@echo "  make format      - Format code"
	@echo "  make clean       - Remove temporary files"

up:
	$(DC) up -d --build

down:
	$(DC) down

restart:
	$(DC) restart

ps:
	$(DC) ps

logs:
	$(DC) logs -f

test:
	$(PYTHON) -m pytest --cov=. --cov-report=term-missing --cov-fail-under=80

lint:
	$(PYTHON) -m ruff check .

format:
	black .
	ruff check . --fix

clean:
	rm -rf `find . -type d -name __pycache__`
	rm -rf .pytest_cache
	rm -rf .ruff_cache
