#!/bin/bash

# AWS Lambda Container API - Setup Script
# Este script configura o ambiente de desenvolvimento

set -e

echo "🚀 Configurando AWS Lambda Container API..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
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

# Verificar se Python está instalado
check_python() {
    print_status "Verificando Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION encontrado"
    else
        print_error "Python 3 não encontrado. Por favor, instale Python 3.11+"
        exit 1
    fi
}

# Verificar se Docker está instalado
check_docker() {
    print_status "Verificando Docker..."
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker $DOCKER_VERSION encontrado"
    else
        print_error "Docker não encontrado. Por favor, instale Docker"
        exit 1
    fi
}

# Verificar se AWS CLI está instalado
check_aws_cli() {
    print_status "Verificando AWS CLI..."
    if command -v aws &> /dev/null; then
        AWS_VERSION=$(aws --version | cut -d' ' -f1 | cut -d'/' -f2)
        print_success "AWS CLI $AWS_VERSION encontrado"
    else
        print_warning "AWS CLI não encontrado. Instale para deploy na AWS"
    fi
}

# Verificar se Terraform está instalado
check_terraform() {
    print_status "Verificando Terraform..."
    if command -v terraform &> /dev/null; then
        TERRAFORM_VERSION=$(terraform --version | head -n1 | cut -d' ' -f2)
        print_success "Terraform $TERRAFORM_VERSION encontrado"
    else
        print_warning "Terraform não encontrado. Instale para gerenciar infraestrutura"
    fi
}

# Criar ambiente virtual Python
setup_python_env() {
    print_status "Configurando ambiente virtual Python..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Ambiente virtual criado"
    else
        print_warning "Ambiente virtual já existe"
    fi
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Atualizar pip
    pip install --upgrade pip
    
    # Instalar dependências
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
        print_success "Dependências de desenvolvimento instaladas"
    fi
    
    if [ -f "src/requirements.txt" ]; then
        pip install -r src/requirements.txt
        print_success "Dependências da aplicação instaladas"
    fi
}

# Configurar pre-commit hooks
setup_precommit() {
    print_status "Configurando pre-commit hooks..."
    
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        print_success "Pre-commit hooks instalados"
    else
        print_warning "Pre-commit não encontrado. Instale com: pip install pre-commit"
    fi
}

# Verificar configuração AWS
check_aws_config() {
    print_status "Verificando configuração AWS..."
    
    if aws sts get-caller-identity &> /dev/null; then
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        REGION=$(aws configure get region)
        print_success "AWS configurado - Account: $ACCOUNT_ID, Region: $REGION"
    else
        print_warning "AWS não configurado. Execute: aws configure"
    fi
}

# Executar testes
run_tests() {
    print_status "Executando testes..."
    
    if command -v pytest &> /dev/null; then
        pytest --version
        # pytest tests/ -v
        print_success "Ambiente de testes configurado"
    else
        print_warning "Pytest não encontrado"
    fi
}

# Verificar Docker Compose
check_docker_compose() {
    print_status "Verificando Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker Compose $COMPOSE_VERSION encontrado"
    else
        print_warning "Docker Compose não encontrado"
    fi
}

# Menu principal
main() {
    echo "=========================================="
    echo "  AWS Lambda Container API - Setup"
    echo "=========================================="
    echo ""
    
    # Verificações de dependências
    check_python
    check_docker
    check_docker_compose
    check_aws_cli
    check_terraform
    
    echo ""
    echo "=========================================="
    echo "  Configurando Ambiente"
    echo "=========================================="
    echo ""
    
    # Setup do ambiente
    setup_python_env
    setup_precommit
    check_aws_config
    run_tests
    
    echo ""
    echo "=========================================="
    echo "  Setup Concluído!"
    echo "=========================================="
    echo ""
    
    print_success "Ambiente configurado com sucesso!"
    echo ""
    echo "Próximos passos:"
    echo "1. Ativar ambiente virtual: source venv/bin/activate"
    echo "2. Configurar AWS (se necessário): aws configure"
    echo "3. Executar testes: make test"
    echo "4. Executar localmente: python run_local.py"
    echo "5. Deploy na AWS: cd terraform && terraform apply"
    echo ""
    echo "Para mais informações, consulte o README.md"
}

# Executar função principal
main "$@"
