#!/bin/bash

# Script para destruir infraestrutura com force delete do ECR
# Este script garante que o repositório ECR seja excluído mesmo com imagens

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

log "🚀 Iniciando processo de destruição da infraestrutura..."

# Verificar se há imagens no ECR antes da destruição
ECR_REPO_NAME=$(terraform output -raw ecr_repository_name 2>/dev/null || echo "")
if [ ! -z "$ECR_REPO_NAME" ]; then
    log "📦 Verificando imagens no repositório ECR: $ECR_REPO_NAME"
    
    # Listar imagens no repositório
    IMAGES=$(aws ecr list-images --repository-name "$ECR_REPO_NAME" --query 'imageIds[*].imageTag' --output text 2>/dev/null || echo "")
    
    if [ ! -z "$IMAGES" ] && [ "$IMAGES" != "None" ]; then
        warn "⚠️  Encontradas imagens no repositório ECR:"
        echo "$IMAGES" | tr '\t' '\n' | sed 's/^/    - /'
        warn "O repositório será excluído com force_delete=true"
    else
        log "✅ Nenhuma imagem encontrada no repositório ECR"
    fi
else
    warn "Não foi possível obter o nome do repositório ECR dos outputs"
fi

# Confirmar destruição
echo
warn "⚠️  ATENÇÃO: Esta operação irá destruir TODA a infraestrutura!"
warn "   - Lambda Function"
warn "   - API Gateway"
warn "   - ECR Repository (com TODAS as imagens)"
warn "   - CloudWatch Logs"
warn "   - IAM Roles e Policies"
warn "   - SNS Topics e CloudWatch Alarms"
echo

read -p "Tem certeza que deseja continuar? (digite 'yes' para confirmar): " confirm

if [ "$confirm" != "yes" ]; then
    log "❌ Operação cancelada pelo usuário"
    exit 0
fi

log "🔄 Executando terraform plan -destroy..."
if ! terraform plan -destroy -out=destroy.tfplan; then
    error "Falha no terraform plan -destroy"
    exit 1
fi

log "🗑️  Executando terraform destroy..."
if terraform apply destroy.tfplan; then
    success "✅ Infraestrutura destruída com sucesso!"
    
    # Limpar arquivo de plano
    rm -f destroy.tfplan
    
    log "🧹 Limpeza adicional..."
    
    # Verificar se o repositório ECR foi realmente excluído
    if [ ! -z "$ECR_REPO_NAME" ]; then
        if aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" >/dev/null 2>&1; then
            warn "⚠️  Repositório ECR ainda existe. Tentando exclusão manual..."
            if aws ecr delete-repository --repository-name "$ECR_REPO_NAME" --force; then
                success "✅ Repositório ECR excluído manualmente"
            else
                error "❌ Falha na exclusão manual do repositório ECR"
            fi
        else
            success "✅ Repositório ECR foi excluído com sucesso"
        fi
    fi
    
    log "🎉 Processo de destruição concluído!"
    echo
    success "Todos os recursos foram removidos da AWS"
    success "Não haverá mais custos relacionados a este projeto"
    
else
    error "❌ Falha na destruição da infraestrutura"
    rm -f destroy.tfplan
    exit 1
fi
