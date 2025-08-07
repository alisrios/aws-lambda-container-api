#!/bin/bash

# Script para testar a API deployada
# Testa todos os endpoints e valida as respostas

set -e

# Configurações
API_URL=""
VERBOSE=false

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: $0 [OPTIONS] <API_URL>"
    echo ""
    echo "Opções:"
    echo "  -v, --verbose    Mostrar detalhes das requisições"
    echo "  -h, --help       Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 https://abc123.execute-api.us-east-1.amazonaws.com"
    echo "  $0 -v https://abc123.execute-api.us-east-1.amazonaws.com"
    echo ""
    echo "Ou obter URL automaticamente do Terraform:"
    echo "  cd terraform && terraform output -raw api_gateway_url | xargs $0"
}

# Processar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            print_error "Opção desconhecida: $1"
            show_help
            exit 1
            ;;
        *)
            API_URL="$1"
            shift
            ;;
    esac
done

# Verificar se URL foi fornecida
if [ -z "$API_URL" ]; then
    print_error "URL da API é obrigatória"
    show_help
    exit 1
fi

# Remover trailing slash se existir
API_URL="${API_URL%/}"

# Função para fazer requisição HTTP
make_request() {
    local method="$1"
    local endpoint="$2"
    local expected_status="$3"
    local description="$4"
    
    local url="${API_URL}${endpoint}"
    local curl_opts="-s -w %{http_code}"
    
    if [ "$VERBOSE" = true ]; then
        curl_opts="-v -w %{http_code}"
    fi
    
    print_status "Testando: $description"
    print_status "URL: $url"
    
    # Fazer requisição
    local response=$(curl $curl_opts "$url" 2>/dev/null)
    local http_code="${response: -3}"
    local body="${response%???}"
    
    # Verificar status code
    if [ "$http_code" = "$expected_status" ]; then
        print_success "Status: $http_code ✓"
    else
        print_error "Status: $http_code (esperado: $expected_status) ✗"
        return 1
    fi
    
    # Mostrar resposta se verbose
    if [ "$VERBOSE" = true ]; then
        echo "Resposta:"
        echo "$body" | jq . 2>/dev/null || echo "$body"
    else
        # Validar JSON básico
        if echo "$body" | jq . >/dev/null 2>&1; then
            print_success "Resposta JSON válida ✓"
        else
            print_warning "Resposta não é JSON válido"
        fi
    fi
    
    echo ""
    return 0
}

# Função principal de teste
run_tests() {
    local failed_tests=0
    
    echo "=========================================="
    echo "  Testando API: $API_URL"
    echo "=========================================="
    echo ""
    
    # Teste 1: Endpoint /hello
    print_status "🧪 Teste 1: Endpoint /hello"
    if make_request "GET" "/hello" "200" "Hello World endpoint"; then
        print_success "Teste 1 passou ✓"
    else
        print_error "Teste 1 falhou ✗"
        ((failed_tests++))
    fi
    
    # Teste 2: Endpoint /echo com parâmetro
    print_status "🧪 Teste 2: Endpoint /echo com parâmetro"
    if make_request "GET" "/echo?msg=teste" "200" "Echo endpoint com parâmetro"; then
        print_success "Teste 2 passou ✓"
    else
        print_error "Teste 2 falhou ✗"
        ((failed_tests++))
    fi
    
    # Teste 3: Endpoint /echo sem parâmetro (deve retornar erro)
    print_status "🧪 Teste 3: Endpoint /echo sem parâmetro"
    if make_request "GET" "/echo" "400" "Echo endpoint sem parâmetro (erro esperado)"; then
        print_success "Teste 3 passou ✓"
    else
        print_error "Teste 3 falhou ✗"
        ((failed_tests++))
    fi
    
    # Teste 4: Endpoint /health
    print_status "🧪 Teste 4: Endpoint /health"
    if make_request "GET" "/health" "200" "Health check endpoint"; then
        print_success "Teste 4 passou ✓"
    else
        print_error "Teste 4 falhou ✗"
        ((failed_tests++))
    fi
    
    # Teste 5: Endpoint inexistente (deve retornar 404)
    print_status "🧪 Teste 5: Endpoint inexistente"
    if make_request "GET" "/inexistente" "404" "Endpoint inexistente (404 esperado)"; then
        print_success "Teste 5 passou ✓"
    else
        print_error "Teste 5 falhou ✗"
        ((failed_tests++))
    fi
    
    # Resumo dos testes
    echo "=========================================="
    echo "  Resumo dos Testes"
    echo "=========================================="
    
    local total_tests=5
    local passed_tests=$((total_tests - failed_tests))
    
    echo "Total de testes: $total_tests"
    echo "Testes passaram: $passed_tests"
    echo "Testes falharam: $failed_tests"
    echo ""
    
    if [ $failed_tests -eq 0 ]; then
        print_success "🎉 Todos os testes passaram!"
        echo ""
        echo "✅ API está funcionando corretamente"
        echo "✅ Todos os endpoints respondem adequadamente"
        echo "✅ Validação de parâmetros funcionando"
        echo "✅ Tratamento de erros implementado"
        return 0
    else
        print_error "❌ $failed_tests teste(s) falharam"
        echo ""
        echo "Verifique:"
        echo "- Se a API está deployada corretamente"
        echo "- Se a URL está correta"
        echo "- Se não há problemas de rede"
        echo "- Os logs do CloudWatch para mais detalhes"
        return 1
    fi
}

# Verificar se jq está instalado (para validação JSON)
if ! command -v jq &> /dev/null; then
    print_warning "jq não está instalado. Validação JSON será limitada."
    print_status "Para instalar: sudo apt-get install jq (Ubuntu) ou brew install jq (Mac)"
    echo ""
fi

# Executar testes
run_tests
