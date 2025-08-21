# Backend configuration for Terraform state
# This stores the Terraform state in S3

terraform {
  backend "s3" {
    # S3 bucket for Terraform state
    bucket = "bucket-state-locking"
    key    = "lambda-container-api/terraform.tfstate"
    region = "us-east-1"
    #use_lockfile = true 
  }
}
