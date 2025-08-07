# AWS Lambda Container API

Uma aplicação serverless completa demonstrando funções Lambda containerizadas com integração API Gateway, provisionamento automatizado de infraestrutura usando Terraform, e pipeline CI/CD automatizado.

## 📋 Visão Geral

Este projeto implementa uma API Python simples usando Flask, empacotada em container Docker, publicada no Amazon ECR, e deployada como função Lambda integrada com API Gateway HTTP. Todo o processo é automatizado através de pipeline CI/CD usando GitHub Actions.

### Funcionalidades

- ✅ **API REST simples** com endpoints `/hello` e `/echo`
- ✅ **Containerização Docker** otimizada para AWS Lambda
- ✅ **Infraestrutura como Código** usando Terraform
- ✅ **Pipeline CI/CD automatizado** com GitHub Actions
- ✅ **Testes abrangentes** (unitários, integração, end-to-end)
- ✅ **Monitoramento e logging** com CloudWatch
- ✅ **Segurança** com scanning de vulnerabilidades

### Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  GitHub Actions  │───▶│   Amazon ECR    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Terraform     │◀───│   Infrastructure │───▶│  AWS Lambda     │
│   State (S3)    │    │   Provisioning   │    │   Function      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  CloudWatch     │◀───│   API Gateway    │◀───│  Public Internet│
│  Logs           │    │   HTTP API       │    │   (HTTPS)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Pré-requisitos

- **Python 3.11+**
- **Docker** e Docker Compose
- **AWS CLI** configurado com credenciais
- **Terraform** 1.5.0+
- **Git** para controle de versão

### Instalação Local

1. **Clone o repositório**
   ```bash
   git clone <repository-url>
   cd aws-lambda-container-api
   ```

2. **Configure o ambiente Python**
   ```bash
   # Criar ambiente virtual
   python -m venv venv
   
   # Ativar ambiente virtual
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   # Instalar dependências
   pip install -r requirements-dev.txt
   ```

3. **Execute a aplicação localmente**
   ```bash
   python run_local.py
   ```

4. **Teste os endpoints**
   ```bash
   # Endpoint Hello
   curl http://localhost:5000/hello
   
   # Endpoint Echo
   curl "http://localhost:5000/echo?msg=Hello%20World"
   ```

### Teste com Docker

#### Opção 1: Container Individual

1. **Build da imagem Docker**
   ```bash
   docker build -t lambda-container-api .
   ```

2. **Execute o container localmente**
   ```bash
   # Usando Docker Lambda Runtime Interface Emulator
   docker run -p 9000:8080 lambda-container-api
   
   # Teste via curl
   curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
        -d '{"httpMethod":"GET","path":"/hello","queryStringParameters":null}'
   ```

#### Opção 2: Docker Compose (Recomendado)

Para uma experiência completa com interface web integrada:

1. **Inicie todos os serviços**
   ```bash
   # Usando Make (recomendado)
   make test
   
   # Ou usando Docker Compose diretamente
   docker-compose up -d
   ```

2. **Acesse a interface de teste**
   ```
   http://localhost:8000/test.html
   ```

3. **Comandos úteis do Make**
   ```bash
   make help          # Ver todos os comandos disponíveis
   make build         # Construir imagens
   make run           # Iniciar serviços
   make test          # Iniciar e tentar abrir no browser
   make open          # Mostrar URLs para acesso manual
   make stop          # Parar serviços
   make logs          # Ver logs
   make test-curl     # Testar com curl
   make health        # Verificar saúde dos serviços
   make clean         # Limpar recursos
   ```

**Serviços incluídos no Docker Compose:**
- `lambda-api`: API Lambda na porta 9000
- `test-server`: Servidor de teste com interface web na porta 8000

### Teste com Interface Web (Modo Manual)

Se preferir executar manualmente sem Docker Compose:

1. **Inicie o servidor proxy** (resolve problemas de CORS)
   ```bash
   python3 server.py
   ```

2. **Acesse a página de teste**
   ```
   http://localhost:8000/test.html
   ```

3. **Use a interface para testar**
   - Selecione o método HTTP (GET, POST, PUT, DELETE)
   - Configure o path (ex: `/hello`, `/echo`)
   - Adicione body JSON se necessário
   - Clique em "Testar API" para ver a resposta

**Arquivos incluídos:**
- `test.html` - Interface web para testes
- `server.py` - Servidor proxy Python que resolve CORS

**Serviços necessários:**
- Lambda API: `localhost:9000` (container Docker)
- Servidor proxy: `localhost:8000` (servidor Python)
- Interface de teste: `localhost:8000/test.html`

## 📚 Endpoints da API

### GET /hello

Retorna uma mensagem "Hello World" simples.

