#!/bin/bash

# Script para testar o build da imagem Docker localmente
set -e

echo "🧪 Testando build da imagem Docker para AWS Lambda..."

# Verificar se os arquivos necessários existem
echo "📋 Verificando arquivos necessários..."

if [ ! -f "src/lambda_function.py" ]; then
    echo "❌ Arquivo src/lambda_function.py não encontrado!"
    exit 1
fi

if [ ! -f "src/app.py" ]; then
    echo "❌ Arquivo src/app.py não encontrado!"
    exit 1
fi

if [ ! -f "src/requirements.txt" ]; then
    echo "❌ Arquivo src/requirements.txt não encontrado!"
    exit 1
fi

if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile não encontrado!"
    exit 1
fi

echo "✅ Todos os arquivos necessários estão presentes"

# Build da imagem de teste
echo "🏗️  Fazendo build da imagem de teste..."
docker build --platform linux/amd64 -t lambda-test:latest .

# Testar a imagem
echo "🧪 Testando a imagem..."
docker run --rm --platform linux/amd64 lambda-test:latest python -c "
import sys
print(f'Python version: {sys.version}')
import lambda_function
print('✅ lambda_function importado com sucesso')
import app
print('✅ app importado com sucesso')
print('✅ Imagem está funcionando corretamente!')
"

echo "🎉 Teste concluído com sucesso!"
echo "💡 A imagem está pronta para ser enviada ao ECR"

# Limpar imagem de teste
docker rmi lambda-test:latest
echo "🧹 Imagem de teste removida"