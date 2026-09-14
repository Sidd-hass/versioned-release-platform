terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "VersionedReleasePlatform"
      ManagedBy   = "Terraform"
    }
  }
}

# -----------------------------------------------------------------------------
# Module 1: Networking (VPC, Subnets, NAT Gateway)
# -----------------------------------------------------------------------------
module "vpc" {
  source = "../../modules/vpc"

  cluster_name         = var.cluster_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
}

# -----------------------------------------------------------------------------
# Module 2: EKS Cluster & 1-Node EC2 Managed Node Group
# -----------------------------------------------------------------------------
module "eks" {
  source = "../../modules/eks"

  cluster_name       = var.cluster_name
  environment        = var.environment
  kubernetes_version = var.kubernetes_version
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
  instance_types     = var.node_instance_types
  desired_size       = 1
  min_size           = 1
  max_size           = 1
}

# -----------------------------------------------------------------------------
# Module 3: IRSA for Pod S3 Access
# -----------------------------------------------------------------------------
module "irsa_s3" {
  source = "../../modules/irsa_s3"

  cluster_name              = var.cluster_name
  environment               = var.environment
  s3_bucket_name            = var.app_s3_bucket_name
  oidc_provider_arn         = module.eks.oidc_provider_arn
  oidc_provider_url         = module.eks.oidc_provider_url
  service_account_name      = var.pod_service_account_name
  service_account_namespace = var.pod_service_account_namespace
}

# -----------------------------------------------------------------------------
# Module 4: Ingress IAM (AWS Load Balancer Controller IRSA)
# -----------------------------------------------------------------------------
module "ingress" {
  source = "../../modules/ingress"

  cluster_name      = var.cluster_name
  environment       = var.environment
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_provider_url = module.eks.oidc_provider_url
}
