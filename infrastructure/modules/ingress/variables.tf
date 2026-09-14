variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "oidc_provider_arn" {
  description = "IAM OIDC Provider ARN from EKS cluster"
  type        = string
}

variable "oidc_provider_url" {
  description = "IAM OIDC Provider URL from EKS cluster"
  type        = string
}
