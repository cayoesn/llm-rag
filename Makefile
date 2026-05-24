.PHONY: help install run api worker test coverage lint format docker-up docker-down logs up down restart ps shell

DC = docker compose
VENV = .venv
PYTHON = $(VENV)/Scripts/python
PIP = $(VENV)/Scripts/pip

help:
	@echo "LLM-RAG Platform Makefile"
	@echo "  make install     - cria a virtualenv e instala dependencias"
	@echo "  make run         - sobe a API localmente com reload"
	@echo "  make api         - alias para make run"
	@echo "  make worker      - sobe o worker localmente"
	@echo "  make test        - executa os testes com coverage minimo"
	@echo "  make coverage    - gera coverage detalhado em terminal e HTML"
	@echo "  make lint        - roda ruff"
	@echo "  make format      - formata o codigo com black e ruff --fix"
	@echo "  make docker-up   - sobe a stack Docker completa"
	@echo "  make docker-down - derruba a stack Docker"
	@echo "  make logs        - acompanha logs da stack"
	@echo "  make restart     - reinicia os containers"
	@echo "  make ps          - lista os services em execucao"
	@echo "  make shell       - abre shell no container da API"

install:
	python -m venv $(VENV)
	$(PIP) install -r requirements-dev.txt

run:
	$(PYTHON) -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

api: run

worker:
	$(PYTHON) worker/main.py

test:
	$(PYTHON) -m pytest --cov=. --cov-report=term-missing --cov-fail-under=80

coverage:
	$(PYTHON) -m pytest --cov=. --cov-report=term-missing --cov-report=html:tests/htmlcov --cov-fail-under=80

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check . --fix

docker-up:
	$(DC) up -d --build

docker-down:
	$(DC) down

logs:
	$(DC) logs -f

up: docker-up

down: docker-down

restart:
	$(DC) restart

ps:
	$(DC) ps

shell:
	$(DC) exec api /bin/sh
