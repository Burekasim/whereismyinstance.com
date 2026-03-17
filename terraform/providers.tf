terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    # Configure via -backend-config flags or environment variables, e.g.:
    #   terraform init \
    #     -backend-config="bucket=my-tf-state" \
    #     -backend-config="key=whereismyinstance/terraform.tfstate" \
    #     -backend-config="region=us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# us-east-1 is required for ACM certs used by CloudFront
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
