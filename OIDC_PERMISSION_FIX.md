# Correção do Erro de Permissões OIDC

## 🚨 Problema Identificado

```
Error: updating IAM Role (lambda-container-api-dev-github-actions-role) assume role policy: 
operation error IAM: UpdateAssumeRolePolicy, https response error StatusCode: 403, 
RequestID: 507a9377-fdb4-4cdf-9915-cb64e9edfada, api error AccessDenied: 
User: arn:aws:sts::148761658767:assumed-role/lambda-container-api-dev-github-actions-role/GitHubActions-Deploy-17136436868 
is not authorized to perform: iam:UpdateAssumeRolePolicy on resource: role lambda-container-api-dev-github-actions-role 
because no identity-based policy allows the iam:UpdateAssumeRolePolicy action
```

## 🔍 Causa do Problema

**Problema de Permissões Circulares**: A role do GitHub Actions está tentando modificar sua própria política de assume role, mas não tem permissão para isso. É um problema de "chicken and egg" - a role precisa de permissão para modificar a si mesma, mas não pode dar essa permissão a si mesma.

## 🔧 Soluções Implementadas

### 1. ✅ Detecção Automática de Contexto
```bash
# Detecta se está executando via GitHub Actions
CURRENT_ROLE=$(aws sts get-caller-identity --query Arn --output text)
if echo "$CURRENT_ROLE" | grep -q "github-actions-role"; then
  echo "skip_github_oidc_modification = true" >> terraform.tfvars
fi
```

### 2. ✅ Apply com Targets Específicos
```bash
# Aplica apenas recursos principais, evitando OIDC
terraform apply -auto-approve \
  -target="aws_lambda_function.main" \
  -target="aws_apigatewayv2_api.main" \
  -target="aws_apigatewayv2_integration.lambda" \
  # ... outros recursos principais
```

### 3. ✅ Variáveis de Controle
```hcl
# terraform.tfvars
skip_oidc_resources = true
skip_github_oidc_modification = true
```

### 4. ✅ Fallback Strategy
```bash
# Tentativa 1: Apply com targets específicos
# Tentativa 2: Apply do plano completo
# Tentativa 3: Debug e identificação do problema
```

## 📋 Recursos Aplicados vs Ignorados

### ✅ Recursos Aplicados (Principais)
- `aws_lambda_function.main` - Função Lambda
- `aws_apigatewayv2_api.main` - API Gateway
- `aws_apigatewayv2_integration.lambda` - Integração Lambda
- `aws_apigatewayv2_stage.default` - Stage da API
- `aws_apigatewayv2_route.*` - Rotas da API
- `aws_cloudwatch_log_group.*` - Grupos de logs
- `aws_iam_role.lambda` - Role da Lambda
- `aws_iam_role_policy.lambda_*` - Políticas da Lambda
- `aws_lambda_permission.api_gateway` - Permissões

### ⚠️ Recursos Ignorados (OIDC)
- `aws_iam_role.github_actions` - Role GitHub Actions
- `aws_iam_openid_connect_provider.github` - Provider OIDC
- `aws_iam_role_policy.github_actions_*` - Políticas GitHub Actions

## 🎯 Estratégia de Deploy

### 1. **Setup Inicial (Manual)**
```bash
# Executar uma vez manualmente para criar recursos OIDC
cd terraform
terraform apply -target="aws_iam_openid_connect_provider.github"
terraform apply -target="aws_iam_role.github_actions"
```

### 2. **Deploy Automatizado (CI/CD)**
```bash
# Pipeline aplica apenas recursos da aplicação
# Ignora recursos OIDC para evitar conflitos de permissão
```

### 3. **Atualizações OIDC (Manual)**
```bash
# Modificações na role OIDC devem ser feitas manualmente
# Ou com credenciais administrativas
```

## 🔧 Comandos de Troubleshooting

### Verificar Role Atual
```bash
aws sts get-caller-identity
```

### Listar Recursos no Estado
```bash
terraform state list | grep -E "(github|oidc)"
```

### Aplicar Recursos Específicos
```bash
terraform apply -target="aws_lambda_function.main"
```

### Remover Recurso Problemático do Estado (Temporário)
```bash
terraform state rm aws_iam_role.github_actions
```

## 🚀 Solução Recomendada

### Para Projetos Novos:
1. **Setup inicial manual** dos recursos OIDC
2. **Pipeline automatizado** para recursos da aplicação
3. **Separação clara** entre infraestrutura OIDC e aplicação

### Para Este Projeto:
1. ✅ **Pipeline ajustado** para aplicar apenas recursos principais
2. ✅ **Detecção automática** do contexto de execução
3. ✅ **Fallback strategies** para diferentes cenários
4. ✅ **Debug melhorado** para identificar problemas

## ✅ Resultado Esperado

Com essas correções:
1. ✅ Pipeline não tenta modificar role OIDC
2. ✅ Recursos principais (Lambda, API Gateway) são aplicados
3. ✅ API funciona corretamente
4. ✅ Evita conflitos de permissões circulares
5. ✅ Mantém funcionalidade completa da aplicação

O erro de permissões OIDC deve ser resolvido, permitindo que o deploy continue normalmente!