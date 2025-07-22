.PHONY: help build up down logs test lint format clean dev prod restart health

# Colors for terminal output
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help: ## Mostra esta mensagem de ajuda
	@echo "$(YELLOW)PyNews Server - Comandos Disponíveis:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Constrói as imagens Docker
	@echo "$(YELLOW)Construindo imagens Docker...$(NC)"
	docker-compose build

up: ## Inicia os serviços
	@echo "$(YELLOW)Iniciando serviços...$(NC)"
	docker-compose up -d

down: ## Para os serviços
	@echo "$(YELLOW)Parando serviços...$(NC)"
	docker-compose down

logs: ## Mostra os logs dos serviços
	docker-compose logs -f pynews-api

test: ## Executa os testes
	@echo "$(YELLOW)Executando testes...$(NC)"
	poetry run pytest

test-cov: ## Executa os testes com coverage
	@echo "$(YELLOW)Executando testes com coverage...$(NC)"
	poetry run pytest --cov=app --cov-report=html

lint: ## Verifica o código com ruff
	@echo "$(YELLOW)Verificando código...$(NC)"
	poetry run ruff check .

format: ## Formata o código
	@echo "$(YELLOW)Formatando código...$(NC)"
	poetry run ruff format .

clean: ## Remove containers, volumes e imagens
	@echo "$(YELLOW)Limpando containers e volumes...$(NC)"
	docker-compose down -v --remove-orphans
	docker system prune -f

dev: build up ## Ambiente de desenvolvimento completo
	@echo "$(GREEN)Ambiente de desenvolvimento iniciado!$(NC)"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"

prod: ## Inicia em modo produção
	@echo "$(YELLOW)Iniciando em modo produção...$(NC)"
	docker-compose -f docker-compose.yaml up -d

restart: ## Reinicia os serviços
	@echo "$(YELLOW)Reiniciando serviços...$(NC)"
	docker-compose restart

health: ## Verifica o health check da API
	@echo "$(YELLOW)Verificando saúde da API...$(NC)"
	curl -f http://localhost:8000/api/healthcheck || echo "API não está respondendo"

install: ## Instala dependências com Poetry
	@echo "$(YELLOW)Instalando dependências...$(NC)"
	poetry install

shell: ## Entra no shell do container
	docker-compose exec pynews-api bash

setup: install build up ## Setup completo do projeto
	@echo "$(GREEN)Setup completo realizado!$(NC)"
	@echo "$(GREEN)Acesse: http://localhost:8000/docs$(NC)"
