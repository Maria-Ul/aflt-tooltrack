.PHONY: build up down

COMPOSE := docker compose -f docker-compose.yml

build: ## Start all services
	$(COMPOSE) up -d --build

up: ## Start all services
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

migration-autogenerate:
	$(COMPOSE) exec backend alembic revision --autogenerate -m "$(MESSAGE)"

migration-upgrade:
	$(COMPOSE) exec backend alembic upgrade head
