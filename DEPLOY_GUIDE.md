# Guia de Deploy - Resolvendo Erro da Imagem ECR

## Problema

Você está enfrentando este erro ao executar `terraform apply`:

```
Error: creating Lambda Function (lambda-container-api-dev): Source image 148761658767.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api-dev:latest does not exist.
```

## Causa

O Terraform está tentando criar a função Lambda antes da imagem Docker ser construída e enviada para o ECR.

## Solução Rápida

Execute estes comandos **na ordem correta**:

### 1. Primeiro, construa e envie a imagem Docker:

**No Windows (PowerShell):**
```powershell
# Navegar para o diretório do projeto
cd d:\Alisson\AWS\Lambda

# Executar o script de build
.\scripts\build-and-push.ps1
```

**No Linux/macOS/WSL:**
```bash
# Navegar para o diretório do projeto
cd /mnt/d/Alisson/AWS/Lambda

# Tornar o script executável
chmod +x scripts/build-and-push.sh

# Executar o script
./scripts/build-and-push.sh
```

### 2. Depois, execute o Terraform:

```bash
cd terraform
terraform apply
```

## Solução Manual (se os scripts não funcionarem)

### 1. Criar o repositório ECR manualmente:

```bash
aws ecr create-repository \
    --repository-name lambda-container-api-dev \
    --region us-east-1 \
    --image-scanning-configuration scanOnPush=true
```

### 2. Fazer login no ECR:

```bash
# Obter o Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Login no ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

### 3. Construir e enviar a imagem:

```bash
# Build da imagem
docker build -t lambda-container-api-dev:latest .

# Tag para ECR
docker tag lambda-container-api-dev:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api-dev:latest

# Push para ECR
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api-dev:latest
```

### 4. Executar o Terraform:

```bash
cd terraform
terraform apply
```

## Verificação

Para verificar se a imagem foi enviada corretamente:

```bash
aws ecr list-images --repository-name lambda-container-api-dev --region us-east-1
```

## Automatização Futura

Para evitar este problema no futuro, você pode:

1. **Usar o GitHub Actions**: O workflow já está configurado para fazer o build automaticamente
2. **Usar os scripts fornecidos**: Sempre execute `build-and-push.sh` antes do `terraform apply`
3. **Integrar no seu processo**: Adicione o build da imagem como um passo anterior ao Terraform

## Troubleshooting

### Se o Docker não estiver rodando:
```bash
# No Windows
Start-Service docker

# No Linux
sudo systemctl start docker
```

### Se houver problemas de permissão AWS:
```bash
# Verificar credenciais
aws sts get-caller-identity

# Verificar permissões ECR
aws ecr describe-repositories --region us-east-1
```

### Se a imagem for muito grande:
- Verifique o Dockerfile para otimizações
- Use multi-stage builds (já implementado)
- Remova dependências desnecessárias

## Próximos Passos

Após resolver este problema:

1. ✅ A função Lambda será criada com sucesso
2. ✅ O API Gateway será configurado
3. ✅ Você poderá testar os endpoints
4. ✅ O monitoramento estará ativo

## Contato

Se ainda houver problemas, verifique:
- Logs do Docker
- Logs do AWS CLI
- Permissões IAM
- Conectividade de rede