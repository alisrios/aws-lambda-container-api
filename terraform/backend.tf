# Backend configuration for Terraform state
# This stores the Terraform state in S3 with versioning for basic state protection

terraform {
  backend "s3" {
    bucket  = "bucket-state-locking"
    key     = "lambda-container-api/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}
