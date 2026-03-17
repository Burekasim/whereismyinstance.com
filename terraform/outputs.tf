output "cloudfront_domain" {
  description = "CloudFront distribution domain name"
  value       = data.aws_cloudfront_distribution.cdn.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (used for cache invalidation in CI)"
  value       = data.aws_cloudfront_distribution.cdn.id
}

output "api_gateway_endpoint" {
  description = "Raw API Gateway endpoint (traffic goes through CloudFront /api/*)"
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "lambda_function_name" {
  description = "Lambda function name (used in update-function-code CI step)"
  value       = aws_lambda_function.api.function_name
}

output "frontend_bucket" {
  description = "S3 bucket name for frontend files"
  value       = aws_s3_bucket.frontend.id
}
