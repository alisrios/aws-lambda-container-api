# Guia de Configuração do GitHub Actions

Este documento explica como configurar os secrets e permissões necessários para o pipeline de CI/CD.

## Secrets Obrigatórios do GitHub

Os seguintes secrets devem ser configurados nas configurações do seu repositório GitHub:

### 1. AWS_ROLE_TO_ASSUME
- **Descrição**: ARN da role IAM que o GitHub Actions irá assumir usando OIDC
- **Formato**: `arn:aws:iam::ACCOUNT-ID:role/GitHubActionsRole`
- **Configuração**: Criar uma role IAM com política de confiança OIDC para GitHub Actions

### 2. TERRAFORM_STATE_BUCKET
- **Descrição**: Nome do bucket S3 para armazenar o estado do Terraform
- **Formato**: `nome-do-seu-bucket-terraform-state`
- **Configuração**: Criar um bucket S3 com versionamento habilitado

## Configuração da Role IAM AWS

### 1. Criar Role IAM para GitHub Actions

Criar uma role IAM com a seguinte política de confiança:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT-ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:SEU-USUARIO-GITHUB/NOME-DO-SEU-REPO:*"
        }
      }
    }
  ]
}
```

### 2. Anexar Políticas Necessárias

A role precisa das seguintes permissões:

- `AmazonEC2ContainerRegistryFullAccess` (para operações ECR)
- `AWSLambdaFullAccess` (para gerenciamento de funções Lambda)
- `AmazonAPIGatewayAdministrator` (para gerenciamento do API Gateway)
- `IAMFullAccess` (para criar roles de execução Lambda)
- `AmazonS3FullAccess` (para backend de estado do Terraform)
- `CloudWatchLogsFullAccess` (para logging do Lambda)

Ou criar uma política customizada com as permissões mínimas necessárias.

### 3. Criar Provedor de Identidade OIDC

Se ainda não foi criado, adicione o GitHub como provedor de identidade OIDC:

1. Vá para IAM → Provedores de identidade → Adicionar provedor
2. Tipo de provedor: OpenID Connect
3. URL do provedor: `https://token.actions.githubusercontent.com`
4. Audiência: `sts.amazonaws.com`

## Configuração do Backend S3

### 1. Criar Bucket S3

```bash
aws s3 mb s3://nome-do-seu-bucket-terraform-state --region us-east-1
```

### 2. Habilitar Versionamento

```bash
aws s3api put-bucket-versioning \
  --bucket nome-do-seu-bucket-terraform-state \
  --versioning-configuration Status=Enabled
```

### 3. Habilitar Criptografia Server-Side

```bash
aws s3api put-bucket-encryption \
  --bucket nome-do-seu-bucket-terraform-state \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'
```

## Configuração do Repositório

### 1. Adicionar Secrets

Vá para seu repositório GitHub → Settings → Secrets and variables → Actions

Adicione os seguintes secrets do repositório:
- `AWS_ROLE_TO_ASSUME`: O ARN da sua role IAM
- `TERRAFORM_STATE_BUCKET`: O nome do seu bucket S3

### 2. Habilitar Actions

Certifique-se de que o GitHub Actions está habilitado nas configurações do seu repositório.

### 3. Proteção de Branch (Opcional)

Considere configurar regras de proteção de branch para a branch `main` que exijam:
- Verificações de status aprovadas
- Revisões de pull request
- Branches atualizadas

## Testando a Configuração

1. Faça push do código para uma branch de feature
2. Crie um pull request para `main` ou `develop`
3. Verifique se o workflow executa e mostra o plano do Terraform nos comentários do PR
4. Faça merge do PR para disparar o deployment
5. Verifique o resumo do deployment na aba Actions

## Solução de Problemas

### Problemas Comuns

1. **Política de Confiança OIDC**: Certifique-se de que a política de confiança corresponde exatamente ao seu repositório
2. **Permissões**: Verifique se a role IAM tem todas as permissões necessárias
3. **Backend S3**: Certifique-se de que o bucket existe e está acessível
4. **Secrets**: Verifique novamente se todos os secrets estão configurados corretamente

### Passos de Debug

1. Verifique os logs do Actions para mensagens de erro detalhadas
2. Verifique se as credenciais AWS estão sendo assumidas corretamente
3. Teste os comandos Terraform localmente com a mesma configuração
4. Certifique-se de que o repositório ECR existe ou pode ser criado

## Melhores Práticas de Segurança

1. Use políticas IAM de menor privilégio
2. Habilite CloudTrail para logging de auditoria
3. Rotacione e revise acessos regularmente
4. Use regras de proteção de branch
5. Monitore tentativas de autenticação falhadas
6. Mantenha o bucket de estado do Terraform privado e criptografado