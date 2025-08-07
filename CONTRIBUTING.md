# Contribuindo para AWS Lambda Container API

Obrigado por considerar contribuir para este projeto! Este documento fornece diretrizes para contribuições.

## 🚀 Como Contribuir

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/SEU-USERNAME/aws-lambda-container-api.git
cd aws-lambda-container-api

# Adicione o repositório original como upstream
git remote add upstream https://github.com/ORIGINAL-USERNAME/aws-lambda-container-api.git
```

### 2. Configurar Ambiente de Desenvolvimento

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Instalar pre-commit hooks
pre-commit install
```

### 3. Criar Branch para Feature

```bash
# Sincronizar com upstream
git fetch upstream
git checkout main
git merge upstream/main

# Criar nova branch
git checkout -b feature/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

## 📝 Padrões de Código

### Python

- **PEP 8**: Seguir as convenções de estilo Python
- **Type Hints**: Usar anotações de tipo quando apropriado
- **Docstrings**: Documentar funções públicas
- **Black**: Formatação automática de código

```bash
# Formatar código
black src/ tests/

# Verificar lint
flake8 src/ tests/

# Verificar tipos
mypy src/
```

### Terraform

- **Formatação**: Usar `terraform fmt`
- **Validação**: Executar `terraform validate`
- **Documentação**: Comentar recursos complexos

```bash
# Formatar Terraform
terraform fmt -recursive terraform/

# Validar configuração
terraform validate terraform/
```

### Docker

- **Multi-stage builds**: Para otimização de tamanho
- **Security**: Usar imagens base oficiais
- **Labels**: Adicionar metadados apropriados

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Testes específicos
pytest tests/unit/
pytest tests/integration/
```

### Escrever Testes

- **Cobertura**: Manter >85% de cobertura
- **Nomenclatura**: `test_funcao_cenario_resultado`
- **Fixtures**: Usar fixtures para setup comum
- **Mocks**: Mockar dependências externas

```python
def test_hello_endpoint_returns_success():
    """Test that /hello endpoint returns 200 with correct message."""
    # Arrange
    # Act
    # Assert
```

## 📋 Processo de Contribuição

### 1. Issues

- **Bug Reports**: Use o template de bug report
- **Feature Requests**: Use o template de feature request
- **Discussões**: Use GitHub Discussions para perguntas

### 2. Pull Requests

#### Checklist antes do PR

- [ ] Código formatado com Black
- [ ] Testes passando
- [ ] Coverage >85%
- [ ] Documentação atualizada
- [ ] Changelog atualizado (se aplicável)
- [ ] Terraform validado
- [ ] Docker build funcionando

#### Template de PR

```markdown
## Descrição
Breve descrição das mudanças.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. Passos para testar
2. Comandos específicos
3. Resultados esperados

## Checklist
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Self-review realizado
```

### 3. Review Process

1. **Automated Checks**: CI/CD deve passar
2. **Code Review**: Pelo menos 1 aprovação
3. **Testing**: Testar localmente se necessário
4. **Merge**: Squash and merge preferido

## 🏗️ Estrutura do Projeto

### Diretórios Importantes

```
├── src/                    # Código fonte da aplicação
├── tests/                  # Testes automatizados
├── terraform/              # Infraestrutura como código
├── .github/workflows/      # CI/CD pipelines
├── docs/                   # Documentação adicional
└── scripts/                # Scripts utilitários
```

### Convenções de Nomenclatura

- **Arquivos**: `snake_case.py`
- **Classes**: `PascalCase`
- **Funções**: `snake_case`
- **Constantes**: `UPPER_CASE`
- **Branches**: `feature/nome-da-feature`, `fix/nome-do-bug`

## 🔧 Desenvolvimento Local

### Configuração AWS

```bash
# Configurar credenciais AWS
aws configure

# Ou usar variáveis de ambiente
export AWS_PROFILE=dev
export AWS_REGION=us-east-1
```

### Executar Localmente

```bash
# Aplicação Flask
python run_local.py

# Container Docker
docker-compose up -d

# Testes de integração
make test
```

### Debug

```bash
# Logs detalhados
export LOG_LEVEL=DEBUG

# Debug do Terraform
export TF_LOG=DEBUG

# Debug do Docker
docker-compose logs -f
```

## 📚 Recursos Úteis

### Documentação

- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/python-programming-model.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Ferramentas

- **IDE**: VS Code com extensões Python, Terraform
- **Testing**: pytest, coverage
- **Linting**: flake8, black, mypy
- **Security**: bandit, safety

## 🐛 Reportar Bugs

### Informações Necessárias

1. **Versão**: Python, Docker, Terraform, AWS CLI
2. **Ambiente**: OS, região AWS
3. **Reprodução**: Passos detalhados
4. **Logs**: Mensagens de erro completas
5. **Comportamento Esperado**: O que deveria acontecer

### Template de Bug Report

```markdown
**Descrição do Bug**
Descrição clara e concisa do bug.

**Reproduzir**
Passos para reproduzir:
1. Vá para '...'
2. Clique em '....'
3. Role para baixo até '....'
4. Veja o erro

**Comportamento Esperado**
O que você esperava que acontecesse.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente:**
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.11]
- Docker: [e.g. 20.10.7]
- AWS CLI: [e.g. 2.4.6]

**Contexto Adicional**
Qualquer outro contexto sobre o problema.
```

## 🎯 Roadmap

Veja [Issues](https://github.com/your-username/aws-lambda-container-api/issues) para features planejadas e bugs conhecidos.

## 📞 Contato

- **Issues**: Para bugs e feature requests
- **Discussions**: Para perguntas e discussões
- **Email**: Para questões sensíveis

---

**Obrigado por contribuir! 🙏**
