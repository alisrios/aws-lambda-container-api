# Guia do .gitignore

Este documento explica o que cada seção do arquivo `.gitignore` faz e por que é importante.

## 🐍 Python Específico

### Cache e Bytecode
```gitignore
__pycache__/
*.py[cod]
*$py.class
```
- **O que são**: Arquivos compilados Python para otimização
- **Por que ignorar**: São gerados automaticamente e específicos do ambiente

### Ambientes Virtuais
```gitignore
.env
.venv
venv/
ENV/
```
- **O que são**: Diretórios de ambientes virtuais Python
- **Por que ignorar**: Podem ser enormes (100MB+) e são específicos da máquina

### Testes e Cobertura
```gitignore
.pytest_cache/
.coverage
htmlcov/
coverage.xml
```
- **O que são**: Resultados de testes e relatórios de cobertura
- **Por que ignorar**: São gerados localmente e podem ser grandes

## 🏗️ Terraform

### Estados e Planos
```gitignore
*.tfstate
*.tfstate.*
.terraform/
tfplan
```
- **O que são**: Estado atual da infraestrutura e planos de execução
- **Por que ignorar**: Podem conter informações sensíveis e são específicos do ambiente

### Variáveis
```gitignore
*.tfvars
*.tfvars.json
```
- **O que são**: Arquivos com valores de variáveis (podem conter secrets)
- **Por que ignorar**: Frequentemente contêm informações sensíveis

## 💻 IDEs e Editores

### VS Code
```gitignore
.vscode/
*.code-workspace
```
- **O que são**: Configurações específicas do VS Code
- **Por que ignorar**: São preferências pessoais do desenvolvedor

### JetBrains (PyCharm, IntelliJ)
```gitignore
.idea/
```
- **O que são**: Configurações do IDE
- **Por que ignorar**: Específicas do usuário e podem causar conflitos

## 🖥️ Sistemas Operacionais

### macOS
```gitignore
.DS_Store
.AppleDouble
._*
```
- **O que são**: Arquivos de metadados do macOS
- **Por que ignorar**: Não são úteis em outros sistemas

### Windows
```gitignore
Thumbs.db
Desktop.ini
$RECYCLE.BIN/
```
- **O que são**: Arquivos de sistema do Windows
- **Por que ignorar**: Específicos do Windows e desnecessários

### Linux
```gitignore
*~
.directory
.Trash-*
```
- **O que são**: Arquivos temporários e de lixeira do Linux
- **Por que ignorar**: Temporários e específicos do sistema

## 🔒 Segurança

### Credenciais AWS
```gitignore
.aws/credentials
.aws/config
credentials
config
```
- **O que são**: Arquivos com chaves de acesso AWS
- **Por que ignorar**: **CRÍTICO** - nunca commitar credenciais!

### Certificados
```gitignore
*.pem
*.key
*.crt
*.p12
```
- **O que são**: Certificados e chaves privadas
- **Por que ignorar**: Informações sensíveis de segurança

### Variáveis de Ambiente
```gitignore
.env
.env.local
.env.production
```
- **O que são**: Arquivos com variáveis de ambiente (podem conter secrets)
- **Por que ignorar**: Frequentemente contêm informações sensíveis

## 🛠️ Desenvolvimento

### Arquivos de Teste Locais
```gitignore
test_*.py
*_test.py
test_implementation.py
run_local.py
```
- **O que são**: Scripts de teste e desenvolvimento local
- **Por que ignorar**: São específicos do ambiente de desenvolvimento

### Logs
```gitignore
*.log
logs/
```
- **O que são**: Arquivos de log da aplicação
- **Por que ignorar**: Podem ser grandes e são específicos da execução

### Arquivos Temporários
```gitignore
*.tmp
*.temp
temp/
tmp/
```
- **O que são**: Arquivos temporários criados durante desenvolvimento
- **Por que ignorar**: Temporários por natureza

## 📊 Relatórios e Resultados

### Testes de Performance
```gitignore
performance-results.json
load-test-results/
```
- **O que são**: Resultados de testes de performance
- **Por que ignorar**: São específicos da execução e podem ser grandes

### Relatórios de Segurança
```gitignore
safety-report.json
bandit-report.json
semgrep-report.json
```
- **O que são**: Relatórios de análise de segurança
- **Por que ignorar**: São gerados automaticamente e podem ser grandes

## 🎯 Benefícios do .gitignore

### ✅ **Repositório Limpo**
- Remove arquivos desnecessários
- Foca apenas no código fonte
- Facilita navegação

### ⚡ **Performance**
- Clones mais rápidos
- Menos dados para transferir
- Operações Git mais rápidas

### 🔒 **Segurança**
- Previne vazamento de credenciais
- Evita commit acidental de secrets
- Protege informações sensíveis

### 👥 **Colaboração**
- Evita conflitos de arquivos específicos do ambiente
- Mantém o repositório focado no código
- Facilita trabalho em equipe

## 🚨 Arquivos Importantes que NÃO estão no .gitignore

Estes arquivos **DEVEM** ser commitados:

- `src/` - Código fonte da aplicação
- `terraform/` - Configuração de infraestrutura (exceto estados)
- `Dockerfile` - Configuração do container
- `requirements.txt` - Dependências Python
- `.github/workflows/` - Configuração CI/CD
- `scripts/` - Scripts de build e deploy
- `README.md` - Documentação
- `tests/` - Testes unitários e de integração

## 💡 Dicas

1. **Sempre revisar** antes de fazer commit
2. **Usar `git status`** para ver o que será commitado
3. **Adicionar exceções** quando necessário com `!arquivo.txt`
4. **Manter atualizado** conforme o projeto evolui