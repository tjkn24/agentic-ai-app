.PHONY: dev ui install test lint

PYTHON := .venv/bin/python
UVICORN := .venv/bin/uvicorn
CHAINLIT := .venv/bin/chainlit
PYTEST := .venv/bin/pytest
RUFF := .venv/bin/ruff

install:
	uv sync

dev:
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

ui:
	@lsof -ti:8001 | xargs kill -9 2>/dev/null || true
	$(CHAINLIT) run ui.py --port 8001

test:
	$(PYTEST) tests/ -v

lint:
	$(RUFF) check app/ tests/

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down
