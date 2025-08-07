#!/bin/bash

# Script para build e push da imagem Docker para ECR
# Este script deve ser executado antes do terraform apply

set -e

BUILD_ARGS=""
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --no-cache)
            BUILD_ARGS="--no-cache"
            ;;
        *)
            echo "Unknown parameter passed: $1"
            exit 1
            ;;
    esac
    shift
done

# Configurações
PROJECT_NAME=${PROJECT_NAME:-"lambda-container-api"}
ENVIRONMENT=${ENVIRONMENT:-"dev"}
AWS_REGION=${AWS_REGION:-"us-east-1"}

# Obter hash do commit Git (7 primeiros dígitos)
if git rev-parse --git-dir > /dev/null 2>&1; then
    GIT_COMMIT_HASH=$(git rev-parse --short=7 HEAD 2>/dev/null || echo "no-commit")
else
    GIT_COMMIT_HASH="no-git"
fi

# Tags da imagem
ECR_IMAGE_TAG_LATEST="latest"
ECR_IMAGE_TAG_COMMIT="${GIT_COMMIT_HASH}"

# Construir nomes
ECR_REPOSITORY_NAME="${PROJECT_NAME}-${ENVIRONMENT}"
LAMBDA_FUNCTION_NAME="${PROJECT_NAME}-${ENVIRONMENT}"

echo "🚀 Iniciando build e push da imagem Docker..."
echo "📋 Configurações:"
echo "   - Projeto: ${PROJECT_NAME}"
echo "   - Ambiente: ${ENVIRONMENT}"
echo "   - Região: ${AWS_REGION}"
echo "   - Repositório ECR: ${ECR_REPOSITORY_NAME}"
echo "   - Tag Latest: ${ECR_IMAGE_TAG_LATEST}"
echo "   - Tag Commit: ${ECR_IMAGE_TAG_COMMIT}"

# Obter Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FULL_IMAGE_NAME_LATEST="${ECR_URI}/${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_LATEST}"
FULL_IMAGE_NAME_COMMIT="${ECR_URI}/${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_COMMIT}"

echo "📦 URIs das imagens:"
echo "   - Latest: ${FULL_IMAGE_NAME_LATEST}"
echo "   - Commit: ${FULL_IMAGE_NAME_COMMIT}"

# Verificar se o repositório ECR existe
echo "🔍 Verificando se o repositório ECR existe..."
if ! aws ecr describe-repositories --repository-names "${ECR_REPOSITORY_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1; then
    echo "❌ Repositório ECR não existe: ${ECR_REPOSITORY_NAME}"
    echo "💡 Para criar o repositório, execute:"
    echo "   aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --region ${AWS_REGION}"
    echo "   ou use o Terraform para criar todos os recursos"
    exit 1
else
    echo "✅ Repositório ECR encontrado: ${ECR_REPOSITORY_NAME}"
fi

# Login no ECR
echo "🔐 Fazendo login no ECR..."
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_URI}"

# Limpar imagens antigas locais para evitar conflitos
echo "🧹 Limpando imagens antigas locais..."
docker rmi "${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_LATEST}" 2>/dev/null || true
docker rmi "${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_COMMIT}" 2>/dev/null || true
docker rmi "${FULL_IMAGE_NAME_LATEST}" 2>/dev/null || true
docker rmi "${FULL_IMAGE_NAME_COMMIT}" 2>/dev/null || true

# Verificar se o Docker buildx está disponível e configurar se necessário
echo "🔧 Verificando Docker buildx..."
if ! docker buildx version >/dev/null 2>&1; then
    echo "⚠️  Docker buildx não está disponível, usando docker build padrão"
    DOCKER_BUILD_CMD="docker build"
else
    echo "✅ Docker buildx disponível"
    # Criar builder se não existir
    docker buildx create --name lambda-builder --use 2>/dev/null || docker buildx use lambda-builder 2>/dev/null || true
    DOCKER_BUILD_CMD="docker buildx build --load"
fi

# Build da imagem Docker com plataforma específica para Lambda
echo "🏗️  Fazendo build da imagem Docker para AWS Lambda (linux/amd64)..."
${DOCKER_BUILD_CMD} --platform linux/amd64 ${BUILD_ARGS} -t "${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_LATEST}" -t "${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_COMMIT}" .

