#!/bin/bash

# Script para configurar backend remoto S3 para Terraform
# Este script cria o bucket S3 e tabela DynamoDB necessários

set -e

# Configurações
BUCKET_NAME="terraform-state-lambda-container-api-$(date +%s)"
DYNAMODB_TABLE="terraform-state-lock"
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
    
    # Criar bucket
    if aws s3api create-bucket \
        --bucket "$BUCKET_NAME" \
        --region "$AWS_REGION" \
        --create-bucket-configuration LocationConstraint="$AWS_REGION" 2>/dev/null; then
        print_success "Bucket S3 criado: $BUCKET_NAME"
    else
        print_warning "Bucket pode já existir ou erro na criação"
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

# Criar tabela DynamoDB para lock
create_dynamodb_table() {
    print_status "Criando tabela DynamoDB: $DYNAMODB_TABLE"
    
    if aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region "$AWS_REGION" &> /dev/null; then
        print_success "Tabela DynamoDB criada: $DYNAMODB_TABLE"
    else
        print_warning "Tabela pode já existir"
    fi
    
    # Aguardar tabela ficar ativa
    print_status "Aguardando tabela ficar ativa..."
    aws dynamodb wait table-exists --table-name "$DYNAMODB_TABLE" --region "$AWS_REGION"
    print_success "Tabela DynamoDB está ativa"
}

# Atualizar configuração do backend
update_backend_config() {
    print_status "Atualizando configuração do backend..."
    
    # Atualizar arquivo backend.tf
    cat > terraform/backend.tf << EOF
# Backend configuration for Terraform state
# This stores the Terraform state in S3 with DynamoDB locking

terraform {
  backend "s3" {
    bucket         = "$BUCKET_NAME"
    key            = "lambda-container-api/terraform.tfstate"
    region         = "$AWS_REGION"
    dynamodb_table = "$DYNAMODB_TABLE"
    encrypt        = true
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
    print_status "Tabela DynamoDB: $DYNAMODB_TABLE"
    print_status "Região: $AWS_REGION"
    echo ""
    
    # Executar configuração
    check_aws_cli
    create_s3_bucket
    create_dynamodb_table
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
    echo "- Bucket S3: $BUCKET_NAME"
    echo "- Tabela DynamoDB: $DYNAMODB_TABLE"
    echo ""
    echo "Próximos passos:"
    echo "1. cd terraform"
    echo "2. terraform plan"
    echo "3. terraform apply"
    echo ""
    print_warning "IMPORTANTE: Anote o nome do bucket para usar em outros ambientes!"
    echo "Bucket: $BUCKET_NAME"
}

# Executar função principal
main "$@"
