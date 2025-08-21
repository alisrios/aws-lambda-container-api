# Correção do Erro "unsupported checkable object kind var"

## 🚨 Problema Identificado

```
Error refreshing state: unsupported checkable object kind "var"
```

Este erro geralmente ocorre devido a:
1. **Versão incompatível do Terraform**
2. **Sintaxe inválida nos arquivos .tf**
3. **Parâmetros inválidos no backend.tf**
4. **Cache corrompido do Terraform**

## 🔧 Correções Implementadas

### 1. ✅ Atualização da Versão do Terraform
```yaml
env:
  TERRAFORM_VERSION: 1.6.0  # Atualizado de 1.5.0
```

### 2. ✅ Limpeza do Cache
```bash
# Remove cache corrompido antes da inicialização
rm -rf .terraform .terraform.lock.hcl
```

### 3. ✅ Correção do backend.tf
```bash
# Remove parâmetro inválido 'use_lockfile'
# Cria backend.tf limpo se necessário
```

### 4. ✅ Múltiplas Estratégias de Inicialização
```bash
# Tentativa 1: terraform init -reconfigure
# Tentativa 2: terraform init -upgrade  
# Tentativa 3: terraform init (básico)
```

### 5. ✅ Verificação de Sintaxe
```bash
# Formata arquivos .tf automaticamente
# Verifica referências problemáticas
# Valida sintaxe antes da inicialização
```

### 6. ✅ Debug Melhorado
```bash
# Mostra versão do Terraform
# Lista providers
# Exibe conteúdo dos arquivos problemáticos
```

## 📋 Arquivo backend.tf Corrigido

O pipeline agora cria automaticamente um `backend.tf` limpo:

```hcl
# Backend configuration for Terraform state
# This stores the Terraform state in S3 with versioning for state protection

terraform {
  backend "s3" {
    bucket  = "bucket-state-locking"
    key     = "lambda-container-api/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}
```

**Removido**: `use_lockfile = true` (parâmetro inválido)

## 🔍 Fluxo de Correção

1. **Check and Fix Terraform Configuration**
   - Verifica sintaxe de todos os arquivos .tf
   - Formata arquivos automaticamente
   - Corrige backend.tf se necessário
   - Remove referências problemáticas

2. **Terraform Init com Múltiplas Tentativas**
   - Limpa cache corrompido
   - Tenta `init -reconfigure`
   - Fallback para `init -upgrade`
   - Fallback para `init` básico

3. **Terraform Validate Melhorado**
   - Validação com debug detalhado
   - Verificação de providers
   - Análise de arquivos de variáveis

## 🚀 Próximos Passos

### Se o erro persistir:

1. **Verificar arquivo terraform/main.tf**
   ```bash
   # Verificar se há sintaxe inválida
   cd terraform
   terraform fmt -check -diff
   ```

2. **Verificar arquivo terraform/variables.tf**
   ```bash
   # Procurar por definições problemáticas
   grep -n "checkable\|validation" variables.tf
   ```

3. **Verificar arquivo terraform/versions.tf**
   ```bash
   # Confirmar versões dos providers
   cat versions.tf
   ```

4. **Executar localmente para debug**
   ```bash
   cd terraform
   terraform init -reconfigure
   terraform validate
   ```

## 🔧 Comandos de Troubleshooting

### Limpar completamente o Terraform:
```bash
cd terraform
rm -rf .terraform .terraform.lock.hcl
terraform init -reconfigure
```

### Verificar sintaxe:
```bash
terraform fmt -check -diff
terraform validate
```

### Debug detalhado:
```bash
TF_LOG=DEBUG terraform init
```

## ✅ Resultado Esperado

Com essas correções, o pipeline deve:
1. ✅ Limpar cache corrompido automaticamente
2. ✅ Corrigir backend.tf se necessário
3. ✅ Inicializar Terraform com sucesso
4. ✅ Validar configuração corretamente
5. ✅ Prosseguir com plan/apply normalmente

O erro "unsupported checkable object kind var" deve ser resolvido!