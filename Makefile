.PHONY: dev install test lint

install:
	uv sync

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	ruff check app/ tests/

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down
