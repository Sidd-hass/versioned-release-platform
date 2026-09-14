output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "eks_cluster_name" {
  description = "EKS Cluster Name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS Cluster API Endpoint"
  value       = module.eks.cluster_endpoint
}

output "eks_oidc_provider_url" {
  description = "EKS Cluster OIDC Issuer URL"
  value       = module.eks.oidc_provider_url
}

output "pod_s3_bucket_name" {
  description = "Application S3 Bucket Name"
  value       = module.irsa_s3.s3_bucket_name
}

output "pod_s3_irsa_role_arn" {
  description = "IAM Role ARN for Pod S3 ServiceAccount"
  value       = module.irsa_s3.irsa_role_arn
}

output "alb_controller_irsa_role_arn" {
  description = "IAM Role ARN for AWS Load Balancer Controller"
  value       = module.ingress.alb_controller_role_arn
}

output "kubeconfig_update_command" {
  description = "Command to update local kubeconfig"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
