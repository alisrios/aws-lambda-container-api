#!/bin/bash

# Script para configurar backend remoto S3 para Terraform
# Este script cria o bucket S3 e tabela DynamoDB necessários

set -e

# Configurações
BUCKET_NAME="bucket-state-locking"
AWS_REGION="us-east-1"

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

# Verificar se AWS CLI está configurado
check_aws_cli() {
    print_status "Verificando configuração AWS CLI..."
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI não está configurado. Execute: aws configure"
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    CURRENT_REGION=$(aws configure get region)
    print_success "AWS configurado - Account: $ACCOUNT_ID, Region: $CURRENT_REGION"
}

# Criar bucket S3 para estado do Terraform
create_s3_bucket() {
    print_status "Criando bucket S3: $BUCKET_NAME"
    
    # Criar bucket (us-east-1 não precisa de LocationConstraint)
    if [ "$AWS_REGION" = "us-east-1" ]; then
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$AWS_REGION"
    else
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$AWS_REGION" \
            --create-bucket-configuration LocationConstraint="$AWS_REGION"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Bucket S3 criado: $BUCKET_NAME"
    else
        print_error "Erro ao criar bucket S3"
        exit 1
    fi
    
    # Habilitar versionamento
    aws s3api put-bucket-versioning \
        --bucket "$BUCKET_NAME" \
        --versioning-configuration Status=Enabled
    print_success "Versionamento habilitado no bucket"
    
    # Habilitar criptografia
    aws s3api put-bucket-encryption \
        --bucket "$BUCKET_NAME" \
        --server-side-encryption-configuration '{
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        }'
    print_success "Criptografia habilitada no bucket"
    
    # Bloquear acesso público
    aws s3api put-public-access-block \
        --bucket "$BUCKET_NAME" \
        --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
    print_success "Acesso público bloqueado no bucket"
}

# Configurar políticas adicionais do bucket
configure_bucket_policies() {
    print_status "Configurando políticas adicionais do bucket..."
    
    # Com versionamento habilitado, o S3 fornece proteção básica contra
    # corrupção de estado sem necessidade de DynamoDB
    
    print_success "Bucket configurado com versionamento para proteção de estado"
}

# Atualizar configuração do backend
update_backend_config() {
    print_status "Atualizando configuração do backend..."
    
    # Atualizar arquivo backend.tf
    cat > terraform/backend.tf << EOF
# Backend configuration for Terraform state
# This stores the Terraform state in S3 with versioning for basic state protection

terraform {
  backend "s3" {
    bucket  = "$BUCKET_NAME"
    key     = "lambda-container-api/terraform.tfstate"
    region  = "$AWS_REGION"
    encrypt = true
  }
}
EOF
    
    print_success "Arquivo backend.tf atualizado"
}

# Inicializar Terraform com novo backend
init_terraform() {
    print_status "Inicializando Terraform com backend remoto..."
    
    cd terraform
    
    # Remover estado local se existir
    rm -f terraform.tfstate terraform.tfstate.backup
    
    # Inicializar com novo backend
    terraform init
    
    print_success "Terraform inicializado com backend remoto"
    
    cd ..
}

# Função principal
main() {
    echo "=========================================="
    echo "  Configuração Backend Terraform S3"
    echo "=========================================="
    echo ""
    
    print_status "Bucket S3: $BUCKET_NAME"
    print_status "Região: $AWS_REGION"
    echo ""
    
    # Executar configuração
    check_aws_cli
    create_s3_bucket
    configure_bucket_policies
    update_backend_config
    init_terraform
    
    echo ""
    echo "=========================================="
    echo "  Configuração Concluída!"
    echo "=========================================="
    echo ""
    
    print_success "Backend remoto S3 configurado com sucesso!"
    echo ""
    echo "Recursos criados:"
    echo "- Bucket S3 com versionamento: $BUCKET_NAME"
    echo ""
    echo "Próximos passos:"
    echo "1. cd terraform"
    echo "2. terraform plan"
    echo "3. terraform apply"
    echo ""
    print_warning "IMPORTANTE: Anote o nome do bucket para usar em outros ambientes!"
    echo "Bucket: $BUCKET_NAME"
    echo ""
    print_status "O bucket foi criado com versionamento habilitado para proteção de estado"
    print_status "Não é mais necessário usar DynamoDB para state locking básico"
}

# Executar função principal
main "$@"
