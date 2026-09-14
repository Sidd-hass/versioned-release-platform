# S3 Remote Backend Configuration
# Ensure you run the bootstrap scripts first to create the state bucket and lock table.
terraform {
  backend "s3" {
    bucket         = "app-versioned-release-platform-tfstate"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "app-versioned-release-platform-tflocks"
    encrypt        = true
  }
}