**Resposta de Sucesso (200)**
```json
{
  "message": "Hello World",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### GET /echo

Retorna a mensagem fornecida no parâmetro `msg`.

**Parâmetros**
- `msg` (string, obrigatório): Mensagem para ecoar

**Resposta de Sucesso (200)**
```json
{
  "message": "sua_mensagem_aqui",
  "echo": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Resposta de Erro (400)**
```json
{
  "error": "Parameter 'msg' is required",
  "status_code": 400,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🧪 Executando Testes

### Testes Locais

```bash
# Executar todos os testes
pytest

# Executar com coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Executar apenas testes unitários
pytest tests/unit/

# Executar apenas testes de integração
pytest tests/integration/

# Executar com script de teste completo
python run_tests.py
```

### Estrutura de Testes

```
tests/
├── unit/                    # Testes unitários
│   ├── test_app.py         # Testes da aplicação Flask
│   └── test_lambda_handler.py  # Testes do handler Lambda
├── integration/            # Testes de integração
│   └── test_api_endpoints.py   # Testes dos endpoints da API
├── conftest.py            # Configuração compartilhada
└── README.md              # Documentação dos testes
```

### Coverage Report

Os relatórios de coverage são gerados em:
- **HTML**: `htmlcov/index.html`
- **Terminal**: Output detalhado com linhas não cobertas
- **XML**: `coverage.xml` para integração CI/CD

## 🏗️ Estrutura do Projeto

```
aws-lambda-container-api/
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # Pipeline CI/CD
├── .kiro/
│   └── specs/                  # Especificações do projeto
├── src/
│   ├── app.py                  # Aplicação Flask principal
│   ├── lambda_function.py      # Handler AWS Lambda
│   └── requirements.txt        # Dependências Python
├── terraform/
│   ├── main.tf                 # Recursos principais
│   ├── variables.tf            # Variáveis de entrada
│   ├── outputs.tf              # Outputs da infraestrutura
│   ├── versions.tf             # Versões dos providers
│   └── backend.tf.example      # Configuração do backend S3
├── tests/
│   ├── unit/                   # Testes unitários
│   ├── integration/            # Testes de integração
│   └── conftest.py             # Configuração dos testes
├── Dockerfile                  # Configuração do container Lambda
├── Dockerfile.test             # Container para servidor de teste
├── docker-compose.yml          # Orquestração de serviços
├── Makefile                    # Comandos automatizados
├── server.py                   # Servidor proxy para testes
├── test.html                   # Interface web para testes
├── requirements-dev.txt        # Dependências de desenvolvimento
├── run_local.py               # Servidor de desenvolvimento
├── run_tests.py               # Script de execução de testes
└── README.md                  # Esta documentação
```

## 🔧 Configuração de Desenvolvimento

### Variáveis de Ambiente

Para desenvolvimento local, configure as seguintes variáveis:

```bash
# Configurações da aplicação
export LOG_LEVEL=INFO
export ENVIRONMENT=development
export API_VERSION=1.0.0

# Configurações AWS (para testes locais)
export AWS_REGION=us-east-1
export AWS_PROFILE=default
```

### Configuração do Editor

**VS Code** (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"]
}
```

### Git Hooks (Opcional)

Configure pre-commit hooks para qualidade de código:

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Executar manualmente
pre-commit run --all-files
```

## 🐛 Troubleshooting

### Problemas Comuns

**1. Erro de Import no Python**
```bash
# Solução: Adicionar src/ ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:./src"
```

**2. Docker Build Falha**
```bash
# Verificar se Docker está rodando
docker --version
docker info

# Limpar cache do Docker
docker system prune -f
```

**3. Testes Falhando**
```bash
# Executar com output detalhado
pytest -v --tb=long

# Verificar dependências
pip install -r requirements-dev.txt
```

**4. Problemas de Permissão AWS**
```bash
# Verificar credenciais
aws sts get-caller-identity

# Configurar perfil
aws configure --profile default
```

### Logs e Debugging

**Logs da Aplicação Local**
```bash
# Executar com debug habilitado
python run_local.py
```

**Logs do Container**
```bash
# Ver logs do container
docker logs <container-id>

# Executar container em modo interativo
docker run -it lambda-container-api /bin/bash
```

## 📊 Métricas e Monitoramento

### Métricas Locais

- **Coverage de Testes**: >85% (atual: 87%)
- **Tempo de Build**: ~2-3 minutos
- **Tempo de Testes**: ~6 segundos
- **Tamanho da Imagem**: ~150MB

### Ferramentas de Qualidade

- **Black**: Formatação de código
- **isort**: Organização de imports
- **flake8**: Linting e análise estática
- **pytest**: Framework de testes
- **safety**: Verificação de vulnerabilidades
- **bandit**: Análise de segurança

## 🤝 Contribuindo

1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

### Padrões de Código

- Seguir **PEP 8** para Python
- Usar **Black** para formatação automática
- Manter **coverage >85%** nos testes
- Documentar funções públicas com **docstrings**
- Usar **type hints** quando apropriado

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Documentação**: Veja os arquivos em `.kiro/specs/` para especificações detalhadas
- **Issues**: Use o GitHub Issues para reportar bugs
- **Discussões**: Use GitHub Discussions para perguntas gerais
- **Wiki**: Documentação adicional no GitHub Wiki

---

**Desenvolvido com ❤️ usando AWS Lambda, Docker, Terraform e GitHub Actions**