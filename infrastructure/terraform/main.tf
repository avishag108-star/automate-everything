# ─────────────────────────────────────────────────────────────────────
# StatusWatch — Infrastructure as Code
# Terraform: VPC + EC2 (k3s) on AWS Free Tier
# Cost: ~$0/month (t2.micro free tier) vs ~$150/month for EKS
# ─────────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state — prevents conflicts between team members
  backend "s3" {
    bucket         = "statuswatch-tf-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "statuswatch-tf-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "statuswatch"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
