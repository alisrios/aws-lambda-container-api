# Changelog - GitHub OIDC Configuration

## 📅 Data: 2025-08-07

## 🎯 Objetivo
Migrar o GitHub Actions de chaves de acesso AWS (Access Keys) para OpenID Connect (OIDC), proporcionando maior segurança e eliminando a necessidade de armazenar credenciais de longo prazo.

## 🔧 Alterações Realizadas

### 1. Configuração OIDC no Terraform (`terraform/oidc.tf`)
- ✅ Criado arquivo completo para configuração OIDC
- ✅ GitHub OIDC Identity Provider configurado
- ✅ IAM Role para GitHub Actions com trust policy específico
- ✅ Políticas IAM granulares para ECR, Lambda, Terraform e recursos gerais
- ✅ Outputs para ARNs da role e provider OIDC

```hcl
# Principais recursos criados:
- aws_iam_openid_connect_provider.github
- aws_iam_role.github_actions
- aws_iam_role_policy.github_actions_ecr
- aws_iam_role_policy.github_actions_lambda
- aws_iam_role_policy.github_actions_terraform
- aws_iam_role_policy.github_actions_general
```

### 2. Variáveis Terraform (`terraform/variables.tf`)
- ✅ Adicionada variável `github_repository` para configurar repositório
- ✅ Adicionada variável `terraform_state_bucket` para bucket S3

### 3. Providers Terraform (`terraform/versions.tf`)
- ✅ Adicionado provider TLS (~> 4.0) para obter thumbprint do GitHub
- ✅ Mantida compatibilidade com provider AWS (~> 6.0)

### 4. GitHub Actions Workflow (`.github/workflows/ci-cd.yml`)
- ✅ Configurado para usar OIDC em vez de chaves de acesso
- ✅ Permissões globais configuradas para OIDC
- ✅ Uso de `vars.AWS_ROLE_TO_ASSUME` em vez de secrets
- ✅ Role session names únicos para cada execução
- ✅ Mantida compatibilidade com todos os jobs existentes

### 5. Script de Configuração (`scripts/setup-github-oidc.sh`)
- ✅ Script interativo para configuração automática
- ✅ Validação de variáveis necessárias
- ✅ Criação/atualização de terraform.tfvars
- ✅ Execução automatizada do terraform plan/apply
- ✅ Instruções detalhadas para configuração no GitHub

### 6. Documentação Completa
- ✅ `docs/GITHUB_OIDC_MIGRATION.md` - Guia completo de migração
- ✅ README.md atualizado com informações sobre OIDC
- ✅ Troubleshooting e validação incluídos

## 🔐 Benefícios Implementados

### Segurança
- 🔒 **Sem credenciais permanentes**: Elimina chaves de acesso armazenadas
- 🔒 **Tokens temporários**: Credenciais com tempo de vida limitado (1 hora)
- 🔒 **Princípio do menor privilégio**: Permissões específicas por repositório
- 🔒 **Auditoria melhorada**: Rastreamento detalhado via CloudTrail

### Operacional
- ⚡ **Rotação automática**: Não requer rotação manual de chaves
- ⚡ **Gestão centralizada**: Controle via IAM roles
- ⚡ **Compliance**: Atende requisitos de segurança corporativa
- ⚡ **Redução de riscos**: Elimina vazamento de credenciais

## 🏗️ Arquitetura OIDC

```
GitHub Actions → GitHub OIDC Provider → AWS STS → IAM Role → AWS Services
     ↓                    ↓                ↓         ↓           ↓
  JWT Token         Token Validation   Assume Role  Temp Creds  ECR/Lambda
```

## 📋 Como Usar

### Passo 1: Configurar Infraestrutura
```bash
cd terraform
../scripts/setup-github-oidc.sh
```

### Passo 2: Configurar GitHub Repository
Adicionar Repository Variables:
```
AWS_ROLE_TO_ASSUME = arn:aws:iam::ACCOUNT_ID:role/lambda-container-api-dev-github-actions-role
TERRAFORM_STATE_BUCKET = your-terraform-state-bucket-name
```

### Passo 3: Testar Pipeline
```bash
git push origin main
```

## 🔍 Validação

### Checklist de Verificação
- [ ] OIDC Provider criado no AWS IAM
- [ ] IAM Role configurada com trust policy correto
- [ ] Políticas de permissão aplicadas à role
- [ ] Repository Variables configuradas no GitHub
- [ ] Pipeline executa sem erros de autenticação
- [ ] Recursos AWS são acessados corretamente

