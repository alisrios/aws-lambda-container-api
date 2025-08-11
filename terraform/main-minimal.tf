# Minimal Terraform configuration for initial deployment
# This creates only the essential resources to get the pipeline working

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local values
locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.id

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  lambda_function_name = "${var.project_name}-${var.environment}"
}

# Use existing ECR Repository (don't create new one)
data "aws_ecr_repository" "main" {
  name = "lambda-container-api-dev"
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.lambda_function_name}"
  retention_in_days = 14

  tags = local.common_tags
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda" {
  name = "${local.lambda_function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# IAM Policy for Lambda basic execution
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda.name
}

# Lambda Function
resource "aws_lambda_function" "main" {
  function_name = local.lambda_function_name
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.main.repository_url}:${var.ecr_image_tag}"

  memory_size   = var.lambda_memory_size
  timeout       = var.lambda_timeout
  architectures = [var.lambda_architecture]

  environment {
    variables = {
      LOG_LEVEL               = "INFO"
      ENVIRONMENT             = var.environment
      API_VERSION             = "1.0.0"
      PYTHONDONTWRITEBYTECODE = "1"
      PYTHONUNBUFFERED        = "1"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_cloudwatch_log_group.lambda,
  ]

  tags = local.common_tags

  lifecycle {
    ignore_changes = [image_uri]
  }
}

# API Gateway HTTP API
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project_name}-${var.environment}-api"
  protocol_type = "HTTP"
  description   = "HTTP API for ${var.project_name}"

  cors_configuration {
    allow_credentials = false
    allow_headers     = var.api_cors_allow_headers
    allow_methods     = var.api_cors_allow_methods
    allow_origins     = var.api_cors_allow_origins
    expose_headers    = ["Content-Length", "Date"]
    max_age           = 300
  }

  tags = local.common_tags
}

# API Gateway Integration with Lambda
resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.main.id

  integration_uri    = aws_lambda_function.main.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

# API Gateway Routes
resource "aws_apigatewayv2_route" "hello" {
  api_id = aws_apigatewayv2_api.main.id

  route_key = "GET /hello"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "echo" {
  api_id = aws_apigatewayv2_api.main.id

  route_key = "GET /echo"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "health" {
  api_id = aws_apigatewayv2_api.main.id

  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# API Gateway Stage
resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.main.id

  name        = "$default"
  auto_deploy = true

  tags = local.common_tags
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}