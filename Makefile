.PHONY: build up down

COMPOSE := docker compose -f docker-compose.yml

ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

ifeq ($(DETECTED_OS),Windows)
    COPY_CMD := copy .env.dist .env
else
    COPY_CMD := cp .env.dist .env
endif

init:
	$(COPY_CMD)
	make build
	make restore


build: ## Start all services
	$(COMPOSE) up -d --build

up: ## Start all services
	$(COMPOSE) up -d

restore:
	docker exec aflt-tooltrack-db-1 psql -U myuser -d postgres -h localhost -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'mydb' AND pid <> pg_backend_pid();"
	docker exec aflt-tooltrack-db-1 psql -U myuser -d postgres -h localhost -c "DROP DATABASE IF EXISTS mydb;"
	docker exec aflt-tooltrack-db-1 psql -U myuser -d postgres -h localhost -c "CREATE DATABASE mydb;"
	docker exec -i aflt-tooltrack-db-1 psql -U myuser -d mydb -h localhost < dump.sql

down: ## Stop all services
	$(COMPOSE) down

migration-autogenerate:
	$(COMPOSE) exec backend alembic revision --autogenerate -m "$(MESSAGE)"

migration-upgrade:
	$(COMPOSE) exec backend alembic upgrade head

test:
	@echo "Running tests in Docker..."
	$(COMPOSE) run --rm backend pytest /app/app/tests/
