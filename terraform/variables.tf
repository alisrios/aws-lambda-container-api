variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "lambda-container-api"
}

variable "environment" {
  description = "Ambiente de deployment"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "Região AWS"
  type        = string
  default     = "us-east-1"
}

variable "lambda_memory_size" {
  description = "Quantidade de memória para a função Lambda (MB)"
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Timeout da função Lambda (segundos)"
  type        = number
  default     = 30
}

variable "ecr_image_tag" {
  description = "Tag da imagem ECR para deployment"
  type        = string
  default     = "latest"
}

variable "api_cors_allow_origins" {
  description = "Origins permitidas para CORS"
  type        = list(string)
  default     = ["*"]
}

variable "api_cors_allow_methods" {
  description = "Métodos HTTP permitidos para CORS"
  type        = list(string)
  default     = ["GET", "POST", "OPTIONS"]
}

variable "api_cors_allow_headers" {
  description = "Headers permitidos para CORS"
  type        = list(string)
  default     = ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Request-ID"]
}

# Performance optimization variables
variable "lambda_reserved_concurrency" {
  description = "Número de execuções concorrentes reservadas para a função Lambda"
  type        = number
  default     = null
}

variable "lambda_provisioned_concurrency" {
  description = "Número de execuções provisionadas para reduzir cold starts"
  type        = number
  default     = null
}

variable "lambda_architecture" {
  description = "Arquitetura da função Lambda (x86_64 ou arm64)"
  type        = string
  default     = "x86_64"
  validation {
    condition     = contains(["x86_64", "arm64"], var.lambda_architecture)
    error_message = "Lambda architecture must be either x86_64 or arm64."
  }
}

variable "lambda_dead_letter_queue_enabled" {
  description = "Habilitar Dead Letter Queue para a função Lambda"
  type        = bool
  default     = true
}

variable "lambda_max_retry_attempts" {
  description = "Número máximo de tentativas de retry para a função Lambda"
  type        = number
  default     = 2
}

variable "api_throttle_burst_limit" {
  description = "Limite de burst para throttling do API Gateway"
  type        = number
  default     = 5000
}

variable "api_throttle_rate_limit" {
  description = "Limite de rate para throttling do API Gateway"
  type        = number
  default     = 2000
}