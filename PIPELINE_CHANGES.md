# Mudanças no Pipeline CI/CD

## Problema Identificado
O job `build-and-push` no pipeline estava criando imagens Docker incorretas e não seguindo a mesma lógica dos scripts `create-ecr-repository.sh` e `build-and-push.sh`, causando falhas no Terraform.

## Mudanças Implementadas

### 1. Job `build-and-push` Atualizado
- ✅ **Criação do repositório ECR**: Agora verifica e cria o repositório ECR se não existir
- ✅ **Variáveis padronizadas**: Usa as mesmas variáveis dos scripts (`PROJECT_NAME`, `ENVIRONMENT`)
- ✅ **Nomenclatura consistente**: `lambda-container-api-dev` (igual aos scripts)
- ✅ **Tags corretas**: `latest` e commit hash de 7 dígitos
- ✅ **Testes de imagem**: Valida se a imagem pode importar os módulos Python
- ✅ **Compatibilidade Lambda**: Verifica arquitetura amd64 e formato correto
- ✅ **Limpeza de imagens**: Remove imagens locais antigas antes do build
- ✅ **Atualização Lambda**: Atualiza função Lambda se já existir

### 2. Outputs Ajustados
```yaml
outputs:
  image-uri: ${{ steps.build-vars.outputs.full-image-latest }}
  image-tag: ${{ steps.build-vars.outputs.commit-hash }}
  ecr-repository: ${{ steps.build-vars.outputs.ecr-repository-name }}
```

### 3. Job `deploy` Atualizado
- ✅ **Variáveis Terraform**: Agora usa as variáveis corretas do build
- ✅ **ECR Repository**: Passa o nome correto do repositório
- ✅ **Image Tag**: Usa o commit hash correto

### 4. Fluxo Completo
1. **Test & Security Scan** → Valida código e segurança
2. **Build & Push** → Cria repositório ECR + build + push da imagem
3. **Deploy** → Terraform apply com imagem já disponível
4. **E2E Tests** → Testa API deployada

## Benefícios
- ✅ **Consistência**: Pipeline agora segue exatamente a mesma lógica dos scripts
- ✅ **Confiabilidade**: Terraform não falha mais por falta de repositório/imagem
- ✅ **Rastreabilidade**: Tags de commit permitem identificar versões específicas
- ✅ **Validação**: Testes garantem que a imagem funciona antes do push
- ✅ **Automação**: Criação automática do repositório ECR

## Próximos Passos
1. Testar o pipeline completo
2. Verificar se todas as variáveis Terraform estão corretas
3. Validar se os outputs estão sendo passados corretamente entre jobs