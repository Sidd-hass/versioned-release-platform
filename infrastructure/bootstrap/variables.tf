variable "aws_region" {
  description = "AWS region for bootstrap infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment tag name"
  type        = string
  default     = "global"
}

variable "state_bucket_name" {
  description = "Globally unique S3 bucket name for storing Terraform remote backend state"
  type        = string
  default     = "app-versioned-release-platform-tfstate"
}

variable "lock_table_name" {
  description = "DynamoDB table name for Terraform backend state locking"
  type        = string
  default     = "app-versioned-release-platform-tflocks"
}

variable "force_destroy" {
  description = "Whether to allow force destroying S3 bucket on cleanup"
  type        = bool
  default     = false
}
