ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
BACKEND_DIR := $(ROOT_DIR)/src/backend
COMPOSE_FILE := $(ROOT_DIR)/devops/docker-compose.yml

.PHONY: install up down test lint format run run-dev

install:
	cd $(BACKEND_DIR) && uv sync --all-groups

up:
	docker compose -f $(COMPOSE_FILE) up -d

down:
	docker compose -f $(COMPOSE_FILE) down

test:
	cd $(BACKEND_DIR) && uv run pytest

lint:
	cd $(BACKEND_DIR) && uv run ruff check .

format:
	cd $(BACKEND_DIR) && uv run ruff format .

run:
	cd $(BACKEND_DIR) && uv run uvicorn api.main:app --reload

run-dev:
	$(ROOT_DIR)/run-dev.sh