# Tag as imagens com os nomes completos do ECR
echo "🏷️  Criando tags para ECR..."
docker tag "${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_LATEST}" "${FULL_IMAGE_NAME_LATEST}"
docker tag "${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_COMMIT}" "${FULL_IMAGE_NAME_COMMIT}"

# Verificar a imagem antes do push
echo "� Vezrificando a imagem construída..."
docker inspect "${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_LATEST}" > /dev/null

# Testar se a imagem pode ser executada (teste básico)
echo "🧪 Testando a imagem localmente..."
# Para imagens Lambda, testamos se os arquivos estão presentes
docker run --rm --platform linux/amd64 --entrypoint="" "${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_LATEST}" python -c "
import lambda_function
import app
print('✅ Todos os módulos importados com sucesso')
print('✅ Imagem OK')
" || {
    echo "❌ Erro: A imagem não passou no teste básico"
    exit 1
}

# Verificar se a imagem tem o formato correto para Lambda
echo "🔍 Verificando compatibilidade da imagem com Lambda..."
docker run --rm --platform linux/amd64 --entrypoint="" "${ECR_REPOSITORY_NAME}:${ECR_IMAGE_TAG_LATEST}" ls -la /lambda-entrypoint.sh >/dev/null 2>&1 || {
    echo "⚠️  Aviso: Imagem pode não ter o entrypoint correto para Lambda"
}

# Verificar se as imagens foram taggeadas corretamente
echo "🔍 Verificando tags das imagens..."
docker images | grep "${ECR_REPOSITORY_NAME}" || {
    echo "❌ Erro: Imagens não foram taggeadas corretamente"
    exit 1
}

# Verificar o manifest da imagem para garantir compatibilidade com Lambda
echo "🔍 Verificando manifest da imagem..."
docker inspect "${FULL_IMAGE_NAME_LATEST}" --format='{{.Architecture}}' | grep -q "amd64" || {
    echo "❌ Erro: Imagem não está na arquitetura amd64"
    exit 1
}

# Verificar se a imagem tem o formato OCI correto
echo "🔍 Verificando formato da imagem..."
docker inspect "${FULL_IMAGE_NAME_LATEST}" --format='{{.Config.Cmd}}' | grep -q "lambda_function.lambda_handler" || {
    echo "⚠️  Aviso: CMD da imagem pode não estar configurado corretamente"
}

# Push das imagens para ECR
echo "📤 Fazendo push das imagens para ECR..."
echo "   - Enviando tag latest..."
docker push "${FULL_IMAGE_NAME_LATEST}"
echo "   - Enviando tag commit (${ECR_IMAGE_TAG_COMMIT})..."
docker push "${FULL_IMAGE_NAME_COMMIT}"

# Verificar se o push foi bem-sucedido
echo "✅ Verificando se as imagens foram enviadas corretamente..."
aws ecr describe-images --repository-name "${ECR_REPOSITORY_NAME}" --region "${AWS_REGION}" --image-ids imageTag="${ECR_IMAGE_TAG_LATEST}" >/dev/null 2>&1 || {
    echo "❌ Erro: Falha ao verificar imagem no ECR"
    exit 1
}

echo "✅ Build e push concluídos com sucesso!"
echo "🎯 Imagens disponíveis em:"
echo "   - Latest: ${FULL_IMAGE_NAME_LATEST}"
echo "   - Commit: ${FULL_IMAGE_NAME_COMMIT}"

# Verificar se a função Lambda existe e atualizar o código se necessário
echo "🔍 Verificando se a função Lambda existe..."
if aws lambda get-function --function-name "${LAMBDA_FUNCTION_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1; then
    echo "🔄 Atualizando código da função Lambda..."
    aws lambda update-function-code \
        --function-name "${LAMBDA_FUNCTION_NAME}" \
        --image-uri "${FULL_IMAGE_NAME_LATEST}" \
        --region "${AWS_REGION}"
    echo "✅ Código da função Lambda atualizado!"
else
    echo "ℹ️  Função Lambda não existe ainda - será criada pelo Terraform"
fi

echo "🎉 Processo concluído com sucesso!"