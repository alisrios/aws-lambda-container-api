# ECR Force Delete Configuration

## 📋 Visão Geral

Este documento explica como a configuração `force_delete = true` no recurso ECR permite a exclusão automática do repositório mesmo quando contém imagens Docker.

## 🔧 Configuração Implementada

No arquivo `terraform/main.tf`, o recurso ECR foi configurado com:

```hcl
resource "aws_ecr_repository" "main" {
  name                 = local.ecr_repository_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true  # Permite exclusão mesmo com imagens

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = local.common_tags
}
```

## ⚙️ Como Funciona

### Comportamento Padrão (sem force_delete)
- Terraform falha ao tentar excluir repositório ECR com imagens
- Erro: `RepositoryNotEmptyException`
- Necessário excluir manualmente todas as imagens antes do destroy

### Comportamento com force_delete = true
- Terraform automaticamente exclui todas as imagens do repositório
- Repositório é excluído mesmo contendo imagens
- Processo de destroy é executado sem interrupções

## 🚀 Benefícios

1. **Automação Completa**: Não requer intervenção manual para limpeza
2. **CI/CD Friendly**: Pipelines podem executar destroy sem falhas
3. **Desenvolvimento Ágil**: Facilita criação/destruição de ambientes de teste
4. **Prevenção de Custos**: Evita repositórios órfãos que geram custos

## ⚠️ Considerações de Segurança

### Ambientes de Desenvolvimento
✅ **Recomendado**: Use `force_delete = true`
- Facilita limpeza de recursos
- Reduz custos de desenvolvimento
- Acelera ciclos de desenvolvimento

### Ambientes de Produção
⚠️ **Cuidado**: Considere `force_delete = false`
- Previne exclusão acidental de imagens importantes
- Requer processo manual de limpeza
- Maior controle sobre exclusão de recursos

## 🛠️ Scripts de Apoio

### Script Automatizado
O script `scripts/force-destroy.sh` fornece:
- Verificação de imagens antes da exclusão
- Confirmação interativa do usuário
- Limpeza adicional se necessário
- Logs detalhados do processo

### Uso do Script
```bash
cd terraform
../scripts/force-destroy.sh
```

## 🔍 Verificação Manual

### Listar Imagens no Repositório
```bash
aws ecr list-images --repository-name lambda-container-api-dev
```

### Verificar se Repositório Existe
```bash
aws ecr describe-repositories --repository-names lambda-container-api-dev
```

### Exclusão Manual (se necessário)
```bash
aws ecr delete-repository --repository-name lambda-container-api-dev --force
```

## 📊 Comparação de Abordagens

| Aspecto | force_delete = false | force_delete = true |
|---------|---------------------|-------------------|
| **Segurança** | ✅ Maior controle | ⚠️ Exclusão automática |
| **Automação** | ❌ Requer intervenção | ✅ Totalmente automatizado |
| **CI/CD** | ❌ Pode falhar | ✅ Execução suave |
| **Desenvolvimento** | ❌ Processo manual | ✅ Rápido e eficiente |
| **Produção** | ✅ Proteção extra | ⚠️ Risco de exclusão |

## 🎯 Recomendações

### Para Este Projeto (Teste Técnico)
- ✅ `force_delete = true` é apropriado
- Facilita demonstração e limpeza
- Reduz complexidade operacional

### Para Projetos Reais
- **Dev/Test**: Use `force_delete = true`
- **Staging**: Considere `force_delete = true` com aprovação
- **Production**: Avalie `force_delete = false` para maior segurança

## 🔄 Alternativas

### Conditional Force Delete
```hcl
resource "aws_ecr_repository" "main" {
  name         = local.ecr_repository_name
  force_delete = var.environment != "production"
  # ...
}
```

### Lifecycle Rules
```hcl
resource "aws_ecr_repository" "main" {
  # ...
  
  lifecycle {
    prevent_destroy = var.environment == "production"
  }
}
```

## 📚 Referências

- [Terraform AWS ECR Repository](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecr_repository)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [ECR Repository Policies](https://docs.aws.amazon.com/ecr/latest/userguide/repository-policies.html)
