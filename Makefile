.PHONY: build up down

COMPOSE := docker compose -f docker-compose.yml

build: ## Start all services
	$(COMPOSE) up -d --build

up: ## Start all services
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down
