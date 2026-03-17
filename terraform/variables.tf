variable "aws_region" {
  description = "AWS region for all resources except CloudFront ACM cert (always us-east-1)"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short name used as a prefix for all resources"
  type        = string
  default     = "whereismyinstance"
}

variable "cloudfront_distribution_id" {
  description = "ID of the existing CloudFront distribution (e.g. E28DZQE1EZUNPH)"
  type        = string
}

variable "lambda_memory_mb" {
  description = "Lambda memory allocation in MB"
  type        = number
  default     = 512
}

variable "lambda_timeout_sec" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 15
}
