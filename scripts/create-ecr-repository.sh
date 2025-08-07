#!/bin/bash

# Script para criar apenas o repositório ECR
# Use este script se quiser criar o repositório antes do Terraform

set -e

# Configurações
PROJECT_NAME=${PROJECT_NAME:-"lambda-container-api"}
ENVIRONMENT=${ENVIRONMENT:-"dev"}
AWS_REGION=${AWS_REGION:-"us-east-1"}

# Construir nomes
ECR_REPOSITORY_NAME="${PROJECT_NAME}-${ENVIRONMENT}"

echo "📝 Criando repositório ECR..."
echo "📋 Configurações:"
echo "   - Projeto: ${PROJECT_NAME}"
echo "   - Ambiente: ${ENVIRONMENT}"
echo "   - Região: ${AWS_REGION}"
echo "   - Repositório ECR: ${ECR_REPOSITORY_NAME}"

# Verificar credenciais AWS
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ Credenciais AWS não configuradas!"
    echo "💡 Execute: aws configure"
    exit 1
fi

# Verificar se o repositório já existe
echo "🔍 Verificando se o repositório ECR já existe..."
if aws ecr describe-repositories --repository-names "${ECR_REPOSITORY_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1; then
    echo "⚠️  Repositório ECR já existe: ${ECR_REPOSITORY_NAME}"
    echo "ℹ️  Nenhuma ação necessária"
    exit 0
fi

# Criar o repositório ECR
echo "📝 Criando repositório ECR: ${ECR_REPOSITORY_NAME}"
aws ecr create-repository \
    --repository-name "${ECR_REPOSITORY_NAME}" \
    --region "${AWS_REGION}" \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256

echo "✅ Repositório ECR criado com sucesso!"
echo "🎯 Repositório: ${ECR_REPOSITORY_NAME}"
echo "💡 Agora você pode executar: ./build-and-push.sh"