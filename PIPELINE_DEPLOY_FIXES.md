# Correções no Job Deploy Infrastructure

## Problemas Identificados

O job "Deploy Infrastructure" estava falhando devido a:

1. **Backend Configuration**: Tentativa de configurar backend via parâmetros quando já existe `backend.tf`
2. **Variáveis Terraform**: Passagem incorreta de variáveis via `-var`
3. **Falta de Validação**: Não verificava se arquivos necessários existem
4. **Outputs Frágeis**: Não tratava casos onde outputs não existem
5. **Debug Insuficiente**: Pouca informação para troubleshooting

## Correções Implementadas

### 1. ✅ Verificação de Arquivos Terraform
```yaml
- name: Check Terraform files
  run: |
    # Verifica se main.tf, backend.tf existem
    # Cria variables.tf se não existir
    # Lista estrutura do projeto
```

### 2. ✅ Backend Configuration Simplificada
```yaml
- name: Terraform Init
  run: |
    # Remove configuração manual do backend
    # Usa configuração do backend.tf
    terraform init
```

### 3. ✅ Variáveis via terraform.tfvars
```yaml
- name: Terraform Plan
  run: |
    # Cria arquivo terraform.tfvars com variáveis
    cat > terraform.tfvars << EOF
    project_name = "lambda-container-api"
    environment = "dev"
    ecr_image_tag = "${{ needs.build-and-push.outputs.image-tag }}"
    EOF
    
    terraform plan -out=tfplan
```

### 4. ✅ Debug Information
```yaml
- name: Debug Information
  run: |
    # Mostra informações do ambiente
    # Lista arquivos Terraform
    # Exibe variáveis importantes
```

### 5. ✅ Outputs Robustos
```yaml
- name: Get Terraform Outputs
  run: |
    # Verifica se outputs existem antes de obtê-los
    # Trata casos onde outputs não estão disponíveis
    # Fornece fallbacks apropriados
```

### 6. ✅ Tratamento de Erros Melhorado
```yaml
- name: Terraform Apply
  run: |
    # Melhor logging de sucesso/erro
    # Verificação do estado em caso de falha
    # Exit codes apropriados
```

## Variáveis Necessárias no GitHub

### Repository Variables (Settings > Secrets and variables > Actions > Variables)
```
AWS_ROLE_TO_ASSUME = arn:aws:iam::ACCOUNT_ID:role/lambda-container-api-dev-github-actions-role
```

### Secrets (se não usar OIDC)
```
AWS_ACCESS_KEY_ID = your-access-key
AWS_SECRET_ACCESS_KEY = your-secret-key
```

## Arquivos Terraform Necessários

### 1. `terraform/main.tf`
- Deve conter recursos AWS (Lambda, API Gateway, ECR, etc.)
- Deve usar as variáveis definidas em `variables.tf`

### 2. `terraform/backend.tf`
- Configuração do backend S3
- Deve estar configurado corretamente

### 3. `terraform/variables.tf` (criado automaticamente se não existir)
```hcl
variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "lambda-container-api"
}

variable "environment" {
  description = "Ambiente"
  type        = string
  default     = "dev"
}

variable "ecr_image_tag" {
  description = "Tag da imagem ECR"
  type        = string
  default     = "latest"
}
```

### 4. `terraform/outputs.tf`
```hcl
output "api_gateway_url" {
  description = "URL do API Gateway"
  value       = aws_api_gateway_deployment.main.invoke_url
}

output "lambda_function_name" {
  description = "Nome da função Lambda"
  value       = aws_lambda_function.main.function_name
}
```

## Fluxo Corrigido

1. **Check Terraform files** → Verifica arquivos necessários
2. **Debug Information** → Mostra informações do ambiente
3. **Check Backend Configuration** → Valida backend.tf
4. **Terraform Init** → Inicializa com backend configurado
5. **Terraform Validate** → Valida sintaxe
6. **Terraform Plan** → Cria plano com terraform.tfvars
7. **Terraform Apply** → Aplica mudanças
8. **Get Terraform Outputs** → Obtém outputs de forma robusta

## Próximos Passos

1. ✅ Verificar se `terraform/main.tf` existe e está correto
2. ✅ Verificar se `terraform/backend.tf` tem configuração válida
3. ✅ Configurar variáveis no GitHub (AWS_ROLE_TO_ASSUME)
4. ✅ Testar pipeline completo
5. ✅ Monitorar logs para identificar outros problemas

## Troubleshooting

### Se ainda houver erros:

1. **Verificar logs do job Deploy Infrastructure**
2. **Confirmar que backend S3 foi criado** (`./scripts/setup-terraform-backend.sh`)
3. **Validar permissões AWS** da role OIDC
4. **Verificar se imagem ECR existe** (job build-and-push deve ter sucesso)
5. **Confirmar estrutura dos arquivos Terraform**

O pipeline agora deve funcionar corretamente com melhor debugging e tratamento de erros!