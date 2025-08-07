# Scripts de Deploy

Este diretório contém scripts para automatizar o build e push da imagem Docker para o ECR antes do deploy com Terraform.

## Problema Resolvido

O erro que você está enfrentando:
```
Error: creating Lambda Function (lambda-container-api-dev): Source image 148761658767.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api-dev:latest does not exist.
```

Acontece porque o Terraform está tentando criar a função Lambda antes da imagem Docker ser construída e enviada para o ECR.

## Solução

Execute um dos scripts abaixo **antes** de rodar `terraform apply`:

### Para Linux/macOS/WSL:
```bash
# Tornar o script executável
chmod +x scripts/build-and-push.sh

# Executar o script
./scripts/build-and-push.sh
```

### Para Windows PowerShell:
```powershell
# Executar o script
.\scripts\build-and-push.ps1
```

### Com parâmetros customizados:
```bash
# Linux/macOS/WSL
PROJECT_NAME="meu-projeto" ENVIRONMENT="prod" AWS_REGION="us-west-2" ./build-and-push.sh
```

```powershell
# Windows PowerShell
.\scripts\build-and-push.ps1 -ProjectName "meu-projeto" -Environment "prod" -AwsRegion "us-west-2"
```

## Tags da Imagem

O script automaticamente cria duas tags para cada imagem:

1. **`latest`** - Tag padrão que sempre aponta para a versão mais recente
2. **`<commit-hash>`** - Tag com os 7 primeiros dígitos do hash do commit Git atual

### Exemplo de tags criadas:
- `148761658767.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api-dev:latest`
- `148761658767.dkr.ecr.us-east-1.amazonaws.com/lambda-container-api-dev:a1b2c3d`

Isso permite rastreabilidade completa das versões e facilita rollbacks se necessário.

## Ordem de Execução Recomendada

1. **Primeiro**: Execute o script de build e push
   ```bash
   ./scripts/build-and-push.sh
   ```

2. **Depois**: Execute o Terraform
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

## O que o Script Faz

1. ✅ Verifica se o repositório ECR existe (falha se não existir)
2. 🔐 Faz login no ECR
3. 🏗️ Constrói a imagem Docker
4. 🏷️ Aplica as tags necessárias
5. 📤 Faz push da imagem para o ECR
6. 🔄 Atualiza a função Lambda se ela já existir

## Scripts Disponíveis

- `build-and-push.sh` - Build e push da imagem (requer repositório existente)
- `create-ecr-repository.sh` - Cria apenas o repositório ECR
- `terraform-deploy.sh` - Deploy completo com Terraform

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `PROJECT_NAME` | `lambda-container-api` | Nome do projeto |
| `ENVIRONMENT` | `dev` | Ambiente (dev, staging, prod) |
| `AWS_REGION` | `us-east-1` | Região AWS |
| `ECR_IMAGE_TAG` | `latest` | Tag da imagem Docker |

## Pré-requisitos

- Docker instalado e rodando
- AWS CLI configurado com credenciais válidas
- Permissões para ECR e Lambda na conta AWS

## Ordem de Execução Recomendada

### Opção 1: Usar Terraform para criar tudo (Recomendado)
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Opção 2: Criar repositório primeiro, depois build
```bash
# 1. Criar repositório ECR
./scripts/create-ecr-repository.sh

# 2. Build e push da imagem
./build-and-push.sh

# 3. Deploy com Terraform (importará o repositório automaticamente)
./scripts/terraform-deploy.sh
```

### Opção 3: Script automatizado completo
```bash
./scripts/terraform-deploy.sh
```

## Integração com CI/CD

Estes scripts podem ser integrados no seu pipeline de CI/CD. Veja o arquivo `.github/workflows/ci-cd.yml` para um exemplo de como usar no GitHub Actions.