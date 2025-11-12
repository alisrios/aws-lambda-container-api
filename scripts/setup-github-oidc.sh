#!/bin/bash

# GitHub OIDC Setup Script for AWS Lambda Terraform Project
# This script sets up GitHub OIDC provider and IAM roles for GitHub Actions

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install Terraform first."
        exit 1
    fi
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to check if terraform.tfvars exists
check_terraform_vars() {
    print_status "Checking Terraform variables..."
    
    if [ ! -f "terraform.tfvars" ]; then
        print_warning "terraform.tfvars not found. Creating from example..."
        if [ -f "terraform.tfvars.example" ]; then
            cp terraform.tfvars.example terraform.tfvars
            print_warning "Please edit terraform.tfvars with your specific values before continuing."
            print_warning "Required variables: github_repository, project_name, environment, etc."
            read -p "Press Enter to continue after editing terraform.tfvars..."
        else
            print_error "terraform.tfvars.example not found. Please create terraform.tfvars manually."
            exit 1
        fi
    fi
    
    print_success "Terraform variables file found"
}

# Function to initialize Terraform
init_terraform() {
    print_status "Initializing Terraform..."
    
    if terraform init; then
        print_success "Terraform initialized successfully"
    else
        print_error "Failed to initialize Terraform"
        exit 1
    fi
}

# Function to validate Terraform configuration
validate_terraform() {
    print_status "Validating Terraform configuration..."
    
    if terraform validate; then
        print_success "Terraform configuration is valid"
    else
        print_error "Terraform configuration validation failed"
        exit 1
    fi
}

# Function to plan Terraform changes
plan_terraform() {
    print_status "Planning Terraform changes..."
    
    if terraform plan -out=tfplan; then
        print_success "Terraform plan completed successfully"
        print_status "Review the plan above. The following resources will be created:"
        echo "  - GitHub OIDC Identity Provider"
        echo "  - IAM Role for GitHub Actions"
        echo "  - IAM Policies for ECR, Lambda, and Terraform state management"
    else
        print_error "Terraform plan failed"
        exit 1
    fi
}

# Function to apply Terraform changes
apply_terraform() {
    print_status "Applying Terraform changes..."
    
    read -p "Do you want to apply these changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if terraform apply tfplan; then
            print_success "Terraform apply completed successfully"
        else
            print_error "Terraform apply failed"
            exit 1
        fi
    else
        print_warning "Terraform apply cancelled by user"
        exit 0
    fi
}

# Function to display outputs
show_outputs() {
    print_status "Retrieving Terraform outputs..."
    
    echo
    print_success "GitHub OIDC setup completed successfully!"
    echo
    print_status "Important outputs for GitHub Actions configuration:"
    
    GITHUB_ROLE_ARN=$(terraform output -raw github_actions_role_arn 2>/dev/null || echo "Not available")
    OIDC_PROVIDER_ARN=$(terraform output -raw github_oidc_provider_arn 2>/dev/null || echo "Not available")
    
    echo "  GitHub Actions Role ARN: $GITHUB_ROLE_ARN"
    echo "  OIDC Provider ARN: $OIDC_PROVIDER_ARN"
    echo
    print_status "Next steps:"
    echo "1. Add the following secrets to your GitHub repository:"
    echo "   - AWS_ROLE_ARN: $GITHUB_ROLE_ARN"
    echo "   - AWS_REGION: $(aws configure get region || echo 'your-aws-region')"
    echo
    echo "2. Use the following in your GitHub Actions workflow:"
    echo "   - name: Configure AWS credentials"
    echo "     uses: aws-actions/configure-aws-credentials@v4"
    echo "     with:"
    echo "       role-to-assume: \${{ secrets.AWS_ROLE_ARN }}"
    echo "       aws-region: \${{ secrets.AWS_REGION }}"
    echo
}

# Function to cleanup temporary files
cleanup() {
    print_status "Cleaning up temporary files..."
    rm -f tfplan
}

# Main execution
main() {
    print_status "Starting GitHub OIDC setup for AWS Lambda project"
    echo
    
    # Change to the script's directory (terraform root)
    cd "$(dirname "$0")/.."
    
    check_prerequisites
    check_terraform_vars
    init_terraform
    validate_terraform
    plan_terraform
    apply_terraform
    show_outputs
    cleanup
    
    print_success "GitHub OIDC setup completed successfully!"
}

# Trap to cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"
