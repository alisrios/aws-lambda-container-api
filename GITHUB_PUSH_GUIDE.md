# 🚀 Guia para Push no GitHub

Este guia te ajudará a fazer o push do projeto AWS Lambda Container API para o GitHub.

## 📋 Pré-requisitos

- [x] Conta no GitHub
- [x] Git configurado localmente
- [x] Projeto commitado localmente

## 🔧 Passos para Push

### 1. Criar Repositório no GitHub

1. Acesse [GitHub](https://github.com)
2. Clique em "New repository" ou "+"
3. Configure o repositório:
   - **Repository name**: `aws-lambda-container-api`
   - **Description**: `Serverless API using AWS Lambda containers with Terraform IaC and CI/CD pipeline`
   - **Visibility**: Public ou Private (sua escolha)
   - **NÃO** inicialize com README, .gitignore ou license (já temos esses arquivos)

### 2. Conectar Repositório Local ao GitHub

```bash
# Navegar para o diretório do projeto
cd /mnt/d/Alisson/AWS/Lambda

# Adicionar remote origin (substitua YOUR-USERNAME pelo seu username)
git remote add origin https://github.com/YOUR-USERNAME/aws-lambda-container-api.git

# Verificar se o remote foi adicionado
git remote -v
```

### 3. Fazer Push para GitHub

```bash
# Push da branch main
git push -u origin main
```

### 4. Configurar Branch Protection (Recomendado)

No GitHub, vá para Settings > Branches e configure:

- [x] Require pull request reviews before merging
- [x] Require status checks to pass before merging
- [x] Require branches to be up to date before merging
- [x] Include administrators

### 5. Configurar Secrets para CI/CD

No GitHub, vá para Settings > Secrets and variables > Actions e adicione:

```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

**⚠️ IMPORTANTE**: Use credenciais com permissões mínimas necessárias.

## 📚 Arquivos Incluídos no Push

### 📄 Documentação
- [x] `README.md` - Documentação principal
- [x] `CONTRIBUTING.md` - Guia de contribuição
- [x] `CHANGELOG.md` - Histórico de mudanças
- [x] `SECURITY.md` - Política de segurança
- [x] `LICENSE` - Licença MIT

### 🔧 Configuração
- [x] `.gitignore` - Arquivos ignorados
- [x] `.pre-commit-config.yaml` - Hooks de pre-commit
- [x] `setup.sh` - Script de configuração

### 🐛 Templates GitHub
- [x] `.github/ISSUE_TEMPLATE/bug_report.md`
- [x] `.github/ISSUE_TEMPLATE/feature_request.md`
- [x] `.github/pull_request_template.md`

### 🚀 CI/CD
- [x] `.github/workflows/ci-cd.yml` - Pipeline GitHub Actions

### 💻 Código
- [x] `src/app.py` - Aplicação Flask
- [x] `src/lambda_function.py` - Handler Lambda
- [x] `src/requirements.txt` - Dependências

### 🏗️ Infraestrutura
- [x] `terraform/` - Configuração Terraform
- [x] `Dockerfile` - Container configuration
- [x] `docker-compose.yml` - Desenvolvimento local

### 🧪 Testes
- [x] `tests/` - Suite de testes
- [x] `pytest.ini` - Configuração pytest

## 🔍 Verificações Pós-Push

### 1. Verificar Repository

- [ ] README.md está sendo exibido corretamente
- [ ] Badges estão funcionando
- [ ] Estrutura de arquivos está correta

### 2. Testar CI/CD

- [ ] GitHub Actions está executando
- [ ] Testes estão passando
- [ ] Build está funcionando

### 3. Configurar Proteções

- [ ] Branch protection configurada
- [ ] Secrets configurados
- [ ] Collaborators adicionados (se necessário)

## 🎯 Próximos Passos

### 1. Atualizar README

Substitua no README.md:
```markdown
# Antes
https://github.com/your-username/aws-lambda-container-api

# Depois
https://github.com/SEU-USERNAME/aws-lambda-container-api
```

### 2. Configurar Releases

```bash
# Criar primeira release
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

### 3. Configurar GitHub Pages (Opcional)

Para documentação adicional:
1. Settings > Pages
2. Source: Deploy from a branch
3. Branch: main / docs

### 4. Configurar Dependabot

Crie `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "terraform"
    directory: "/terraform"
    schedule:
      interval: "weekly"
```

## 🛡️ Segurança

### ⚠️ NUNCA commitar:
- [ ] Credenciais AWS
- [ ] Chaves privadas
- [ ] Tokens de acesso
- [ ] Arquivos .tfstate com dados sensíveis

### ✅ Sempre verificar:
- [ ] .gitignore está funcionando
- [ ] Secrets estão no GitHub Secrets
- [ ] Permissões IAM são mínimas

## 🆘 Troubleshooting

### Erro: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR-USERNAME/aws-lambda-container-api.git
```

### Erro: "failed to push some refs"
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Erro: "Permission denied"
```bash
# Verificar autenticação
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Ou usar SSH
git remote set-url origin git@github.com:YOUR-USERNAME/aws-lambda-container-api.git
```

## 📞 Suporte

Se encontrar problemas:

1. **GitHub Docs**: https://docs.github.com/
2. **Git Docs**: https://git-scm.com/doc
3. **Issues**: Abra uma issue no repositório

---

**🎉 Parabéns! Seu projeto está pronto para o GitHub!**

Lembre-se de:
- ⭐ Dar uma estrela no seu próprio projeto
- 📝 Manter a documentação atualizada
- 🔄 Usar o CI/CD pipeline
- 🤝 Aceitar contribuições da comunidade
