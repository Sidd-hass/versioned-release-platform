variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "Globally unique S3 bucket name for pod storage"
  type        = string
}

variable "oidc_provider_arn" {
  description = "IAM OIDC Provider ARN from EKS cluster"
  type        = string
}

variable "oidc_provider_url" {
  description = "IAM OIDC Provider URL from EKS cluster"
  type        = string
}

variable "service_account_name" {
  description = "Kubernetes ServiceAccount name for the pod"
  type        = string
  default     = "app-s3-sa"
}

variable "service_account_namespace" {
  description = "Kubernetes namespace for the ServiceAccount"
  type        = string
  default     = "default"
}

variable "force_destroy" {
  description = "Whether to allow force deletion of application S3 bucket"
  type        = bool
  default     = false
}
