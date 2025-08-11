# GitHub OIDC Provider and IAM Role for GitHub Actions
# This configuration allows GitHub Actions to assume AWS roles without storing long-term credentials

# Data source to get GitHub's OIDC thumbprint
data "tls_certificate" "github" {
  url = "https://token.actions.githubusercontent.com"
}

# GitHub OIDC Identity Provider
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  thumbprint_list = [
    data.tls_certificate.github.certificates[0].sha1_fingerprint,
  ]

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-github-oidc"
  })
}

# IAM Role for GitHub Actions
resource "aws_iam_role" "github_actions" {
  name = "${var.project_name}-${var.environment}-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = [
              "repo:${var.github_repository}:ref:refs/heads/main",
              "repo:${var.github_repository}:ref:refs/heads/develop",
              "repo:${var.github_repository}:pull_request"
            ]
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-github-actions-role"
  })
}

# IAM Policy for GitHub Actions - ECR permissions
resource "aws_iam_role_policy" "github_actions_ecr" {
  name = "${var.project_name}-${var.environment}-github-actions-ecr-policy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:DescribeRepositories",
          "ecr:DescribeImages",
          "ecr:ListImages",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = [
          "arn:aws:ecr:${local.region}:${local.account_id}:repository/${var.project_name}-${var.environment}",
          "*"
        ]
      }
    ]
  })
}

# IAM Policy for GitHub Actions - Lambda permissions
resource "aws_iam_role_policy" "github_actions_lambda" {
  name = "${var.project_name}-${var.environment}-github-actions-lambda-policy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",
          "lambda:ListVersionsByFunction",
          "lambda:PublishVersion",
          "lambda:UpdateAlias",
          "lambda:GetAlias",
          "lambda:InvokeFunction"
        ]
        Resource = [
          "arn:aws:lambda:${local.region}:${local.account_id}:function:${var.project_name}-${var.environment}",
          "arn:aws:lambda:${local.region}:${local.account_id}:function:${var.project_name}-${var.environment}:*"
        ]
      }
    ]
  })
}

# IAM Policy for GitHub Actions - Terraform state management
resource "aws_iam_role_policy" "github_actions_terraform" {
  name = "${var.project_name}-${var.environment}-github-actions-terraform-policy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.terraform_state_bucket}",
          "arn:aws:s3:::${var.terraform_state_bucket}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem"
        ]
        Resource = "arn:aws:dynamodb:${local.region}:${local.account_id}:table/terraform-state-lock"
      }
    ]
  })
}

# IAM Policy for GitHub Actions - General AWS permissions
resource "aws_iam_role_policy" "github_actions_general" {
  name = "${var.project_name}-${var.environment}-github-actions-general-policy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          # IAM permissions for managing roles and policies
          "iam:GetRole",
          "iam:GetRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:ListPolicyVersions",
          "iam:PassRole",
          "iam:CreateRole",
          "iam:UpdateRole",
          "iam:DeleteRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:CreateOpenIDConnectProvider",
          "iam:DeleteOpenIDConnectProvider",
          "iam:GetOpenIDConnectProvider",
          "iam:ListOpenIDConnectProviders",
          "iam:TagOpenIDConnectProvider",
          "iam:UntagOpenIDConnectProvider",
          
          # ECR permissions
          "ecr:CreateRepository",
          "ecr:DeleteRepository",
          "ecr:DescribeRepositories",
          "ecr:PutLifecyclePolicy",
          "ecr:DeleteLifecyclePolicy",
          "ecr:GetLifecyclePolicy",
          "ecr:PutRepositoryPolicy",
          "ecr:DeleteRepositoryPolicy",
          "ecr:GetRepositoryPolicy",
          "ecr:TagResource",
          "ecr:UntagResource",
          "ecr:ListTagsForResource",
          
          # API Gateway permissions
          "apigateway:GET",
          "apigateway:POST",
          "apigateway:PUT",
          "apigateway:DELETE",
          "apigateway:PATCH",
          "apigateway:TagResource",
          "apigateway:UntagResource",
          
          # CloudWatch permissions
          "logs:CreateLogGroup",
          "logs:DeleteLogGroup",
          "logs:DescribeLogGroups",
          "logs:PutRetentionPolicy",
          "logs:TagLogGroup",
          "logs:UntagLogGroup",
          "logs:ListTagsForResource",
          "logs:TagResource",
          "logs:UntagResource",
          "cloudwatch:PutMetricAlarm",
          "cloudwatch:DeleteAlarms",
          "cloudwatch:DescribeAlarms",
          "cloudwatch:PutDashboard",
          "cloudwatch:DeleteDashboards",
          "cloudwatch:GetDashboard",
          "cloudwatch:ListDashboards",
          "cloudwatch:TagResource",
          "cloudwatch:UntagResource",
          "cloudwatch:ListTagsForResource",
          
          # SNS permissions
          "sns:CreateTopic",
          "sns:DeleteTopic",
          "sns:GetTopicAttributes",
          "sns:SetTopicAttributes",
          "sns:TagResource",
          "sns:UntagResource",
          "sns:ListTagsForResource",
          "sns:Subscribe",
          "sns:Unsubscribe",
          
          # SQS permissions (for DLQ)
          "sqs:CreateQueue",
          "sqs:DeleteQueue",
          "sqs:GetQueueAttributes",
          "sqs:SetQueueAttributes",
          "sqs:TagQueue",
          "sqs:UntagQueue",
          "sqs:ListQueueTags",
          
          # General permissions
          "sts:GetCallerIdentity",
          "sts:AssumeRole"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:CreateFunction",
          "lambda:DeleteFunction",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:GetFunction",
          "lambda:ListFunctions",
          "lambda:TagResource",
          "lambda:UntagResource",
          "lambda:AddPermission",
          "lambda:RemovePermission",
          "lambda:GetPolicy",
          "lambda:CreateAlias",
          "lambda:DeleteAlias",
          "lambda:UpdateAlias",
          "lambda:GetAlias",
          "lambda:ListAliases",
          "lambda:PutProvisionedConcurrencyConfig",
          "lambda:DeleteProvisionedConcurrencyConfig",
          "lambda:GetProvisionedConcurrencyConfig"
        ]
        Resource = [
          "arn:aws:lambda:${local.region}:${local.account_id}:function:${local.lambda_function_name}*"
        ]
      }
    ]
  })
}

# Output the role ARN for GitHub Actions configuration
output "github_actions_role_arn" {
  description = "ARN of the IAM role for GitHub Actions OIDC"
  value       = aws_iam_role.github_actions.arn
}

output "github_oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider"
  value       = aws_iam_openid_connect_provider.github.arn
}
