# Script para build e push da imagem Docker para ECR
# Este script deve ser executado antes do terraform apply

param(
    [string]$ProjectName = "lambda-container-api",
    [string]$Environment = "dev",
    [string]$AwsRegion = "us-east-1"
)

# Configurar ErrorActionPreference para parar em erros
$ErrorActionPreference = "Stop"

# Obter hash do commit Git (7 primeiros dígitos)
try {
    $gitDir = git rev-parse --git-dir 2>$null
    if ($gitDir) {
        $GitCommitHash = (git rev-parse --short=7 HEAD 2>$null)
        if (-not $GitCommitHash) { $GitCommitHash = "no-commit" }
    } else {
        $GitCommitHash = "no-git"
    }
}
catch {
    $GitCommitHash = "no-git"
}

# Tags da imagem
$EcrImageTagLatest = "latest"
$EcrImageTagCommit = $GitCommitHash

# Construir nomes
$EcrRepositoryName = "$ProjectName-$Environment"
$LambdaFunctionName = "$ProjectName-$Environment"

Write-Host "🚀 Iniciando build e push da imagem Docker..." -ForegroundColor Green
Write-Host "📋 Configurações:" -ForegroundColor Cyan
Write-Host "   - Projeto: $ProjectName" -ForegroundColor White
Write-Host "   - Ambiente: $Environment" -ForegroundColor White
Write-Host "   - Região: $AwsRegion" -ForegroundColor White
Write-Host "   - Repositório ECR: $EcrRepositoryName" -ForegroundColor White
Write-Host "   - Tag Latest: $EcrImageTagLatest" -ForegroundColor White
Write-Host "   - Tag Commit: $EcrImageTagCommit" -ForegroundColor White

try {
    # Obter Account ID
    $AccountId = (aws sts get-caller-identity --query Account --output text)
    $EcrUri = "$AccountId.dkr.ecr.$AwsRegion.amazonaws.com"
    $FullImageNameLatest = "$EcrUri/${EcrRepositoryName}:$EcrImageTagLatest"
    $FullImageNameCommit = "$EcrUri/${EcrRepositoryName}:$EcrImageTagCommit"

    Write-Host "📦 URIs das imagens:" -ForegroundColor Yellow
    Write-Host "   - Latest: $FullImageNameLatest" -ForegroundColor White
    Write-Host "   - Commit: $FullImageNameCommit" -ForegroundColor White

    # Verificar se o repositório ECR existe
    Write-Host "🔍 Verificando se o repositório ECR existe..." -ForegroundColor Cyan
    
    $repoExists = $false
    try {
        aws ecr describe-repositories --repository-names $EcrRepositoryName --region $AwsRegion | Out-Null
        $repoExists = $true
    }
    catch {
        $repoExists = $false
    }

    if (-not $repoExists) {
        Write-Host "❌ Repositório ECR não existe: $EcrRepositoryName" -ForegroundColor Red
        Write-Host "💡 Para criar o repositório, execute:" -ForegroundColor Yellow
        Write-Host "   aws ecr create-repository --repository-name $EcrRepositoryName --region $AwsRegion" -ForegroundColor White
        Write-Host "   ou use o Terraform para criar todos os recursos" -ForegroundColor White
        exit 1
    }
    else {
        Write-Host "✅ Repositório ECR encontrado: $EcrRepositoryName" -ForegroundColor Green
    }

    # Login no ECR
    Write-Host "🔐 Fazendo login no ECR..." -ForegroundColor Cyan
    $loginToken = aws ecr get-login-password --region $AwsRegion
    $loginToken | docker login --username AWS --password-stdin $EcrUri

    # Build da imagem Docker com plataforma específica para Lambda
    Write-Host "🏗️  Fazendo build da imagem Docker para AWS Lambda (linux/amd64)..." -ForegroundColor Cyan
    docker build --platform linux/amd64 -t "${EcrRepositoryName}:$EcrImageTagLatest" .

    # Aplicar tags para ECR
    Write-Host "🏷️  Aplicando tags para ECR..." -ForegroundColor Cyan
    docker tag "${EcrRepositoryName}:$EcrImageTagLatest" $FullImageNameLatest
    docker tag "${EcrRepositoryName}:$EcrImageTagLatest" $FullImageNameCommit

    # Verificar a imagem antes do push
    Write-Host "🔍 Verificando a imagem construída..." -ForegroundColor Cyan
    docker inspect "${EcrRepositoryName}:$EcrImageTagLatest" | Out-Null

    # Testar se a imagem pode ser executada (teste básico)
    Write-Host "🧪 Testando a imagem localmente..." -ForegroundColor Cyan
    $testResult = docker run --rm --platform linux/amd64 --entrypoint="" "${EcrRepositoryName}:$EcrImageTagLatest" python -c "
import lambda_function
import app
print('✅ Todos os módulos importados com sucesso')
print('✅ Imagem OK')
"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro: A imagem não passou no teste básico" -ForegroundColor Red
        exit 1
    }

    # Push das imagens para ECR
    Write-Host "📤 Fazendo push das imagens para ECR..." -ForegroundColor Cyan
    Write-Host "   - Enviando tag latest..." -ForegroundColor White
    docker push $FullImageNameLatest
    Write-Host "   - Enviando tag commit ($EcrImageTagCommit)..." -ForegroundColor White
    docker push $FullImageNameCommit

    Write-Host "✅ Build e push concluídos com sucesso!" -ForegroundColor Green
    Write-Host "🎯 Imagens disponíveis em:" -ForegroundColor Yellow
    Write-Host "   - Latest: $FullImageNameLatest" -ForegroundColor White
    Write-Host "   - Commit: $FullImageNameCommit" -ForegroundColor White

    # Verificar se a função Lambda existe e atualizar o código se necessário
    Write-Host "🔍 Verificando se a função Lambda existe..." -ForegroundColor Cyan
    
    $functionExists = $false
    try {
        aws lambda get-function --function-name $LambdaFunctionName --region $AwsRegion | Out-Null
        $functionExists = $true
    }
    catch {
        $functionExists = $false
    }

    if ($functionExists) {
        Write-Host "🔄 Atualizando código da função Lambda..." -ForegroundColor Yellow
        aws lambda update-function-code `
            --function-name $LambdaFunctionName `
            --image-uri $FullImageNameLatest `
            --region $AwsRegion
        Write-Host "✅ Código da função Lambda atualizado!" -ForegroundColor Green
    }
    else {
        Write-Host "ℹ️  Função Lambda não existe ainda - será criada pelo Terraform" -ForegroundColor Blue
    }

    Write-Host "🎉 Processo concluído com sucesso!" -ForegroundColor Green
}
catch {
    Write-Host "❌ Erro durante o processo: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}