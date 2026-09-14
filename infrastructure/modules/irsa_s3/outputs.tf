output "s3_bucket_name" {
  description = "The name of the application S3 bucket created for pod access"
  value       = aws_s3_bucket.app_storage.id
}

output "s3_bucket_arn" {
  description = "The ARN of the application S3 bucket"
  value       = aws_s3_bucket.app_storage.arn
}

output "irsa_role_arn" {
  description = "The IAM Role ARN to annotate on the Kubernetes ServiceAccount"
  value       = aws_iam_role.pod_s3_irsa.arn
}

output "service_account_annotation" {
  description = "Helper snippet to add to Kubernetes ServiceAccount YAML"
  value       = "eks.amazonaws.com/role-arn: ${aws_iam_role.pod_s3_irsa.arn}"
}
