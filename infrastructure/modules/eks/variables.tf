variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS control plane"
  type        = string
  default     = "1.29"
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for cluster VPC config"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for worker node placement"
  type        = list(string)
}

variable "instance_types" {
  description = "EC2 Instance types for the node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "capacity_type" {
  description = "Capacity type for node group (ON_DEMAND or SPOT)"
  type        = string
  default     = "ON_DEMAND"
}

variable "desired_size" {
  description = "Desired number of worker nodes (Default: 1)"
  type        = number
  default     = 1
}

variable "min_size" {
  description = "Minimum number of worker nodes (Default: 1)"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum number of worker nodes (Default: 1)"
  type        = number
  default     = 1
}
