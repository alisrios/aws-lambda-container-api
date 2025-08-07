# Guia de Testes e Validação - AWS Lambda Container API

Este documento fornece instruções detalhadas sobre como executar, interpretar e manter os testes da aplicação AWS Lambda Container API.

## 📋 Índice

- [Visão Geral dos Testes](#-visão-geral-dos-testes)
- [Configuração do Ambiente de Testes](#-configuração-do-ambiente-de-testes)
- [Executando Testes Localmente](#-executando-testes-localmente)
- [Tipos de Testes](#-tipos-de-testes)
- [Testando Endpoints da API](#-testando-endpoints-da-api)
- [Exemplos de Requisições e Respostas](#-exemplos-de-requisições-e-respostas)
- [Coverage e Qualidade](#-coverage-e-qualidade)
- [Testes de Container](#-testes-de-container)
- [Testes End-to-End](#-testes-end-to-end)
- [Troubleshooting](#-troubleshooting)

## 🔍 Visão Geral dos Testes

### Estratégia de Testes

A aplicação utiliza uma estratégia de testes em múltiplas camadas:

```
┌─────────────────────────────────────────────────────────────┐
│                    End-to-End Tests                         │
│              (API deployada na AWS)                        │
├─────────────────────────────────────────────────────────────┤
│                  Integration Tests                          │
│            (Flask app + Lambda handler)                    │
├─────────────────────────────────────────────────────────────┤
│                    Unit Tests                               │
│         (Funções individuais isoladas)                     │
├─────────────────────────────────────────────────────────────┤
│                  Container Tests                            │
│              (Docker functionality)                        │
└─────────────────────────────────────────────────────────────┘
```

### Métricas de Qualidade

- **Coverage Mínimo**: 85%
- **Coverage Atual**: 87%
- **Tempo de Execução**: ~6 segundos
- **Testes Totais**: 25+ testes

### Ferramentas Utilizadas

- **pytest**: Framework principal de testes
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking e fixtures
- **requests**: Testes de API HTTP
- **Docker**: Testes de container

## ⚙️ Configuração do Ambiente de Testes

### Pré-requisitos

```bash
# Python 3.11+
python --version

# Dependências de desenvolvimento
pip install -r requirements-dev.txt

# Docker (para testes de container)
docker --version
```

### Configuração Inicial

```bash
# 1. Clonar repositório
git clone <repository-url>
cd aws-lambda-container-api

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements-dev.txt

# 5. Configurar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:./src"
```

### Variáveis de Ambiente para Testes

```bash
# Configurações de teste
export TESTING=true
export LOG_LEVEL=DEBUG
export ENVIRONMENT=test

# Para testes de integração com AWS (opcional)
export AWS_REGION=us-east-1
export AWS_PROFILE=test
```

## 🧪 Executando Testes Localmente

### Comandos Básicos

```bash
# Executar todos os testes
pytest

# Executar com output verboso
pytest -v

# Executar testes específicos
pytest tests/unit/
pytest tests/integration/
pytest tests/unit/test_app.py

# Executar teste específico
pytest tests/unit/test_app.py::test_hello_endpoint

# Executar com coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Executar em paralelo (mais rápido)
pytest -n auto
```

### Script de Teste Completo

```bash
# Usar o script de teste integrado
python run_tests.py

# Ou executar manualmente todas as verificações
python run_tests.py --full
```

### Configuração Personalizada

O arquivo `pytest.ini` contém as configurações padrão:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=85
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

## 🔬 Tipos de Testes

### 1. Testes Unitários (`tests/unit/`)

Testam componentes individuais isoladamente.

#### Flask Application Tests (`test_app.py`)

```python
# Exemplo de teste unitário
def test_hello_endpoint():
    """Testa o endpoint /hello"""
    with app.test_client() as client:
        response = client.get('/hello')
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Hello World'
        assert 'timestamp' in data
        assert data['version'] == '1.0.0'
```

**Executar apenas testes unitários:**
```bash
pytest tests/unit/ -v
```

#### Lambda Handler Tests (`test_lambda_handler.py`)

```python
# Exemplo de teste do handler Lambda
def test_lambda_handler_hello():
    """Testa handler Lambda para endpoint /hello"""
    event = {
        'httpMethod': 'GET',
        'path': '/hello',
        'queryStringParameters': None
    }
    
    response = lambda_handler(event, mock_context)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Hello World'
```

### 2. Testes de Integração (`tests/integration/`)

Testam a interação entre componentes.

#### API Endpoints Integration (`test_api_endpoints.py`)

```python
# Exemplo de teste de integração
def test_multiple_requests():
    """Testa múltiplas requisições consecutivas"""
    with app.test_client() as client:
        # Primeira requisição
        response1 = client.get('/hello')
        assert response1.status_code == 200
        
        # Segunda requisição
        response2 = client.get('/echo?msg=test')
        assert response2.status_code == 200
        
        # Verificar que ambas funcionam
        data2 = response2.get_json()
        assert data2['message'] == 'test'
```

**Executar apenas testes de integração:**
```bash
pytest tests/integration/ -v
```

### 3. Testes de Container

Testam a funcionalidade do Docker container.

```bash
# Build da imagem para teste
docker build -t lambda-container-api-test .

# Executar container em modo de teste
docker run --rm -d -p 9000:8080 \
  --name lambda-test \
  lambda-container-api-test

# Testar endpoints via container
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"httpMethod":"GET","path":"/hello","queryStringParameters":null}'

# Cleanup
docker stop lambda-test
```

### 4. Testes End-to-End

Testam a aplicação deployada na AWS.

```bash
# Definir URL da API deployada
export API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com"

# Executar testes E2E
pytest tests/e2e/ --api-url=$API_URL -v
```

## 🌐 Testando Endpoints da API

### Teste Manual com curl

#### Endpoint /hello

```bash
# Teste básico
curl -X GET "http://localhost:5000/hello"

# Com headers detalhados
curl -X GET "http://localhost:5000/hello" \
  -H "Accept: application/json" \
  -H "User-Agent: TestClient/1.0" \
  -v

# Teste de performance (múltiplas requisições)
for i in {1..10}; do
  curl -s "http://localhost:5000/hello" | jq '.timestamp'
done
```

#### Endpoint /echo

```bash
# Teste com parâmetro
curl -X GET "http://localhost:5000/echo?msg=Hello%20World"

# Teste sem parâmetro (deve retornar erro)
curl -X GET "http://localhost:5000/echo"

# Teste com caracteres especiais
curl -X GET "http://localhost:5000/echo?msg=Olá%20Mundo%21"

# Teste com parâmetro longo
curl -X GET "http://localhost:5000/echo?msg=$(python -c 'print("A"*1000)')"
```

### Teste com Python requests

```python
import requests
import json

# Configurar base URL
BASE_URL = "http://localhost:5000"

def test_hello_endpoint():
    """Teste do endpoint /hello"""
    response = requests.get(f"{BASE_URL}/hello")
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['message'] == 'Hello World'

def test_echo_endpoint():
    """Teste do endpoint /echo"""
    test_message = "Test message 123"
    response = requests.get(f"{BASE_URL}/echo", params={'msg': test_message})
    
    print(f"Status: {response.status_code}")
    print(f"Body: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['message'] == test_message
    assert data['echo'] == True

if __name__ == "__main__":
    test_hello_endpoint()
    test_echo_endpoint()
    print("Todos os testes passaram!")
```

### Teste de Carga Simples

```bash
# Usando Apache Bench (ab)
ab -n 100 -c 10 http://localhost:5000/hello

# Usando curl em loop
time for i in {1..100}; do
  curl -s http://localhost:5000/hello > /dev/null
done
```

## 📊 Exemplos de Requisições e Respostas

### Endpoint /hello

#### Requisição Válida

```http
GET /hello HTTP/1.1
Host: localhost:5000
Accept: application/json
User-Agent: TestClient/1.0
```

#### Resposta de Sucesso (200)

```json
{
  "message": "Hello World",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### Endpoint /echo

#### Requisição Válida

```http
GET /echo?msg=Hello%20World HTTP/1.1
Host: localhost:5000
Accept: application/json
```

#### Resposta de Sucesso (200)

```json
{
  "message": "Hello World",
  "echo": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Requisição Inválida (sem parâmetro)

```http
GET /echo HTTP/1.1
Host: localhost:5000
Accept: application/json
```

#### Resposta de Erro (400)

```json
{
  "error": "Parameter 'msg' is required",
  "status_code": 400,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Casos de Teste Especiais

#### Caracteres Unicode

```bash
# Requisição
curl "http://localhost:5000/echo?msg=Olá%20Mundo%20🌍"

# Resposta esperada
{
  "message": "Olá Mundo 🌍",
  "echo": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Parâmetros Longos

```bash
# Requisição com 1000 caracteres
curl "http://localhost:5000/echo?msg=$(python -c 'print("A"*1000)')"

# Deve funcionar normalmente
```

#### Caracteres Especiais

```bash
# Requisição
curl "http://localhost:5000/echo?msg=%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E"

# Resposta (sem processamento especial)
{
  "message": "<script>alert('xss')</script>",
  "echo": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 📈 Coverage e Qualidade

### Relatório de Coverage

```bash
# Gerar relatório HTML
pytest --cov=src --cov-report=html

# Abrir relatório no navegador
# Windows
start htmlcov/index.html
# Linux/Mac
open htmlcov/index.html
```

### Interpretando Coverage

```bash
# Relatório no terminal
pytest --cov=src --cov-report=term-missing

# Exemplo de output:
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/app.py                 45      3    93%   67-69
src/lambda_function.py     32      2    94%   45, 52
-----------------------------------------------------
TOTAL                      77      5    94%
```

### Métricas de Qualidade

#### Coverage por Arquivo

- **src/app.py**: 93% (endpoints Flask)
- **src/lambda_function.py**: 94% (handler Lambda)
- **Total**: 94% (acima do mínimo de 85%)

#### Linhas Não Cobertas

```python
# Exemplo de código não coberto
try:
    # Código principal
    pass
except Exception as e:
    # Esta linha pode não estar coberta
    logger.error(f"Unexpected error: {e}")  # Linha 67-69
    return error_response(500)
```

### Melhorando Coverage

```python
# Adicionar teste para casos de erro
def test_unexpected_error(mocker):
    """Testa tratamento de erro inesperado"""
    # Mock para forçar exceção
    mocker.patch('src.app.jsonify', side_effect=Exception("Test error"))
    
    with app.test_client() as client:
        response = client.get('/hello')
        assert response.status_code == 500
```

## 🐳 Testes de Container

### Build e Teste Local

```bash
# 1. Build da imagem
docker build -t lambda-container-api-test .

# 2. Executar container
docker run --rm -d -p 9000:8080 \
  --name lambda-test \
  lambda-container-api-test

# 3. Aguardar inicialização
sleep 5

# 4. Testar endpoint /hello
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{
    "httpMethod": "GET",
    "path": "/hello",
    "queryStringParameters": null
  }' | jq '.'

# 5. Testar endpoint /echo
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{
    "httpMethod": "GET",
    "path": "/echo",
    "queryStringParameters": {"msg": "container-test"}
  }' | jq '.'

# 6. Cleanup
docker stop lambda-test
```

### Teste de Health Check

```bash
# Verificar health check do container
docker run --rm lambda-container-api-test python -c "
import app
print('Health check passed')
"
```

### Teste de Performance do Container

```bash
# Medir tempo de cold start
time docker run --rm lambda-container-api-test python -c "
import lambda_function
print('Container ready')
"

# Teste de múltiplas invocações
for i in {1..5}; do
  echo "Invocação $i:"
  time curl -s -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
    -d '{"httpMethod":"GET","path":"/hello","queryStringParameters":null}' \
    | jq -r '.body | fromjson | .timestamp'
done
```

## 🌍 Testes End-to-End

### Configuração

```bash
# Definir URL da API deployada
export API_URL="https://abc123.execute-api.us-east-1.amazonaws.com"

# Ou obter do Terraform
export API_URL=$(cd terraform && terraform output -raw api_gateway_url)
```

### Script de Teste E2E

```bash
#!/bin/bash
# test-e2e.sh

set -e

API_URL=${API_URL:-"https://your-api-gateway-url"}

echo "🧪 Executando testes End-to-End..."
echo "API URL: $API_URL"

# Teste 1: Hello endpoint
echo "Testando /hello..."
HELLO_RESPONSE=$(curl -s "$API_URL/hello")
if echo "$HELLO_RESPONSE" | jq -e '.message == "Hello World"' > /dev/null; then
  echo "✅ Hello endpoint OK"
else
  echo "❌ Hello endpoint FALHOU"
  echo "$HELLO_RESPONSE"
  exit 1
fi

# Teste 2: Echo endpoint
echo "Testando /echo..."
ECHO_RESPONSE=$(curl -s "$API_URL/echo?msg=e2e-test")
if echo "$ECHO_RESPONSE" | jq -e '.message == "e2e-test"' > /dev/null; then
  echo "✅ Echo endpoint OK"
else
  echo "❌ Echo endpoint FALHOU"
  echo "$ECHO_RESPONSE"
  exit 1
fi

# Teste 3: Error handling
echo "Testando error handling..."
ERROR_RESPONSE=$(curl -s "$API_URL/echo")
if echo "$ERROR_RESPONSE" | jq -e '.error' > /dev/null; then
  echo "✅ Error handling OK"
else
  echo "❌ Error handling FALHOU"
  echo "$ERROR_RESPONSE"
  exit 1
fi

# Teste 4: Performance
echo "Testando performance..."
START_TIME=$(date +%s%N)
for i in {1..10}; do
  curl -s "$API_URL/hello" > /dev/null
done
END_TIME=$(date +%s%N)
DURATION=$(( (END_TIME - START_TIME) / 1000000 ))
echo "✅ 10 requisições em ${DURATION}ms (média: $((DURATION/10))ms)"

echo "🎉 Todos os testes E2E passaram!"
```

### Executar Testes E2E

```bash
# Tornar script executável
chmod +x test-e2e.sh

# Executar testes
./test-e2e.sh

# Ou com URL específica
API_URL="https://your-api.execute-api.us-east-1.amazonaws.com" ./test-e2e.sh
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Testes Falhando Localmente

**Sintoma**: `ImportError` ou `ModuleNotFoundError`

**Solução**:
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:./src"

# Ou instalar em modo desenvolvimento
pip install -e .
```

#### 2. Coverage Baixo

**Sintoma**: Coverage abaixo de 85%

**Solução**:
```bash
# Ver linhas não cobertas
pytest --cov=src --cov-report=term-missing

# Adicionar testes para linhas específicas
pytest --cov=src --cov-report=html
# Abrir htmlcov/index.html para análise detalhada
```

#### 3. Testes Lentos

**Sintoma**: Testes demoram muito para executar

**Solução**:
```bash
# Executar em paralelo
pytest -n auto

# Pular testes lentos
pytest -m "not slow"

# Executar apenas testes rápidos
pytest tests/unit/
```

#### 4. Container Tests Falhando

**Sintoma**: Erro ao conectar com container

**Solução**:
```bash
# Verificar se container está rodando
docker ps

# Verificar logs do container
docker logs lambda-test

# Aguardar inicialização
sleep 10

# Verificar porta
netstat -an | grep 9000
```

#### 5. E2E Tests Falhando

**Sintoma**: Timeout ou erro de conexão

**Solução**:
```bash
# Verificar URL da API
echo $API_URL

# Testar conectividade
curl -I $API_URL/hello

# Verificar logs CloudWatch
aws logs tail /aws/lambda/your-function-name --follow
```

### Debug de Testes

#### Executar com Debug

```bash
# Pytest com debug
pytest --pdb

# Ou com logging detalhado
pytest -s --log-cli-level=DEBUG

# Executar teste específico com debug
pytest tests/unit/test_app.py::test_hello_endpoint -s -vv
```

#### Usar Debugger

```python
# Adicionar breakpoint no código de teste
def test_hello_endpoint():
    import pdb; pdb.set_trace()  # Breakpoint
    
    with app.test_client() as client:
        response = client.get('/hello')
        assert response.status_code == 200
```

### Logs e Monitoramento

#### Logs de Teste

```bash
# Executar com logs detalhados
pytest --log-cli-level=INFO --log-cli-format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s'

# Salvar logs em arquivo
pytest --log-file=tests.log --log-file-level=DEBUG
```

#### Monitoramento de Performance

```python
import time
import pytest

@pytest.fixture(autouse=True)
def measure_test_time(request):
    """Mede tempo de execução de cada teste"""
    start = time.time()
    yield
    duration = time.time() - start
    print(f"\n{request.node.name}: {duration:.2f}s")
```

## 📋 Checklist de Validação

### Antes de Commit

- [ ] Todos os testes passam (`pytest`)
- [ ] Coverage >= 85% (`pytest --cov=src`)
- [ ] Linting OK (`flake8 src/ tests/`)
- [ ] Formatação OK (`black --check src/ tests/`)
- [ ] Imports organizados (`isort --check src/ tests/`)

### Antes de Deploy

- [ ] Testes unitários passam
- [ ] Testes de integração passam
- [ ] Container build OK
- [ ] Testes de container passam
- [ ] Security scan limpo

### Após Deploy

- [ ] Testes E2E passam
- [ ] API responde corretamente
- [ ] Logs CloudWatch OK
- [ ] Métricas normais
- [ ] Performance aceitável

---

**Para mais informações:**
- [README.md](README.md) - Documentação geral
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guia de deployment
- [CI-CD.md](CI-CD.md) - Pipeline automatizado