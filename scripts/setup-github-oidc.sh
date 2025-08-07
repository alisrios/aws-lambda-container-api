#!/bin/bash

# Script para configurar GitHub OIDC com AWS
# Este script configura o provider OIDC e a role IAM necessária para GitHub Actions

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Verificar se estamos no diretório correto
if [ ! -f "main.tf" ]; then
    error "Este script deve ser executado no diretório terraform/"
    exit 1
fi

log "🚀 Configurando GitHub OIDC para AWS..."

# Verificar se as variáveis necessárias estão definidas
if [ -z "$GITHUB_REPOSITORY" ]; then
    warn "Variável GITHUB_REPOSITORY não definida"
    read -p "Digite o nome do repositório GitHub (formato: owner/repo): " GITHUB_REPOSITORY
    export GITHUB_REPOSITORY
fi

if [ -z "$TERRAFORM_STATE_BUCKET" ]; then
    warn "Variável TERRAFORM_STATE_BUCKET não definida"
    read -p "Digite o nome do bucket S3 para estado do Terraform: " TERRAFORM_STATE_BUCKET
    export TERRAFORM_STATE_BUCKET
fi

log "📋 Configuração:"
log "  - Repositório GitHub: $GITHUB_REPOSITORY"
log "  - Bucket S3: $TERRAFORM_STATE_BUCKET"
log "  - Região AWS: $(aws configure get region || echo 'us-east-1')"

echo
read -p "Confirma a configuração acima? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    log "❌ Configuração cancelada"
    exit 0
fi

# Verificar se o arquivo terraform.tfvars existe
if [ ! -f "terraform.tfvars" ]; then
    log "📝 Criando arquivo terraform.tfvars..."
    cat > terraform.tfvars << EOF
# Configuração do projeto
project_name = "lambda-container-api"
environment  = "dev"
aws_region   = "$(aws configure get region || echo 'us-east-1')"

# Configuração GitHub OIDC
github_repository      = "$GITHUB_REPOSITORY"
terraform_state_bucket = "$TERRAFORM_STATE_BUCKET"

# Configuração da Lambda
lambda_memory_size = 512
lambda_timeout     = 30
ecr_image_tag      = "latest"

# Configuração do API Gateway
api_cors_allow_origins = ["*"]
api_cors_allow_methods = ["GET", "POST", "OPTIONS"]
api_cors_allow_headers = ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Request-ID"]
EOF
    success "✅ Arquivo terraform.tfvars criado"
else
    log "📝 Atualizando arquivo terraform.tfvars existente..."
    
    # Atualizar variáveis específicas do OIDC
    if grep -q "github_repository" terraform.tfvars; then
        sed -i "s/github_repository.*/github_repository = \"$GITHUB_REPOSITORY\"/" terraform.tfvars
    else
        echo "github_repository = \"$GITHUB_REPOSITORY\"" >> terraform.tfvars
    fi
    
    if grep -q "terraform_state_bucket" terraform.tfvars; then
        sed -i "s/terraform_state_bucket.*/terraform_state_bucket = \"$TERRAFORM_STATE_BUCKET\"/" terraform.tfvars
    else
        echo "terraform_state_bucket = \"$TERRAFORM_STATE_BUCKET\"" >> terraform.tfvars
    fi
    
    success "✅ Arquivo terraform.tfvars atualizado"
fi

log "🔄 Inicializando Terraform..."
if ! terraform init; then
    error "Falha na inicialização do Terraform"
    exit 1
fi

log "✅ Validando configuração Terraform..."
if ! terraform validate; then
    error "Configuração Terraform inválida"
    exit 1
fi

log "📋 Executando terraform plan..."
if ! terraform plan -out=oidc-setup.tfplan; then
    error "Falha no terraform plan"
    exit 1
fi

echo
warn "⚠️  ATENÇÃO: Esta operação irá criar recursos AWS!"
warn "   - GitHub OIDC Identity Provider"
warn "   - IAM Role para GitHub Actions"
warn "   - Políticas IAM necessárias"
echo

read -p "Deseja aplicar as mudanças? (y/N): " apply_confirm
if [[ ! $apply_confirm =~ ^[Yy]$ ]]; then
    log "❌ Aplicação cancelada"
    rm -f oidc-setup.tfplan
    exit 0
fi

log "🚀 Aplicando configuração..."
if terraform apply oidc-setup.tfplan; then
    success "✅ Configuração OIDC aplicada com sucesso!"
    
    # Obter outputs importantes
    log "📋 Informações importantes:"
    
    ROLE_ARN=$(terraform output -raw github_actions_role_arn 2>/dev/null || echo "N/A")
    OIDC_PROVIDER_ARN=$(terraform output -raw github_oidc_provider_arn 2>/dev/null || echo "N/A")
    
    echo
    success "🔑 Role ARN para GitHub Actions:"
    echo "   $ROLE_ARN"
    echo
    success "🔗 OIDC Provider ARN:"
    echo "   $OIDC_PROVIDER_ARN"
    echo
    
    # Limpar arquivo de plano
    rm -f oidc-setup.tfplan
    
    log "📝 Próximos passos:"
    echo
    echo "1. 🔧 Configure as variáveis no GitHub:"
    echo "   - Vá para: https://github.com/$GITHUB_REPOSITORY/settings/variables/actions"
    echo "   - Adicione as seguintes Repository Variables:"
    echo
    echo "   AWS_ROLE_TO_ASSUME = $ROLE_ARN"
    echo "   TERRAFORM_STATE_BUCKET = $TERRAFORM_STATE_BUCKET"
    echo
    echo "2. 🚀 Execute um push para testar o pipeline:"
    echo "   git add ."
    echo "   git commit -m 'Configure GitHub OIDC'"
    echo "   git push origin main"
    echo
    echo "3. 🔍 Monitore o pipeline em:"
    echo "   https://github.com/$GITHUB_REPOSITORY/actions"
    echo
    
    success "🎉 Configuração OIDC concluída com sucesso!"
    
else
    error "❌ Falha na aplicação da configuração"
    rm -f oidc-setup.tfplan
    exit 1
fi
