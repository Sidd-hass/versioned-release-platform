# S3 Remote Backend Configuration for Production Environment
terraform {
  backend "s3" {
    bucket         = "app-versioned-release-platform-tfstate"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "app-versioned-release-platform-tflocks"
    encrypt        = true
  }
}
