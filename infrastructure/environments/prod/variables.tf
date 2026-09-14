variable "aws_region" {
  description = "AWS region for production resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment identifier"
  type        = string
  default     = "prod"
}

variable "cluster_name" {
  description = "EKS Cluster Name for Production"
  type        = string
  default     = "prod-versioned-release-eks"
}

variable "kubernetes_version" {
  description = "Kubernetes Version for EKS"
  type        = string
  default     = "1.29"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.1.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.1.1.0/24", "10.1.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.1.101.0/24", "10.1.102.0/24"]
}

variable "availability_zones" {
  description = "Availability Zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "node_instance_types" {
  description = "Instance type for single EC2 worker node"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "desired_size" {
  description = "Desired worker node count"
  type        = number
  default     = 1
}

variable "min_size" {
  description = "Minimum worker node count"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum worker node count"
  type        = number
  default     = 1
}

variable "app_s3_bucket_name" {
  description = "Globally unique S3 bucket name for production application pod storage"
  type        = string
  default     = "prod-app-versioned-release-pod-storage"
}

variable "pod_service_account_name" {
  description = "Name of Kubernetes ServiceAccount for pod S3 permissions"
  type        = string
  default     = "app-s3-sa"
}

variable "pod_service_account_namespace" {
  description = "Namespace of Kubernetes ServiceAccount for pod S3 permissions"
  type        = string
  default     = "default"
}
