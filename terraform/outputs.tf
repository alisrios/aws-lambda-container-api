output "api_gateway_url" {
  description = "URL do API Gateway"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "api_gateway_id" {
  description = "ID do API Gateway"
  value       = aws_apigatewayv2_api.main.id
}

output "hello_endpoint_url" {
  description = "URL completa do endpoint /hello"
  value       = "${aws_apigatewayv2_api.main.api_endpoint}/hello"
}

output "echo_endpoint_url" {
  description = "URL completa do endpoint /echo"
  value       = "${aws_apigatewayv2_api.main.api_endpoint}/echo"
}

output "lambda_function_name" {
  description = "Nome da função Lambda"
  value       = aws_lambda_function.main.function_name
}

output "lambda_function_arn" {
  description = "ARN da função Lambda"
  value       = aws_lambda_function.main.arn
}

output "lambda_invoke_arn" {
  description = "ARN de invocação da função Lambda"
  value       = aws_lambda_function.main.invoke_arn
}

output "ecr_repository_url" {
  description = "URL do repositório ECR"
  value       = data.aws_ecr_repository.main.repository_url
}

output "ecr_repository_name" {
  description = "Nome do repositório ECR"
  value       = data.aws_ecr_repository.main.name
}

output "ecr_repository_arn" {
  description = "ARN do repositório ECR"
  value       = data.aws_ecr_repository.main.arn
}

output "cloudwatch_log_group_name" {
  description = "Nome do grupo de logs CloudWatch da Lambda"
  value       = aws_cloudwatch_log_group.lambda.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN do grupo de logs CloudWatch da Lambda"
  value       = aws_cloudwatch_log_group.lambda.arn
}

output "api_gateway_log_group_name" {
  description = "Nome do grupo de logs CloudWatch do API Gateway"
  value       = aws_cloudwatch_log_group.api_gateway.name
}

output "deployment_info" {
  description = "Informações resumidas do deployment"
  value = {
    project_name    = var.project_name
    environment     = var.environment
    aws_region      = var.aws_region
    api_url         = aws_apigatewayv2_api.main.api_endpoint
    lambda_function = aws_lambda_function.main.function_name
    ecr_repository  = data.aws_ecr_repository.main.name
  }
}

output "health_endpoint_url" {
  description = "URL completa do endpoint /health"
  value       = "${aws_apigatewayv2_api.main.api_endpoint}/health"
}

output "cloudwatch_dashboard_url" {
  description = "URL do CloudWatch Dashboard"
  value       = "https://${local.region}.console.aws.amazon.com/cloudwatch/home?region=${local.region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "sns_topic_arn" {
  description = "ARN do tópico SNS para alertas"
  value       = aws_sns_topic.alerts.arn
}

output "monitoring_info" {
  description = "Informações de monitoramento"
  value = {
    dashboard_name = aws_cloudwatch_dashboard.main.dashboard_name
    dashboard_url  = "https://${local.region}.console.aws.amazon.com/cloudwatch/home?region=${local.region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
    sns_topic_arn  = aws_sns_topic.alerts.arn
    alarms = {
      lambda_errors      = aws_cloudwatch_metric_alarm.lambda_errors.alarm_name
      lambda_duration    = aws_cloudwatch_metric_alarm.lambda_duration.alarm_name
      lambda_cold_starts = aws_cloudwatch_metric_alarm.lambda_cold_starts.alarm_name
      lambda_throttles   = aws_cloudwatch_metric_alarm.lambda_throttles.alarm_name
      lambda_memory      = aws_cloudwatch_metric_alarm.lambda_memory.alarm_name
      api_4xx_errors     = aws_cloudwatch_metric_alarm.api_gateway_4xx.alarm_name
      api_5xx_errors     = aws_cloudwatch_metric_alarm.api_gateway_5xx.alarm_name
      api_latency        = aws_cloudwatch_metric_alarm.api_gateway_latency.alarm_name
    }
  }
}

output "lambda_alias_arn" {
  description = "ARN do alias da função Lambda"
  value       = aws_lambda_alias.main.arn
}

output "lambda_performance_config" {
  description = "Configurações de performance da função Lambda"
  value = {
    memory_size_mb            = aws_lambda_function.main.memory_size
    timeout_seconds           = aws_lambda_function.main.timeout
    architecture              = aws_lambda_function.main.architectures[0]
    reserved_concurrency      = aws_lambda_function.main.reserved_concurrent_executions
    provisioned_concurrency   = var.lambda_provisioned_concurrency
    dead_letter_queue_enabled = var.lambda_dead_letter_queue_enabled
    tracing_enabled           = aws_lambda_function.main.tracing_config[0].mode == "Active"
  }
}

output "lambda_dlq_url" {
  description = "URL da Dead Letter Queue (se habilitada)"
  value       = var.lambda_dead_letter_queue_enabled ? aws_sqs_queue.lambda_dlq[0].url : null
}

output "api_throttle_settings" {
  description = "Configurações de throttling do API Gateway"
  value = {
    burst_limit = var.api_throttle_burst_limit
    rate_limit  = var.api_throttle_rate_limit
  }
}

output "performance_summary" {
  description = "Resumo das otimizações de performance implementadas"
  value = {
    lambda_optimizations = {
      memory_mb               = var.lambda_memory_size
      timeout_seconds         = var.lambda_timeout
      architecture            = var.lambda_architecture
      reserved_concurrency    = var.lambda_reserved_concurrency
      provisioned_concurrency = var.lambda_provisioned_concurrency
      dead_letter_queue       = var.lambda_dead_letter_queue_enabled
      x_ray_tracing           = true
      max_retry_attempts      = var.lambda_max_retry_attempts
    }
    api_gateway_optimizations = {
      throttle_burst_limit = var.api_throttle_burst_limit
      throttle_rate_limit  = var.api_throttle_rate_limit
      cors_enabled         = true
      access_logging       = true
    }
    docker_optimizations = {
      multi_stage_build     = true
      python_bytecode_cache = true
      minimal_dependencies  = true
      security_scanning     = true
    }
    monitoring_enhancements = {
      enhanced_alarms       = true
      performance_dashboard = true
      cold_start_monitoring = true
      memory_monitoring     = true
      throttle_monitoring   = true
    }
  }
}
