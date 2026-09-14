# EKS Infrastructure Terraform Setup

This directory contains modularized Terraform scripts to deploy single-node Amazon EKS clusters inside a custom multi-AZ VPC with Pod-level S3 access (via IRSA) and AWS Load Balancer Controller (Ingress) support across **Dev** and **Prod** environments.

## Architecture Directory Overview

```text
infrastructure/
├── bootstrap/                     # Step 1: Creates S3 state bucket & DynamoDB lock table
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── modules/                       # Reusable infrastructure modules
│   ├── vpc/                       # VPC, 2 Public & 2 Private Subnets, IGW, NAT Gateway, K8s tags
│   ├── eks/                       # EKS Cluster, OIDC Provider, 1 EC2 Managed Node Group
│   ├── irsa_s3/                   # Pod S3 bucket, IAM policy & IRSA Role for Pod ServiceAccount
│   └── ingress/                   # IAM Policy & IRSA Role for AWS Load Balancer Controller
└── environments/
    ├── dev/                       # Dev Environment (State key: dev/terraform.tfstate)
    │   ├── backend.tf
    │   ├── main.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── terraform.tfvars.example
    └── prod/                      # Prod Environment (State key: prod/terraform.tfstate)
        ├── backend.tf
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── terraform.tfvars.example
```

---

## Deployment Steps

> [!CAUTION]
> Running `terraform apply` will incur costs in your AWS account. As requested, **do not run `terraform apply`** unless you are ready to provision live AWS resources.

### Step 1: Remote Backend Bootstrap (Run First)

1. Navigate to the bootstrap directory:
   ```bash
   cd infrastructure/bootstrap
   ```
2. Initialize and apply bootstrap resources (creates remote state S3 bucket & DynamoDB lock table):
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

### Step 2: Provision Environment (Dev or Prod)

#### For Dev Environment:
```bash
cd infrastructure/environments/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

#### For Prod Environment:
```bash
cd infrastructure/environments/prod
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

---

## Post-Provisioning Usage Guide

### 1. Connecting kubectl to your EKS Cluster
- **Dev**:
  ```bash
  aws eks update-kubeconfig --region us-east-1 --name dev-versioned-release-eks
  ```
- **Prod**:
  ```bash
  aws eks update-kubeconfig --region us-east-1 --name prod-versioned-release-eks
  ```

### 2. Installing AWS Load Balancer Controller (Ingress Support)
```bash
# Add EKS Helm repository
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install AWS Load Balancer Controller using the output IRSA Role ARN
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=<CLUSTER_NAME> \
  --set serviceAccount.create=true \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set serviceAccount.annotations.eks\.amazonaws\.com/role-arn=<OUTPUT_ALB_CONTROLLER_IRSA_ROLE_ARN>
```

### 3. Binding Pod S3 Permissions (IRSA) to Kubernetes Pods

Create a Kubernetes `ServiceAccount` in your deployment YAML with the IRSA annotation output by Terraform:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-s3-sa
  namespace: default
  annotations:
    eks.amazonaws.com/role-arn: <OUTPUT_POD_S3_IRSA_ROLE_ARN>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: versioned-app
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: versioned-app
  template:
    metadata:
      labels:
        app: versioned-app
    spec:
      serviceAccountName: app-s3-sa
      containers:
        - name: app
          image: your-app-image:latest
          env:
            - name: S3_BUCKET_NAME
              value: "dev-app-versioned-release-pod-storage" # Or prod bucket name
            - name: AWS_REGION
              value: "us-east-1"
```