### Comandos de Teste
```bash
# Verificar outputs do Terraform
terraform output github_actions_role_arn
terraform output github_oidc_provider_arn

# Testar pipeline
git push origin main

# Verificar logs
aws logs tail /aws/lambda/lambda-container-api-dev --follow
```

## 🔧 Configuração Detalhada

### Trust Policy da IAM Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": [
            "repo:owner/repo:ref:refs/heads/main",
            "repo:owner/repo:ref:refs/heads/develop",
            "repo:owner/repo:pull_request"
          ]
        }
      }
    }
  ]
}
```

### Permissões IAM Configuradas
- **ECR**: Push/pull de imagens Docker
- **Lambda**: Update de código e configuração
- **Terraform**: Acesso ao estado S3 e lock DynamoDB
- **CloudWatch**: Logs e métricas
- **API Gateway**: Configuração e deployment
- **IAM**: Gestão de roles e políticas (limitado)

## 🚨 Troubleshooting

### Erro: "No OpenIDConnect provider found"
```bash
# Verificar se o provider existe
aws iam list-open-id-connect-providers

# Recriar se necessário
terraform apply -target=aws_iam_openid_connect_provider.github
```

### Erro: "Not authorized to perform sts:AssumeRoleWithWebIdentity"
- Verificar nome do repositório na trust policy
- Confirmar branch nas condições
- Validar variável `AWS_ROLE_TO_ASSUME`

### Erro: "Access Denied" em operações AWS
```bash
# Verificar políticas da role
aws iam list-attached-role-policies --role-name lambda-container-api-dev-github-actions-role
aws iam list-role-policies --role-name lambda-container-api-dev-github-actions-role
```

## 📊 Comparação: Antes vs Depois

| Aspecto | Access Keys | OIDC |
|---------|-------------|------|
| **Segurança** | ❌ Credenciais permanentes | ✅ Tokens temporários |
| **Rotação** | ❌ Manual (90 dias) | ✅ Automática (1 hora) |
| **Auditoria** | ⚠️ Limitada | ✅ Detalhada |
| **Compliance** | ❌ Não recomendado | ✅ Best practice |
| **Gestão** | ❌ Complexa | ✅ Centralizada |
| **Risco** | ❌ Alto (vazamento) | ✅ Baixo |

## 🔄 Rollback (Se Necessário)

### Reverter para Access Keys
1. Reconfigurar secrets no GitHub
2. Reverter workflow para usar secrets
3. Remover recursos OIDC (opcional)

## 📚 Arquivos Modificados/Criados

### Novos Arquivos:
- `terraform/oidc.tf` - Configuração OIDC completa
- `scripts/setup-github-oidc.sh` - Script de configuração
- `docs/GITHUB_OIDC_MIGRATION.md` - Guia de migração
- `CHANGELOG_GITHUB_OIDC.md` - Este arquivo

### Arquivos Modificados:
- `.github/workflows/ci-cd.yml` - Workflow atualizado para OIDC
- `terraform/variables.tf` - Novas variáveis OIDC
- `terraform/versions.tf` - Provider TLS adicionado
- `terraform/outputs.tf` - Corrigido duplicatas
- `README.md` - Seção CI/CD atualizada

## 🎉 Resultado Final

O GitHub Actions agora utiliza OpenID Connect para autenticação com AWS, proporcionando:

- ✅ **Segurança aprimorada** sem credenciais de longo prazo
- ✅ **Automação completa** sem intervenção manual
- ✅ **Compliance** com melhores práticas de segurança
- ✅ **Auditoria detalhada** de todas as operações
- ✅ **Gestão centralizada** via IAM roles

## 🔄 Próximos Passos

1. Testar o pipeline em ambiente de desenvolvimento
2. Validar funcionamento em diferentes branches
3. Monitorar logs de auditoria no CloudTrail
4. Considerar implementação em outros projetos
5. Documentar processo para equipe de desenvolvimento

## 📞 Suporte

Em caso de problemas:
1. Consultar `docs/GITHUB_OIDC_MIGRATION.md`
2. Verificar logs do GitHub Actions
3. Validar configuração IAM no AWS Console
4. Revisar trust policy da role
5. Confirmar variáveis do repositório GitHub
