# Configuração das Credenciais AWS

## Passo 1: Configurar Credenciais AWS

Você precisa configurar suas credenciais AWS antes de executar o script. Há algumas opções:

### Opção 1: AWS Configure (Recomendado)
```bash
aws configure
```

Quando solicitado, insira:
- **AWS Access Key ID**: Sua chave de acesso
- **AWS Secret Access Key**: Sua chave secreta
- **Default region name**: `us-east-1`
- **Default output format**: `json`

### Opção 2: Variáveis de Ambiente
```bash
export AWS_ACCESS_KEY_ID="sua-access-key"
export AWS_SECRET_ACCESS_KEY="sua-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Opção 3: AWS Profile
Se você tem múltiplos perfis:
```bash
aws configure --profile meu-perfil
```

E depois use:
```bash
export AWS_PROFILE=meu-perfil
```

## Passo 2: Verificar Configuração

```bash
aws sts get-caller-identity
```

Deve retornar algo como:
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/DevAdmin"
}
```

## Passo 3: Executar o Script

Após configurar as credenciais:

```bash
./build-and-push.sh
```

## Permissões Necessárias

Sua conta AWS precisa das seguintes permissões:

### ECR (Elastic Container Registry)
- `ecr:CreateRepository`
- `ecr:DescribeRepositories`
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:GetDownloadUrlForLayer`
- `ecr:BatchGetImage`
- `ecr:InitiateLayerUpload`
- `ecr:UploadLayerPart`
- `ecr:CompleteLayerUpload`
- `ecr:PutImage`

### Lambda
- `lambda:GetFunction`
- `lambda:UpdateFunctionCode`

### STS (Security Token Service)
- `sts:GetCallerIdentity`

## Política IAM Exemplo

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:*",
                "lambda:GetFunction",
                "lambda:UpdateFunctionCode",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

## Troubleshooting

### Erro: "Unable to locate credentials"
- Execute `aws configure` para configurar suas credenciais
- Verifique se as variáveis de ambiente estão definidas
- Confirme se o perfil AWS está correto

### Erro: "Access Denied"
- Verifique se sua conta tem as permissões necessárias
- Confirme se você está usando a região correta
- Verifique se as credenciais não expiraram

### Erro: "Region not specified"
- Configure a região padrão: `aws configure set region us-east-1`
- Ou use a variável de ambiente: `export AWS_DEFAULT_REGION=us-east-1`