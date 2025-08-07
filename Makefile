# Makefile para AWS Lambda Container API

.PHONY: help build run test stop clean logs

# Variáveis
COMPOSE_FILE = docker-compose.yml
PROJECT_NAME = lambda-container-api

help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Constrói as imagens Docker
	@echo "🔨 Construindo imagens Docker..."
	docker-compose -f $(COMPOSE_FILE) build

run: ## Inicia todos os serviços
	@echo "🚀 Iniciando serviços..."
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "✅ Serviços iniciados!"
	@echo "📱 Interface de teste: http://localhost:8000/test.html"
	@echo "🔗 Lambda API: http://localhost:9000"

test: ## Inicia os serviços e abre a página de teste
	@make run
	@echo "🌐 Abrindo página de teste..."
	@sleep 3
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:8000/test.html; \
	elif command -v python3 >/dev/null 2>&1; then \
		python3 -c "import webbrowser; webbrowser.open('http://localhost:8000/test.html')"; \
	elif command -v python >/dev/null 2>&1; then \
		python -c "import webbrowser; webbrowser.open('http://localhost:8000/test.html')"; \
	else \
		echo "⚠️  Abra manualmente no browser: http://localhost:8000/test.html"; \
	fi

stop: ## Para todos os serviços
	@echo "⏹️  Parando serviços..."
	docker-compose -f $(COMPOSE_FILE) down

clean: ## Remove containers, imagens e volumes
	@echo "🧹 Limpando recursos Docker..."
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f

logs: ## Mostra logs dos serviços
	docker-compose -f $(COMPOSE_FILE) logs -f

status: ## Mostra status dos serviços
	@echo "📊 Status dos serviços:"
	docker-compose -f $(COMPOSE_FILE) ps

restart: ## Reinicia todos os serviços
	@make stop
	@make run

dev: ## Modo desenvolvimento (com logs em tempo real)
	@echo "🔧 Iniciando em modo desenvolvimento..."
	docker-compose -f $(COMPOSE_FILE) up --build

# Comandos de teste específicos
test-curl: ## Testa a API usando curl
	@echo "🧪 Testando API com curl..."
	@echo "Endpoint /hello:"
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
		-H "Content-Type: application/json" \
		-d '{"httpMethod":"GET","path":"/hello","queryStringParameters":null}' | jq .
	@echo "\nEndpoint /echo:"
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
		-H "Content-Type: application/json" \
		-d '{"httpMethod":"GET","path":"/echo","queryStringParameters":{"msg":"Hello Docker!"}}' | jq .

health: ## Verifica saúde dos serviços
	@echo "🏥 Verificando saúde dos serviços..."
	@echo "Lambda API:"
	@curl -s http://localhost:9000/2015-03-31/functions/function/invocations \
		-X POST \
		-H "Content-Type: application/json" \
		-d '{"httpMethod":"GET","path":"/hello","queryStringParameters":null}' | jq .message || echo "❌ Lambda API não está respondendo"
	@echo "Test Server:"
	@curl -s http://localhost:8000/test.html > /dev/null && echo "✅ Test Server OK" || echo "❌ Test Server não está respondendo"

open: ## Mostra URLs para acesso manual
	@echo "🌐 URLs disponíveis:"
	@echo "📱 Interface de teste: http://localhost:8000/test.html"
	@echo "🔗 Lambda API: http://localhost:9000"
	@echo ""
	@echo "💡 Para testar via curl:"
	@echo "curl -XPOST 'http://localhost:9000/2015-03-31/functions/function/invocations' \\"
	@echo "     -H 'Content-Type: application/json' \\"
	@echo "     -d '{\"httpMethod\":\"GET\",\"path\":\"/hello\",\"queryStringParameters\":null}'"