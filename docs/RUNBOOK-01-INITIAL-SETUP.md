# Runbook 01: Initial Setup and Prerequisites

**Purpose**: Set up your environment and prepare for using the ai-app repository  
**Audience**: DevOps Engineers, Platform Administrators  
**Duration**: 30-45 minutes  
**Prerequisites**: AWS Account, GitHub Account, Basic Linux knowledge

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Understanding](#architecture-understanding)
3. [Prerequisites Checklist](#prerequisites-checklist)
4. [Initial Setup Steps](#initial-setup-steps)
5. [Validation](#validation)

---

## Overview

### What is This Repository?

The `ai-app` repository is a **GitOps-style application repository** that contains:
- Application source code (Backend FastAPI + Frontend Next.js)
- Docker build configurations
- Kubernetes deployment manifests (Helm charts)
- Jenkins CI/CD pipeline definition (Jenkinsfile)

### How Does It Work?

```
Developer → Git Push → GitHub Repository → Jenkins Pipeline → Build → Deploy to EKS
                                              ↓
                                         Jenkinsfile
                                              ↓
                                    1. Test Code
                                    2. Build Docker Images
                                    3. Push to ECR
                                    4. Deploy via Helm to EKS
```

### Repository vs Jenkins Server

**Important Distinction**:
- **This Repository**: Contains application code and deployment definitions
- **Jenkins Server**: Separate permanent server that reads this repository and executes deployments
- **Relationship**: Jenkins pulls code from this repo and executes the Jenkinsfile

---

## Architecture Understanding

### Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│                        (ai-app)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Backend    │  │   Frontend   │  │  Helm Chart  │     │
│  │   (FastAPI)  │  │  (Next.js)   │  │ (K8s Manifests)│   │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                    ┌──────────────┐                         │
│                    │  Jenkinsfile │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    (Git Clone/Pull)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Jenkins Server                            │
│                  (Permanent Server)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Jenkins Pipeline Job: ai-app-deploy                 │  │
│  │  - Reads Jenkinsfile from repository                 │  │
│  │  - Executes build and deployment steps               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    (Docker Build & Push)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    AWS ECR                                   │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Backend Image│  │Frontend Image│                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    (Helm Deploy)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    AWS EKS Cluster                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Backend Pods  │  │Frontend Pods │  │  ALB Ingress │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites Checklist

### ✅ Checkpoint 1.1: AWS Infrastructure

**Required AWS Resources**:

| Resource | Purpose | How to Verify |
|----------|---------|---------------|
| EKS Cluster | Kubernetes cluster for running apps | `aws eks describe-cluster --name rdh-eks-cluster` |
| ECR Repositories | Store Docker images | `aws ecr describe-repositories` |
| VPC with Subnets | Network infrastructure | `aws ec2 describe-vpcs` |
| IAM Roles | Permissions for Jenkins/EKS | `aws iam list-roles` |
| ACM Certificate | SSL/TLS for HTTPS | `aws acm list-certificates` |
| Secrets Manager | Store API keys | `aws secretsmanager list-secrets` |

**Verification Commands**:

```bash
# 1. Check EKS Cluster
aws eks describe-cluster --name rdh-eks-cluster --region us-east-1 \
  --query 'cluster.status' --output text
# Expected: ACTIVE

# 2. Check ECR Repositories
aws ecr describe-repositories --region us-east-1 \
  --repository-names ai-app-backend ai-app-frontend
# Expected: Both repositories exist

# 3. Check VPC
aws ec2 describe-vpcs --region us-east-1 \
  --query 'Vpcs[?Tags[?Key==`Name`&&contains(Value,`rdh`)]]' --output table
# Expected: VPC with rdh in name

# 4. Check ACM Certificate
aws acm list-certificates --region us-east-1 \
  --query 'CertificateSummaryList[?DomainName==`*.rdhcloudlab.com`]' --output table
# Expected: Certificate for *.rdhcloudlab.com
```

**✅ Checkpoint**: All AWS resources exist and are accessible

---

### ✅ Checkpoint 1.2: Jenkins Server

**Required Jenkins Setup**:

| Component | Purpose | How to Verify |
|-----------|---------|---------------|
| Jenkins Server | CI/CD automation server | Access Jenkins UI |
| Jenkins Plugins | Pipeline, Git, Docker, AWS | Check Plugin Manager |
| AWS Credentials | Access to AWS services | Test AWS CLI from Jenkins |
| Git Access | Clone repositories | Test git clone |
| Docker | Build container images | `docker --version` |
| kubectl | Deploy to Kubernetes | `kubectl version` |
| Helm | Package manager for K8s | `helm version` |

**Verification Steps**:

**Step 1**: Access Jenkins Server

```bash
# SSH to Jenkins server
ssh -i ~/.ssh/jenkins-key.pem ec2-user@jenkins.rdhcloudlab.com

# Or if Jenkins is on local machine
# Just open terminal
```

**Step 2**: Verify Jenkins is Running

```bash
# Check Jenkins service
sudo systemctl status jenkins

# Expected Output:
# ● jenkins.service - Jenkins Continuous Integration Server
#    Active: active (running)
```

**Step 3**: Verify Required Tools on Jenkins Server

```bash
# Check AWS CLI
aws --version
# Expected: aws-cli/2.x.x

# Check Docker
docker --version
# Expected: Docker version 24.x.x

# Check kubectl
kubectl version --client
# Expected: Client Version: v1.28.x

# Check Helm
helm version
# Expected: version.BuildInfo{Version:"v3.12.x"}

# Check Git
git --version
# Expected: git version 2.x.x

# Check Python (for backend tests)
python3 --version
# Expected: Python 3.11.x

# Check Node.js (for frontend build)
node --version
# Expected: v18.x.x
```

**✅ Checkpoint**: All tools are installed and accessible on Jenkins server

---

### ✅ Checkpoint 1.3: Platform Add-ons

**Required Kubernetes Add-ons**:

| Add-on | Purpose | Namespace |
|--------|---------|-----------|
| AWS Load Balancer Controller | Manage ALB for Ingress | kube-system |
| External Secrets Operator | Sync secrets from AWS | external-secrets |
| Metrics Server | Provide metrics for HPA | kube-system |

**Verification Commands**:

```bash
# Update kubeconfig first
aws eks update-kubeconfig --region us-east-1 --name rdh-eks-cluster

# 1. Check AWS Load Balancer Controller
kubectl get deployment -n kube-system aws-load-balancer-controller
# Expected: READY 2/2

# 2. Check External Secrets Operator
kubectl get deployment -n external-secrets external-secrets
# Expected: READY 1/1

# 3. Check Metrics Server
kubectl get deployment -n kube-system metrics-server
# Expected: READY 1/1

# 4. Test metrics are working
kubectl top nodes
# Expected: CPU and Memory usage displayed
```

**✅ Checkpoint**: All platform add-ons are running

---

### ✅ Checkpoint 1.4: Access and Permissions

**Required Access**:

| Access Type | Purpose | How to Verify |
|-------------|---------|---------------|
| GitHub Repository Access | Clone and push code | `git clone` test |
| Jenkins Admin Access | Configure jobs | Login to Jenkins UI |
| AWS Console Access | View resources | Login to AWS Console |
| EKS Cluster Access | Deploy applications | `kubectl get nodes` |

**Verification Steps**:

**Step 1**: Verify GitHub Access

```bash
# Test SSH access to GitHub
ssh -T git@github.com
# Expected: Hi username! You've successfully authenticated

# Or test HTTPS access
git ls-remote https://github.com/your-org/ai-app.git
# Expected: List of refs
```

**Step 2**: Verify Jenkins Admin Access

```bash
# Access Jenkins UI
# Open browser: http://jenkins.rdhcloudlab.com:8080

# Login with admin credentials
# Username: admin
# Password: [from initial setup or password file]

# Verify you can access:
# - Dashboard
# - Manage Jenkins
# - New Item
```

**Step 3**: Verify AWS Access from Jenkins Server

```bash
# SSH to Jenkins server
ssh ec2-user@jenkins.rdhcloudlab.com

# Test AWS credentials
aws sts get-caller-identity
# Expected: Your AWS account details

# Test EKS access
aws eks describe-cluster --name rdh-eks-cluster --region us-east-1
# Expected: Cluster details
```

**Step 4**: Verify kubectl Access

```bash
# On Jenkins server
kubectl get nodes
# Expected: List of EKS nodes

kubectl get namespaces
# Expected: List of namespaces including kube-system
```

**✅ Checkpoint**: All access and permissions are configured

---

## Initial Setup Steps

### Step 1: Clone Repository to Your Local Machine

**Purpose**: Get a local copy for development and configuration

```bash
# Navigate to your workspace
cd ~/workspace

# Clone the repository
git clone https://github.com/your-org/ai-app.git

# Navigate into repository
cd ai-app

# Verify structure
ls -la
# Expected: backend/, frontend/, helm/, Jenkinsfile, README.md, etc.
```

**✅ Validation**: Repository cloned successfully with all files present

---

### Step 2: Configure AWS Resources

**Purpose**: Update Helm values with your actual AWS resources

**Step 2.1**: Get Your AWS Account ID

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"
# Record this: _______________
```

**Step 2.2**: Get Your Certificate ARN

```bash
CERT_ARN=$(aws acm list-certificates --region us-east-1 \
  --query 'CertificateSummaryList[?DomainName==`*.rdhcloudlab.com`].CertificateArn' \
  --output text)
echo "Certificate ARN: $CERT_ARN"
# Record this: _______________
```

**Step 2.3**: Get Your Security Group ID

```bash
# Find security group for ALB
SG_ID=$(aws ec2 describe-security-groups --region us-east-1 \
  --filters "Name=group-name,Values=*alb*" \
  --query 'SecurityGroups[0].GroupId' --output text)
echo "Security Group ID: $SG_ID"
# Record this: _______________
```

**Step 2.4**: Update Helm Values File

```bash
cd helm/ai-app

# Backup original
cp values.yaml values.yaml.backup

# Edit values.yaml
nano values.yaml
# Or use your preferred editor: vim, code, etc.
```

**Update these sections**:

```yaml
# Line ~17-18: Update backend image repository
backend:
  image:
    repository: YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-app-backend

# Line ~73-74: Update frontend image repository
frontend:
  image:
    repository: YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-app-frontend

# Line ~130: Update certificate ARN
ingress:
  annotations:
    alb.ingress.kubernetes.io/certificate-arn: YOUR_CERT_ARN

# Line ~138: Update security group
    alb.ingress.kubernetes.io/security-groups: YOUR_SG_ID
```

**✅ Validation**: Values file updated with actual AWS resources

---

### Step 3: Create AWS Secrets

**Purpose**: Store sensitive data (API keys) in AWS Secrets Manager

**Step 3.1**: Create Dev Environment Secret

```bash
aws secretsmanager create-secret \
  --name ai-app/dev/openai \
  --description "OpenAI API key for AI App - Dev Environment" \
  --secret-string '{"openaiApiKey":"sk-your-dev-api-key-here"}' \
  --region us-east-1

# Expected Output:
# {
#     "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:ai-app/dev/openai-AbCdEf",
#     "Name": "ai-app/dev/openai",
#     "VersionId": "..."
# }
```

**Step 3.2**: Verify Secret

```bash
aws secretsmanager get-secret-value \
  --secret-id ai-app/dev/openai \
  --region us-east-1 \
  --query 'SecretString' --output text

# Expected: {"openaiApiKey":"sk-..."}
```

**Step 3.3**: Create Stage and Prod Secrets (Optional)

```bash
# Stage environment
aws secretsmanager create-secret \
  --name ai-app/stage/openai \
  --secret-string '{"openaiApiKey":"sk-your-stage-api-key"}' \
  --region us-east-1

# Production environment
aws secretsmanager create-secret \
  --name ai-app/prod/openai \
  --secret-string '{"openaiApiKey":"sk-your-prod-api-key"}' \
  --region us-east-1
```

**✅ Validation**: Secrets created and accessible in AWS Secrets Manager

---

### Step 4: Commit Configuration Changes

**Purpose**: Save your configuration updates to Git

```bash
# Check what changed
git status
# Expected: Modified: helm/ai-app/values.yaml

# Review changes
git diff helm/ai-app/values.yaml

# Stage changes
git add helm/ai-app/values.yaml

# Commit with descriptive message
git commit -m "Configure AWS resources for deployment

- Updated ECR repository URLs with account ID
- Added ACM certificate ARN
- Configured security group for ALB
- Ready for initial deployment"

# Push to GitHub
git push origin main
```

**✅ Validation**: Changes committed and pushed to GitHub

---

## Validation

### Final Validation Checklist

Before proceeding to Jenkins setup, verify:

- [ ] **AWS Infrastructure**
  - [ ] EKS cluster is ACTIVE
  - [ ] ECR repositories exist (backend, frontend)
  - [ ] ACM certificate is issued
  - [ ] VPC and subnets are configured

- [ ] **Jenkins Server**
  - [ ] Jenkins service is running
  - [ ] All required tools installed (aws, docker, kubectl, helm, git)
  - [ ] Can access Jenkins UI
  - [ ] AWS credentials configured

- [ ] **Platform Add-ons**
  - [ ] AWS Load Balancer Controller running
  - [ ] External Secrets Operator running
  - [ ] Metrics Server running

- [ ] **Access and Permissions**
  - [ ] GitHub repository access (clone/push)
  - [ ] Jenkins admin access
  - [ ] AWS console access
  - [ ] kubectl access to EKS

- [ ] **Configuration**
  - [ ] Repository cloned locally
  - [ ] Helm values updated with AWS resources
  - [ ] AWS Secrets created
  - [ ] Changes committed and pushed

---

## Important Notes

### 🔒 Security Best Practices

1. **Never commit secrets to Git**
   - Always use AWS Secrets Manager
   - Check .gitignore includes secret patterns
   - Use .env.example as template only

2. **Use IAM roles instead of access keys**
   - Attach IAM role to Jenkins EC2 instance
   - Avoid storing AWS credentials in Jenkins

3. **Rotate secrets regularly**
   - Update OpenAI API keys periodically
   - Use AWS Secrets Manager rotation

### ⚠️ Common Pitfalls

1. **Wrong AWS Account ID**: Double-check account ID in values.yaml
2. **Certificate Region Mismatch**: Certificate must be in same region as ALB
3. **Security Group Rules**: Ensure ALB security group allows inbound 80/443
4. **IAM Permissions**: Jenkins needs ECR, EKS, Secrets Manager access

### 📝 What You've Accomplished

After completing this runbook:
- ✅ Understood the repository structure and workflow
- ✅ Verified all prerequisites are in place
- ✅ Configured AWS resources
- ✅ Created secrets for application
- ✅ Updated and committed configuration

---

## Next Steps

Proceed to **Runbook 02: Jenkins Configuration** to:
- Set up Jenkins pipeline job
- Configure job parameters
- Test the pipeline
- Deploy the application

---

**Runbook Version**: 1.0.0  
**Last Updated**: 2026-01-09  
**Next Review**: 2026-04-09