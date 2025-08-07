# 🔧 Lambda Container Troubleshooting Guide

Este guia ajuda a resolver problemas comuns com AWS Lambda Container Images.

## ❌ Erro Atual

```
Error: creating Lambda Function (lambda-container-api-dev): operation error Lambda: CreateFunction, 
https response error StatusCode: 400, RequestID: 1390a68d-99e2-42de-ab0a-f4e38351d1c9, 
InvalidParameterValueException: The image manifest, config or layer media type for the source image 
148761658767.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api-dev:latest is not supported.
```

## 🔍 Possíveis Causas

### 1. **Arquitetura Incompatível**
- A imagem não foi construída para `linux/amd64`
- Construída em arquitetura ARM (Apple Silicon) sem especificar plataforma

### 2. **Imagem Base Incorreta**
- Não está usando a imagem base oficial do Lambda
- Imagem corrompida ou incompleta

### 3. **Problemas no Build Process**
- Docker buildx não configurado corretamente
- Cache corrompido do Docker
- Problemas na transferência para ECR

### 4. **Problemas no ECR**
- Imagem corrompida no repositório
- Manifest inválido
- Problemas de permissão

## 🛠️ Soluções

### Solução 1: Executar Script de Correção

**Linux/macOS:**
```bash
chmod +x scripts/fix-lambda-image.sh
./scripts/fix-lambda-image.sh
```

**Windows (PowerShell):**
```powershell
.\scripts\fix-lambda-image.ps1
```

### Solução 2: Reconstrução Manual

1. **Limpar cache local:**
```bash
docker system prune -f
docker rmi $(docker images -q) 2>/dev/null || true
```

2. **Rebuild com plataforma específica:**
```bash
docker buildx create --use --name lambda-builder
docker buildx build --platform linux/amd64 --load -t lambda-container-api-dev:latest .
```

3. **Verificar a imagem:**
```bash
docker run --rm --platform linux/amd64 lambda-container-api-dev:latest python -c "
import lambda_function
print('✅ Handler encontrado:', hasattr(lambda_function, 'lambda_handler'))
"
```

4. **Push para ECR:**
```bash
# Login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 148761658767.dkr.ecr.us-east-1.amazonaws.com

# Tag e push
docker tag lambda-container-api-dev:latest 148761658767.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api-dev:latest
docker push 148761658767.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api-dev:latest
```

### Solução 3: Recriar Repositório ECR

Se o repositório estiver corrompido:

```bash
# Backup (opcional)
aws ecr describe-images --repository-name lambda-container-api-dev --region us-east-1

# Deletar repositório
aws ecr delete-repository --repository-name lambda-container-api-dev --region us-east-1 --force

# Recriar via Terraform
terraform apply -target=aws_ecr_repository.main
```

### Solução 4: Verificar Dockerfile

Certifique-se de que o Dockerfile está correto:

```dockerfile
# ✅ Correto
FROM public.ecr.aws/lambda/python:3.11

# ❌ Incorreto
FROM python:3.11
FROM ubuntu:latest
```

## 🧪 Testes de Validação

### 1. Testar Imagem Localmente
```bash
# Testar handler
docker run --rm lambda-container-api-dev:latest python -c "
import lambda_function
event = {'httpMethod': 'GET', 'path': '/hello'}
context = type('Context', (), {'aws_request_id': 'test-123'})()
result = lambda_function.lambda_handler(event, context)
print('✅ Teste local OK:', result['statusCode'])
"
```

### 2. Testar no ECR
```bash
# Verificar manifest
aws ecr describe-images \
  --repository-name lambda-container-api-dev \
  --image-ids imageTag=latest \
  --region us-east-1
```

### 3. Testar Lambda (se existir)
```bash
# Invocar função
aws lambda invoke \
  --function-name lambda-container-api-dev \
  --payload '{"httpMethod":"GET","path":"/hello"}' \
  --region us-east-1 \
  response.json

cat response.json
```

## 📋 Checklist de Verificação

- [ ] Imagem construída com `--platform linux/amd64`
- [ ] Usando imagem base `public.ecr.aws/lambda/python:3.11`
- [ ] Handler `lambda_function.lambda_handler` existe
- [ ] Dependências instaladas corretamente
- [ ] Push para ECR bem-sucedido
- [ ] Manifest da imagem válido
- [ ] Permissões IAM corretas

## 🔄 Processo Recomendado

1. **Execute o script de correção** (`fix-lambda-image.sh` ou `.ps1`)
2. **Verifique os logs** para identificar problemas específicos
3. **Teste localmente** antes do push
4. **Valide no ECR** após o push
5. **Execute terraform apply** novamente

## 📞 Próximos Passos

Após executar as correções:

1. Execute `terraform apply` novamente
2. Teste os endpoints da API
3. Monitore os logs do CloudWatch
4. Configure alertas de monitoramento

## 🚨 Se Nada Funcionar

1. **Verifique as permissões IAM**
2. **Confirme a região AWS**
3. **Teste com uma imagem Lambda simples**
4. **Contate o suporte AWS** se necessário

---

**💡 Dica:** Sempre teste localmente antes de fazer deploy para evitar problemas no ECR/Lambda.