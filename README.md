# AI App - Production-Ready FastAPI + Next.js Application

A production-grade AI chat application with FastAPI backend and Next.js frontend, deployed on AWS EKS using Helm charts and Jenkins CI/CD.

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Repository Structure](#repository-structure)
- [Local Development](#local-development)
- [AWS Infrastructure Setup](#aws-infrastructure-setup)
- [Secrets Management](#secrets-management)
- [Jenkins Pipeline Setup](#jenkins-pipeline-setup)
- [Deployment](#deployment)
- [Verification](#verification)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)
- [Monitoring and Logging](#monitoring-and-logging)

## 🏗️ Architecture Overview

### Components

- **Backend**: FastAPI application with health checks and chat endpoints
- **Frontend**: Next.js application with responsive UI
- **Infrastructure**: AWS EKS with ALB Ingress Controller
- **Secrets**: External Secrets Operator for AWS Secrets Manager integration
- **CI/CD**: Jenkins pipeline for automated testing, building, and deployment

### Traffic Flow

```
Internet → ALB (HTTPS) → Ingress Controller
                          ├─ /api/* → Backend Service (FastAPI)
                          └─ /*     → Frontend Service (Next.js)
```

### Key Features

- ✅ Health and readiness probes
- ✅ Horizontal Pod Autoscaling (HPA)
- ✅ Resource requests and limits
- ✅ External secrets integration
- ✅ Multi-environment support (dev/stage/prod)
- ✅ Automated CI/CD with Jenkins
- ✅ ALB Ingress with SSL/TLS
- ✅ Structured logging with request tracing

## 📦 Prerequisites

### Required Infrastructure

1. **platform-infra** repository deployed:
   - AWS VPC with public/private subnets
   - EKS cluster running
   - ECR repositories created:
     - `ai-app-backend`
     - `ai-app-frontend`

2. **platform-addons** repository deployed:
   - AWS Load Balancer Controller
   - External Secrets Operator
   - Metrics Server (for HPA)

### Required Tools

- AWS CLI v2.x
- kubectl v1.28+
- Helm v3.12+
- Docker v24+
- Python 3.11+
- Node.js 18+
- Jenkins with required plugins

### AWS Permissions

The Jenkins service account or IAM role needs:
- ECR: Push/Pull images
- EKS: Update kubeconfig, deploy resources
- Secrets Manager: Read secrets
- EC2: Describe (for ALB)

## 📁 Repository Structure

```
ai-app/
├── README.md                          # This file
├── Jenkinsfile                        # CI/CD pipeline definition
├── .gitignore                         # Git ignore rules
├── .env.example                       # Environment variables template
│
├── backend/                           # FastAPI backend
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Backend container image
│   ├── app/
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── settings.py                # Configuration management
│   │   └── routers/
│   │       ├── health.py              # Health check endpoints
│   │       └── chat.py                # Chat API endpoints
│   └── tests/
│       └── test_health.py             # Backend tests
│
├── frontend/                          # Next.js frontend
│   ├── package.json                   # Node.js dependencies
│   ├── next.config.js                 # Next.js configuration
│   ├── Dockerfile                     # Frontend container image
│   └── pages/
│       └── index.js                   # Main UI page
│
└── helm/                              # Helm chart
    └── ai-app/
        ├── Chart.yaml                 # Chart metadata
        ├── values.yaml                # Default values
        └── templates/
            ├── backend-deployment.yaml
            ├── backend-service.yaml
            ├── frontend-deployment.yaml
            ├── frontend-service.yaml
            ├── ingress.yaml           # ALB Ingress configuration
            ├── hpa.yaml               # Horizontal Pod Autoscaler
            ├── configmap.yaml         # Configuration data
            └── externalsecret.yaml    # External Secrets integration
```

## 💻 Local Development

### Backend Development

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, AI!"}'
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production build
npm start
```

### Docker Local Testing

```bash
# Build backend
cd backend
docker build -t ai-app-backend:local .
docker run -p 8000:8000 ai-app-backend:local

# Build frontend
cd frontend
docker build -t ai-app-frontend:local .
docker run -p 3000:3000 ai-app-frontend:local
```

## 🔧 AWS Infrastructure Setup

### 1. Verify EKS Cluster

```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name rdh-eks-cluster

# Verify cluster access
kubectl cluster-info
kubectl get nodes
```

### 2. Verify ECR Repositories

```bash
# List ECR repositories
aws ecr describe-repositories --region us-east-1

# Expected repositories:
# - ai-app-backend
# - ai-app-frontend

# Create if missing
aws ecr create-repository --repository-name ai-app-backend --region us-east-1
aws ecr create-repository --repository-name ai-app-frontend --region us-east-1
```

### 3. Verify Platform Add-ons

```bash
# Check AWS Load Balancer Controller
kubectl get deployment -n kube-system aws-load-balancer-controller

# Check External Secrets Operator
kubectl get deployment -n external-secrets external-secrets

# Check Metrics Server (for HPA)
kubectl get deployment -n kube-system metrics-server
```

### 4. Create Namespace

```bash
# Create namespace for the application
kubectl create namespace ai

# Label namespace
kubectl label namespace ai environment=dev
```

## 🔐 Secrets Management

### Create AWS Secrets Manager Secret

The application expects OpenAI API key to be stored in AWS Secrets Manager.

```bash
# For dev environment
aws secretsmanager create-secret \
  --name ai-app/dev/openai \
  --description "OpenAI API key for AI App - Dev" \
  --secret-string '{"openaiApiKey":"sk-your-openai-api-key-here"}' \
  --region us-east-1

# For stage environment
aws secretsmanager create-secret \
  --name ai-app/stage/openai \
  --description "OpenAI API key for AI App - Stage" \
  --secret-string '{"openaiApiKey":"sk-your-openai-api-key-here"}' \
  --region us-east-1

# For prod environment
aws secretsmanager create-secret \
  --name ai-app/prod/openai \
  --description "OpenAI API key for AI App - Prod" \
  --secret-string '{"openaiApiKey":"sk-your-openai-api-key-here"}' \
  --region us-east-1
```

### Update Existing Secret

```bash
aws secretsmanager update-secret \
  --secret-id ai-app/dev/openai \
  --secret-string '{"openaiApiKey":"sk-new-api-key"}' \
  --region us-east-1
```

### Verify Secret

```bash
aws secretsmanager get-secret-value \
  --secret-id ai-app/dev/openai \
  --region us-east-1
```

### IAM Permissions for External Secrets

Ensure the EKS service account has permissions to read from Secrets Manager:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:ai-app/*"
    }
  ]
}
```

## 🚀 Jenkins Pipeline Setup

### 1. Create Jenkins Pipeline Job

1. Log into Jenkins
2. Click "New Item"
3. Enter name: `ai-app-deploy`
4. Select "Pipeline"
5. Click "OK"

### 2. Configure Pipeline

**General Settings:**
- ✅ This project is parameterized (parameters defined in Jenkinsfile)
- ✅ GitHub project: `https://github.com/your-org/ai-app`

**Pipeline Configuration:**
- Definition: `Pipeline script from SCM`
- SCM: `Git`
- Repository URL: `https://github.com/your-org/ai-app.git`
- Branch: `*/main`
- Script Path: `Jenkinsfile`

### 3. Configure Jenkins Credentials

Add AWS credentials to Jenkins:

```bash
# Option 1: Use IAM role (recommended for EC2/EKS)
# Attach IAM role to Jenkins EC2 instance

# Option 2: Use AWS credentials
# Add credentials in Jenkins: Manage Jenkins → Credentials
# Kind: AWS Credentials
# ID: aws-credentials
```

### 4. Install Required Jenkins Plugins

- Pipeline
- Git
- Docker Pipeline
- Kubernetes CLI
- AWS Steps

## 📤 Deployment

### First-Time Deployment

1. **Update Helm Values**

Edit `helm/ai-app/values.yaml`:

```yaml
# Update with your AWS account ID
backend:
  image:
    repository: YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-app-backend

frontend:
  image:
    repository: YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-app-frontend

# Update with your certificate ARN
ingress:
  annotations:
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:YOUR_ACCOUNT_ID:certificate/YOUR_CERT_ID
    alb.ingress.kubernetes.io/security-groups: sg-YOUR_SECURITY_GROUP
```

2. **Commit and Push Changes**

```bash
git add .
git commit -m "Initial deployment configuration"
git push origin main
```

3. **Run Jenkins Pipeline**

- Go to Jenkins → ai-app-deploy
- Click "Build with Parameters"
- Set parameters:
  - ENV: `dev`
  - AWS_REGION: `us-east-1`
  - AWS_ACCOUNT_ID: `123456789012`
  - CLUSTER_NAME: `rdh-eks-cluster`
  - NAMESPACE: `ai`
  - INGRESS_HOST: `ai-dev.rdhcloudlab.com`
- Click "Build"

### Subsequent Deployments

For code changes, simply push to the repository and trigger the Jenkins pipeline. The pipeline will:

1. Run backend tests
2. Build Docker images with git commit SHA as tag
3. Push images to ECR
4. Deploy to EKS using Helm
5. Verify rollout
6. Print verification commands

### Manual Helm Deployment

If you need to deploy manually without Jenkins:

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build and push images
cd backend
docker build -t 123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-app-backend:v1.0.0 .
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-app-backend:v1.0.0

cd ../frontend
docker build -t 123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-app-frontend:v1.0.0 .
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-app-frontend:v1.0.0

# Deploy with Helm
cd ../helm
helm upgrade --install ai-app ./ai-app \
  --namespace ai \
  --create-namespace \
  --set env=dev \
  --set ingressHost=ai-dev.rdhcloudlab.com \
  --set backend.image.tag=v1.0.0 \
  --set frontend.image.tag=v1.0.0 \
  --wait \
  --timeout 10m
```

## ✅ Verification

### 1. Check Kubernetes Resources

```bash
# Check all resources
kubectl get all -n ai

# Check pods
kubectl get pods -n ai
kubectl describe pod <pod-name> -n ai

# Check services
kubectl get svc -n ai

# Check ingress
kubectl get ingress -n ai
kubectl describe ingress ai-app-ingress -n ai

# Check HPA
kubectl get hpa -n ai

# Check external secrets
kubectl get externalsecret -n ai
kubectl get secret ai-app-secrets -n ai
```

### 2. Check Helm Release

```bash
# List releases
helm list -n ai

# Get release status
helm status ai-app -n ai

# Get release values
helm get values ai-app -n ai

# Get release history
helm history ai-app -n ai
```

### 3. Test Application Endpoints

```bash
# Get ALB DNS name
ALB_DNS=$(kubectl get ingress ai-app-ingress -n ai -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "ALB DNS: $ALB_DNS"

# Test backend health (via ALB)
curl http://$ALB_DNS/api/health

# Test backend health (via ingress host)
curl https://ai-dev.rdhcloudlab.com/api/health

# Test chat endpoint
curl -X POST https://ai-dev.rdhcloudlab.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, AI!"}'

# Test frontend
curl https://ai-dev.rdhcloudlab.com/
```

### 4. Check Application Logs

```bash
# Backend logs
kubectl logs -n ai -l app=ai-app-backend --tail=100 -f

# Frontend logs
kubectl logs -n ai -l app=ai-app-frontend --tail=100 -f

# All logs
kubectl logs -n ai --all-containers=true --tail=50
```

### 5. Check ALB Target Health

```bash
# Get ALB ARN
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?contains(LoadBalancerName, 'k8s-ai')].LoadBalancerArn" \
  --output text)

# Get target groups
aws elbv2 describe-target-groups --load-balancer-arn $ALB_ARN

# Check target health
TG_ARN=$(aws elbv2 describe-target-groups \
  --load-balancer-arn $ALB_ARN \
  --query "TargetGroups[0].TargetGroupArn" \
  --output text)

aws elbv2 describe-target-health --target-group-arn $TG_ARN
```

### 6. Verify DNS Resolution

```bash
# Check DNS resolution
nslookup ai-dev.rdhcloudlab.com

# Check with dig
dig ai-dev.rdhcloudlab.com
```

## 🔄 Rollback Procedures

### Helm Rollback

```bash
# View release history
helm history ai-app -n ai

# Rollback to previous version
helm rollback ai-app -n ai

# Rollback to specific revision
helm rollback ai-app 2 -n ai

# Verify rollback
kubectl rollout status deployment/ai-app-backend -n ai
kubectl rollout status deployment/ai-app-frontend -n ai
```

### Kubernetes Rollback

```bash
# Rollback backend deployment
kubectl rollout undo deployment/ai-app-backend -n ai

# Rollback frontend deployment
kubectl rollout undo deployment/ai-app-frontend -n ai

# Rollback to specific revision
kubectl rollout undo deployment/ai-app-backend --to-revision=2 -n ai

# Check rollout status
kubectl rollout status deployment/ai-app-backend -n ai
```

### Emergency Rollback via Jenkins

1. Go to Jenkins → ai-app-deploy
2. Find the last successful build
3. Click "Rebuild" with the same parameters
4. This will redeploy the previous working version

## 🔍 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n ai

# Describe pod for events
kubectl describe pod <pod-name> -n ai

# Check pod logs
kubectl logs <pod-name> -n ai

# Check previous container logs (if crashed)
kubectl logs <pod-name> -n ai --previous

# Common issues:
# - Image pull errors: Check ECR permissions
# - CrashLoopBackOff: Check application logs
# - Pending: Check resource requests vs node capacity
```

### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n ai
kubectl describe ingress ai-app-ingress -n ai

# Check ALB controller logs
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller

# Check ingress events
kubectl get events -n ai --sort-by='.lastTimestamp' | grep ingress

# Common issues:
# - ALB not created: Check controller logs and IAM permissions
# - 503 errors: Check target health and pod readiness
# - SSL errors: Verify certificate ARN
```

### External Secrets Not Syncing

```bash
# Check external secret status
kubectl get externalsecret -n ai
kubectl describe externalsecret ai-app-external-secret -n ai

# Check if secret was created
kubectl get secret ai-app-secrets -n ai

# Check external secrets operator logs
kubectl logs -n external-secrets -l app.kubernetes.io/name=external-secrets

# Verify secret in AWS
aws secretsmanager get-secret-value --secret-id ai-app/dev/openai

# Common issues:
# - Secret not found: Verify secret name in AWS Secrets Manager
# - Permission denied: Check IAM role/policy for service account
# - Wrong format: Ensure secret is JSON with correct key names
```

### HPA Not Scaling

```bash
# Check HPA status
kubectl get hpa -n ai
kubectl describe hpa ai-app-backend-hpa -n ai

# Check metrics server
kubectl top nodes
kubectl top pods -n ai

# Check metrics server logs
kubectl logs -n kube-system -l k8s-app=metrics-server

# Common issues:
# - Metrics not available: Ensure metrics-server is running
# - Not scaling up: Check CPU/memory thresholds
# - Not scaling down: Check stabilization window
```

### Backend API Errors

```bash
# Check backend logs
kubectl logs -n ai -l app=ai-app-backend --tail=100

# Check backend pod status
kubectl get pods -n ai -l app=ai-app-backend

# Test backend directly (port-forward)
kubectl port-forward -n ai svc/ai-app-backend 8000:8000
curl http://localhost:8000/api/health

# Check environment variables
kubectl exec -n ai <backend-pod-name> -- env | grep -E 'OPENAI|LOG_LEVEL'

# Common issues:
# - OpenAI API errors: Check API key in secret
# - Connection timeouts: Check network policies
# - 500 errors: Check application logs for stack traces
```

### Frontend Not Loading

```bash
# Check frontend logs
kubectl logs -n ai -l app=ai-app-frontend --tail=100

# Check frontend pod status
kubectl get pods -n ai -l app=ai-app-frontend

# Test frontend directly (port-forward)
kubectl port-forward -n ai svc/ai-app-frontend 3000:3000
curl http://localhost:3000

# Common issues:
# - Build errors: Check Docker build logs
# - API connection errors: Verify ingress routing
# - Static assets not loading: Check Next.js configuration
```

### Jenkins Pipeline Failures

```bash
# Check Jenkins console output
# Common issues:
# - AWS credentials: Verify IAM role or credentials
# - Docker build fails: Check Dockerfile syntax
# - kubectl access denied: Verify kubeconfig and permissions
# - Helm timeout: Increase --timeout value or check pod startup
```

## 📊 Monitoring and Logging

### CloudWatch Logs

```bash
# View EKS cluster logs in CloudWatch
aws logs tail /aws/eks/rdh-eks-cluster/cluster --follow

# View application logs (if using CloudWatch Container Insights)
aws logs tail /aws/containerinsights/rdh-eks-cluster/application --follow
```

### Prometheus Metrics (if installed)

```bash
# Port-forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Access Prometheus UI
open http://localhost:9090

# Example queries:
# - CPU usage: rate(container_cpu_usage_seconds_total{namespace="ai"}[5m])
# - Memory usage: container_memory_usage_bytes{namespace="ai"}
# - Request rate: rate(http_requests_total{namespace="ai"}[5m])
```

### Application Metrics

The backend exposes request tracing via `X-Request-ID` header. Use this for distributed tracing.

```bash
# Example: Track a specific request
curl -v https://ai-dev.rdhcloudlab.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}' 2>&1 | grep X-Request-ID

# Then search logs for that request ID
kubectl logs -n ai -l app=ai-app-backend | grep <request-id>
```

## 🔒 Security Best Practices

1. **Secrets Management**
   - Never commit secrets to Git
   - Use AWS Secrets Manager for sensitive data
   - Rotate API keys regularly

2. **Network Security**
   - Use security groups to restrict ALB access
   - Enable SSL/TLS for all external traffic
   - Use network policies for pod-to-pod communication

3. **Container Security**
   - Run containers as non-root user
   - Use read-only root filesystem where possible
   - Scan images for vulnerabilities

4. **Access Control**
   - Use RBAC for Kubernetes access
   - Implement least-privilege IAM policies
   - Enable audit logging

## 📝 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Helm Documentation](https://helm.sh/docs/)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)
- [External Secrets Operator](https://external-secrets.io/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests locally
4. Submit a pull request
5. Wait for CI/CD checks to pass

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For issues and questions:
- Create an issue in the repository
- Contact DevOps team: devops@rdhcloudlab.com
- Slack channel: #ai-app-support

---

**Last Updated**: 2026-01-09  
**Version**: 1.0.0  
**Maintained by**: DevOps Team
