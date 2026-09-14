terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# -----------------------------------------------------------------------------
# S3 Bucket for Pod Storage
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "app_storage" {
  bucket        = var.s3_bucket_name
  force_destroy = var.force_destroy

  tags = {
    Name        = var.s3_bucket_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# S3 Public Access Block (Security Best Practice)
resource "aws_s3_bucket_public_access_block" "app_storage_public_block" {
  bucket                  = aws_s3_bucket.app_storage.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Server Side Encryption for Pod S3 Bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "app_storage_crypto" {
  bucket = aws_s3_bucket.app_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# -----------------------------------------------------------------------------
# IAM Policy for Pod S3 CRUD Operations
# -----------------------------------------------------------------------------
resource "aws_iam_policy" "pod_s3_access" {
  name        = "${var.cluster_name}-pod-s3-policy"
  description = "IAM policy granting scoped S3 access to EKS pods"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.app_storage.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.app_storage.arn}/*"
        ]
      }
    ]
  })

  tags = {
    Name        = "${var.cluster_name}-pod-s3-policy"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# -----------------------------------------------------------------------------
# IRSA Role (IAM Role for Service Accounts)
# -----------------------------------------------------------------------------
locals {
  oidc_url_stripped = replace(var.oidc_provider_url, "https://", "")
}

resource "aws_iam_role" "pod_s3_irsa" {
  name = "${var.cluster_name}-pod-s3-irsa-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${local.oidc_url_stripped}:sub" = "system:serviceaccount:${var.service_account_namespace}:${var.service_account_name}"
            "${local.oidc_url_stripped}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "${var.cluster_name}-pod-s3-irsa-role"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_iam_role_policy_attachment" "pod_s3_irsa_attach" {
  role       = aws_iam_role.pod_s3_irsa.name
  policy_arn = aws_iam_policy.pod_s3_access.arn
}
