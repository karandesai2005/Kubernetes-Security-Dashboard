.PHONY: help dev build test lint clean deploy

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start local dev environment
	docker compose up --build

build: ## Build all containers
	docker compose build

test: ## Run all tests
	cd backend && pytest tests/ -v --cov=app

lint: ## Lint backend + frontend
	cd backend && ruff check .
	cd frontend && npm run lint

clean: ## Stop and remove containers
	docker compose down -v

deploy-dev: ## Deploy to dev cluster
	kubectl apply -k k8s/overlays/dev

deploy-prod: ## Deploy to prod cluster
	kubectl apply -k k8s/overlays/prod

seed: ## Seed mock data for local dev (backend must be up)
	python scripts/seed-mock-data.py

dev-up: ## Alias
	docker compose up --build

logs: ## Tail logs
	docker compose logs -f --tail=80
