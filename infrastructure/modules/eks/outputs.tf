output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "cluster_endpoint" {
  description = "EKS cluster control plane API endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.main.certificate_authority[0].data
}

output "cluster_arn" {
  description = "ARN of the EKS cluster"
  value       = aws_eks_cluster.main.arn
}

output "oidc_provider_arn" {
  description = "ARN of the IAM OIDC Provider for IRSA"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "oidc_provider_url" {
  description = "URL of the IAM OIDC Provider for IRSA"
  value       = aws_iam_openid_connect_provider.eks.url
}

output "node_group_arn" {
  description = "ARN of the single EC2 Managed Node Group"
  value       = aws_eks_node_group.main.arn
}
