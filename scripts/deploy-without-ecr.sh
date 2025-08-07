#!/bin/bash

# Script para deploy sem ECR (usando imagem placeholder)
# Útil para testes quando não há credenciais AWS configuradas

set -e

echo "🚀 Deploy sem ECR - Usando imagem placeholder..."

# Verificar se a imagem local existe
if ! docker image inspect lambda-container-api-dev:latest >/dev/null 2>&1; then
    echo "❌ Imagem local não encontrada. Execute primeiro:"
    echo "   docker build --platform linux/amd64 -t lambda-container-api-dev:latest ."
    exit 1
fi

echo "✅ Imagem local encontrada"

# Navegar para o diretório terraform
cd terraform

# Criar um arquivo de variáveis temporário
cat > terraform.tfvars.tmp << EOF
# Configuração temporária para deploy sem ECR
project_name = "lambda-container-api"
environment = "dev"
aws_region = "us-east-1"
ecr_image_tag = "placeholder"
EOF

echo "📝 Arquivo de variáveis temporário criado"

# Modificar temporariamente o main.tf para usar uma imagem placeholder
echo "⚠️  ATENÇÃO: Este é um deploy de teste sem ECR"
echo "   A função Lambda será criada mas não funcionará até que"
echo "   uma imagem real seja enviada para o ECR"

echo ""
echo "🔧 Para fazer o deploy completo:"
echo "1. Configure suas credenciais AWS: aws configure"
echo "2. Execute: ../build-and-push.sh"
echo "3. Execute: terraform apply"

echo ""
echo "📋 Comandos Terraform disponíveis:"
echo "   terraform init    - Inicializar"
echo "   terraform plan    - Ver mudanças"
echo "   terraform apply   - Aplicar mudanças"
echo "   terraform destroy - Destruir recursos"

echo ""
echo "🎯 Próximos passos:"
echo "1. Configure AWS CLI com suas credenciais"
echo "2. Execute o script build-and-push.sh"
echo "3. A função Lambda será atualizada automaticamente"