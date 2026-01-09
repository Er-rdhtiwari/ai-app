# AI App - Deployment Runbook

**Version**: 1.0.0  
**Last Updated**: 2026-01-09  
**Owner**: DevOps Team

---

## Table of Contents

1. [Pre-Deployment Validation](#pre-deployment-validation)
2. [Environment Setup](#environment-setup)
3. [Deployment Steps](#deployment-steps)
4. [Post-Deployment Validation](#post-deployment-validation)
5. [Rollback Procedures](#rollback-procedures)
6. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Validation

### Checkpoint 1: Repository Structure Validation

**Objective**: Verify all required files are present and properly structured.

**Steps**:

```bash
# Navigate to repository
cd /path/to/ai-app

# List all files
find . -type f -not -path "./.git/*" -not -path "./node_modules/*" \
  -not -path "./__pycache__/*" -not -path "./venv/*" | sort

# Expected: 35 files including:
# - Backend: 7 Python files + Dockerfile + requirements.txt
# - Frontend: 4 files + Dockerfile
# - Helm: 10 templates + Chart.yaml + values.yaml
# - Root: Jenkinsfile, README.md, .gitignore, .env.example
```

**Expected Result**:
```
✅ All 35 files present
✅ Directory structure matches specification
```

**Checkpoint**: ✅ PASS / ❌ FAIL

---

### Checkpoint 2: Helm Chart Validation

**Objective**: Validate Helm chart syntax and structure.

#### Step 2.1: Helm Lint

```bash
cd helm
helm lint ./ai-app --strict
```

**Expected Output**:
```
==> Linting ./ai-app
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

**Checkpoint**: ✅ PASS (0 failures)

#### Step 2.2: Helm Template Generation

```bash
helm template ai-app ./ai-app --dry-run > /tmp/helm-output.yaml
echo "✅ Helm template generated successfully"
wc -l /tmp/helm-output.yaml
```

**Expected Output**:
```
✅ Helm template generated successfully
     363 /tmp/helm-output.yaml
```

**Checkpoint**: ✅ PASS (363 lines generated)

#### Step 2.3: YAML Syntax Validation

```bash
python3 -c "import yaml; list(yaml.safe_load_all(open('/tmp/helm-output.yaml')))" \
  && echo "✅ YAML syntax is valid"
```

**Expected Output**:
```
✅ YAML syntax is valid
```

**Checkpoint**: ✅ PASS

#### Step 2.4: Verify Generated Resources

```bash
grep -E "^kind:" /tmp/helm-output.yaml | sort | uniq -c
```

**Expected Output**:
```
   1 kind: ConfigMap
   2 kind: Deployment
   1 kind: ExternalSecret
   1 kind: HorizontalPodAutoscaler
   1 kind: Ingress
   1 kind: SecretStore
   2 kind: Service
   1 kind: ServiceAccount
```

**Checkpoint**: ✅ PASS (9 resources)

---

### Checkpoint 3: Backend Validation

**Objective**: Validate Python code syntax and structure.

#### Step 3.1: Python Syntax Check

```bash
cd backend
python3 -m py_compile app/main.py app/settings.py \
  app/routers/health.py app/routers/chat.py \
  && echo "✅ Python syntax is valid"
```

**Expected Output**:
```
✅ Python syntax is valid
```

**Checkpoint**: ✅ PASS

#### Step 3.2: Verify Python Packages

```bash
# Check __init__.py files exist
ls -la app/__init__.py app/routers/__init__.py tests/__init__.py
```

**Expected Output**:
```
-rw-r--r-- 1 user group 0 Jan  9 09:19 app/__init__.py
-rw-r--r-- 1 user group 0 Jan  9 09:19 app/routers/__init__.py
-rw-r--r-- 1 user group 0 Jan  9 09:19 tests/__init__.py
```

**Checkpoint**: ✅ PASS

#### Step 3.3: Backend Dockerfile Validation

```bash
grep -E "^FROM|^RUN|^COPY|^CMD|^EXPOSE|^WORKDIR" Dockerfile
```

**Expected Output**:
```
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Checkpoint**: ✅ PASS

#### Step 3.4: Dependencies Check

```bash
cat requirements.txt
```

**Expected Output**:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
openai==1.3.7
```

**Checkpoint**: ✅ PASS (9 dependencies)

---

### Checkpoint 4: Frontend Validation

**Objective**: Validate Next.js configuration and structure.

#### Step 4.1: Next.js Config Validation

```bash
cd frontend
node -e "const config = require('./next.config.js'); \
  console.log('✅ Next.js config is valid'); \
  console.log(JSON.stringify(config, null, 2))"
```

**Expected Output**:
```
✅ Next.js config is valid
{
  "reactStrictMode": true,
  "output": "standalone"
}
```

**Checkpoint**: ✅ PASS

#### Step 4.2: Package.json Validation

```bash
node -e "const pkg = require('./package.json'); \
  console.log('✅ package.json is valid'); \
  console.log('Dependencies:', Object.keys(pkg.dependencies).length)"
```

**Expected Output**:
```
✅ package.json is valid
Dependencies: 3
```

**Checkpoint**: ✅ PASS

#### Step 4.3: Frontend Dockerfile Validation

```bash
grep -E "^FROM|^RUN|^COPY|^CMD|^EXPOSE|^WORKDIR" Dockerfile | head -15
```

**Expected Output**:
```
FROM node:18-alpine AS base
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build
FROM base AS runner
WORKDIR /app
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
```

**Checkpoint**: ✅ PASS (Multi-stage build)

---

### Checkpoint 5: CI/CD Pipeline Validation

**Objective**: Validate Jenkinsfile structure.

#### Step 5.1: Jenkinsfile Structure Check

```bash
cd /path/to/ai-app
grep -E "^pipeline|^    stage\(" Jenkinsfile | wc -l
```

**Expected Output**:
```
13  # (1 pipeline + 12 stages)
```

**Checkpoint**: ✅ PASS

#### Step 5.2: Verify Pipeline Parameters

```bash
grep -A 20 "parameters {" Jenkinsfile | grep "name:" | wc -l
```

**Expected Output**:
```
6  # (ENV, AWS_REGION, AWS_ACCOUNT_ID, CLUSTER_NAME, NAMESPACE, INGRESS_HOST)
```

**Checkpoint**: ✅ PASS

---

### Checkpoint 6: Security Validation

**Objective**: Ensure no secrets are committed and security best practices are followed.

#### Step 6.1: Check for Secrets

```bash
# Check for common secret patterns
grep -r "sk-" . --exclude-dir=.git --exclude="*.md" || echo "✅ No OpenAI keys found"
grep -r "AKIA" . --exclude-dir=.git --exclude="*.md" || echo "✅ No AWS keys found"
grep -r "password.*=" . --exclude-dir=.git --exclude="*.md" --exclude=".env.example" \
  || echo "✅ No hardcoded passwords found"
```

**Expected Output**:
```
✅ No OpenAI keys found
✅ No AWS keys found
✅ No hardcoded passwords found
```

**Checkpoint**: ✅ PASS

#### Step 6.2: Verify .gitignore

```bash
cat .gitignore | grep -E "\.env$|secret|password|credentials|\.pem|\.key" | wc -l
```

**Expected Output**:
```
7  # (Multiple secret-related patterns)
```

**Checkpoint**: ✅ PASS

#### Step 6.3: Check Container Security

```bash
# Verify non-root users in Dockerfiles
grep "USER" backend/Dockerfile frontend/Dockerfile
```

**Expected Output**:
```
backend/Dockerfile:USER appuser
frontend/Dockerfile:USER nextjs
```

**Checkpoint**: ✅ PASS

---

## Environment Setup

### Checkpoint 7: AWS Prerequisites

**Objective**: Verify AWS infrastructure is ready.

#### Step 7.1: Verify EKS Cluster

```bash
aws eks describe-cluster --name rdh-eks-cluster --region us-east-1 \
  --query 'cluster.status' --output text
```

**Expected Output**:
```
ACTIVE
```

**Checkpoint**: ✅ PASS / ❌ FAIL

#### Step 7.2: Update Kubeconfig

```bash
aws eks update-kubeconfig --region us-east-1 --name rdh-eks-cluster
kubectl cluster-info
```

**Expected Output**:
```
Updated context arn:aws:eks:us-east-1:123456789012:cluster/rdh-eks-cluster
Kubernetes control plane is running at https://...
```

**Checkpoint**: ✅ PASS / ❌ FAIL

#### Step 7.3: Verify ECR Repositories

```bash
aws ecr describe-repositories --region us-east-1 \
  --repository-names ai-app-backend ai-app-frontend \
  --query 'repositories[].repositoryName' --output table
```

**Expected Output**:
```
-----------------------
|DescribeRepositories|
+---------------------+
|  ai-app-backend     |
|  ai-app-frontend    |
+---------------------+
```

**Checkpoint**: ✅ PASS / ❌ FAIL

**If FAIL**: Create repositories:
```bash
aws ecr create-repository --repository-name ai-app-backend --region us-east-1
aws ecr create-repository --repository-name ai-app-frontend --region us-east-1
```

#### Step 7.4: Verify Platform Add-ons

```bash
# Check AWS Load Balancer Controller
kubectl get deployment -n kube-system aws-load-balancer-controller

# Check External Secrets Operator
kubectl get deployment -n external-secrets external-secrets

# Check Metrics Server
kubectl get deployment -n kube-system metrics-server
```

**Expected Output**:
```
NAME                           READY   UP-TO-DATE   AVAILABLE   AGE
aws-load-balancer-controller   2/2     2            2           30d

NAME               READY   UP-TO-DATE   AVAILABLE   AGE
external-secrets   1/1     1            1           30d

NAME             READY   UP-TO-DATE   AVAILABLE   AGE
metrics-server   1/1     1            1           30d
```

**Checkpoint**: ✅ PASS / ❌ FAIL

---

### Checkpoint 8: Secrets Management

**Objective**: Create and verify AWS Secrets Manager secrets.

#### Step 8.1: Create Secrets (Dev Environment)

```bash
# Create OpenAI API key secret
aws secretsmanager create-secret \
  --name ai-app/dev/openai \
  --description "OpenAI API key for AI App - Dev" \
  --secret-string '{"openaiApiKey":"sk-your-actual-openai-api-key-here"}' \
  --region us-east-1
```

**Expected Output**:
```json
{
    "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:ai-app/dev/openai-AbCdEf",
    "Name": "ai-app/dev/openai",
    "VersionId": "..."
}
```

**Checkpoint**: ✅ PASS / ❌ FAIL

#### Step 8.2: Verify Secret

```bash
aws secretsmanager get-secret-value \
  --secret-id ai-app/dev/openai \
  --region us-east-1 \
  --query 'SecretString' --output text
```

**Expected Output**:
```json
{"openaiApiKey":"sk-..."}
```

**Checkpoint**: ✅ PASS / ❌ FAIL

#### Step 8.3: Repeat for Other Environments

```bash
# Stage
aws secretsmanager create-secret \
  --name ai-app/stage/openai \
  --secret-string '{"openaiApiKey":"sk-stage-key"}' \
  --region us-east-1

# Prod
aws secretsmanager create-secret \
  --name ai-app/prod/openai \
  --secret-string '{"openaiApiKey":"sk-prod-key"}' \
  --region us-east-1
```

**Checkpoint**: ✅ PASS / ❌ FAIL

---

### Checkpoint 9: Configuration Update

**Objective**: Update Helm values with actual AWS resources.

#### Step 9.1: Get AWS Account ID

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"
```

**Expected Output**:
```
AWS Account ID: 123456789012
```

**Checkpoint**: ✅ PASS

#### Step 9.2: Get Certificate ARN

```bash
aws acm list-certificates --region us-east-1 \
  --query 'CertificateSummaryList[?DomainName==`*.rdhcloudlab.com`].CertificateArn' \
  --output text
```

**Expected Output**:
```
arn:aws:acm:us-east-1:123456789012:certificate/abc123...
```

**Checkpoint**: ✅ PASS / ❌ FAIL

#### Step 9.3: Update values.yaml

```bash
cd helm/ai-app

# Backup original
cp values.yaml values.yaml.backup

# Update with actual values (manual edit or sed)
sed -i "s/123456789012/$AWS_ACCOUNT_ID/g" values.yaml
sed -i "s|arn:aws:acm:us-east-1:123456789012:certificate/YOUR_CERT_ID|$CERT_ARN|g" values.yaml
```

**Checkpoint**: ✅ PASS

#### Step 9.4: Verify Updated Values

```bash
grep "repository:" values.yaml
grep "certificate-arn:" values.yaml
```

**Expected Output**:
```
    repository: 123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-app-backend
    repository: 123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-app-frontend
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:123456789012:certificate/...
```

**Checkpoint**: ✅ PASS

---

## Deployment Steps

### Checkpoint 10: Jenkins Pipeline Setup

**Objective**: Configure Jenkins pipeline for deployment.

#### Step 10.1: Create Jenkins Job

1. Log into Jenkins
2. Click "New Item"
3. Enter name: `ai-app-deploy`
4. Select "Pipeline"
5. Click "OK"

**Checkpoint**: ✅ PASS

#### Step 10.2: Configure Pipeline

**General Settings**:
- ✅ This project is parameterized
- ✅ GitHub project URL: `https://github.com/your-org/ai-app`

**Pipeline Configuration**:
- Definition: `Pipeline script from SCM`
- SCM: `Git`
- Repository URL: `https://github.com/your-org/ai-app.git`
- Branch: `*/main`
- Script Path: `Jenkinsfile`

**Checkpoint**: ✅ PASS

#### Step 10.3: Configure AWS Credentials

```bash
# Verify Jenkins has AWS credentials configured
# Or attach IAM role to Jenkins EC2 instance
```

**Checkpoint**: ✅ PASS

---

### Checkpoint 11: First Deployment

**Objective**: Deploy application to dev environment.

#### Step 11.1: Trigger Jenkins Build

**Parameters**:
- ENV: `dev`
- AWS_REGION: `us-east-1`
- AWS_ACCOUNT_ID: `123456789012`
- CLUSTER_NAME: `rdh-eks-cluster`
- NAMESPACE: `ai`
- INGRESS_HOST: `ai-dev.rdhcloudlab.com`

**Checkpoint**: ✅ Build Started

#### Step 11.2: Monitor Pipeline Stages

Watch Jenkins console output for each stage:

1. ✅ Validate Tools
2. ✅ AWS Identity Check
3. ✅ Backend Tests
4. ✅ Build Frontend
5. ✅ ECR Login
6. ✅ Build and Push Backend Image
7. ✅ Build and Push Frontend Image
8. ✅ Update Kubeconfig
9. ✅ Create Namespace
10. ✅ Helm Deploy
11. ✅ Verify Rollout
12. ✅ Helm Status
13. ✅ Verification Commands

**Expected Duration**: 10-15 minutes

**Checkpoint**: ✅ All stages PASS / ❌ FAIL at stage X

---

## Post-Deployment Validation

### Checkpoint 12: Kubernetes Resources

**Objective**: Verify all Kubernetes resources are created and healthy.

#### Step 12.1: Check Namespace

```bash
kubectl get namespace ai
kubectl describe namespace ai
```

**Expected Output**:
```
NAME   STATUS   AGE
ai     Active   5m

Labels: environment=dev
```

**Checkpoint**: ✅ PASS

#### Step 12.2: Check Pods

```bash
kubectl get pods -n ai
```

**Expected Output**:
```
NAME                               READY   STATUS    RESTARTS   AGE
ai-app-backend-xxx-yyy            1/1     Running   0          5m
ai-app-backend-xxx-zzz            1/1     Running   0          5m
ai-app-frontend-aaa-bbb           1/1     Running   0          5m
ai-app-frontend-aaa-ccc           1/1     Running   0          5m
```

**Checkpoint**: ✅ PASS (All pods Running)

#### Step 12.3: Check Services

```bash
kubectl get svc -n ai
```

**Expected Output**:
```
NAME               TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
ai-app-backend     ClusterIP   10.100.x.x       <none>        8000/TCP   5m
ai-app-frontend    ClusterIP   10.100.y.y       <none>        3000/TCP   5m
```

**Checkpoint**: ✅ PASS

#### Step 12.4: Check Ingress

```bash
kubectl get ingress -n ai
kubectl describe ingress ai-app-ingress -n ai
```

**Expected Output**:
```
NAME              CLASS   HOSTS                      ADDRESS                                   PORTS   AGE
ai-app-ingress    alb     ai-dev.rdhcloudlab.com    k8s-ai-aiappingr-xxx.us-east-1.elb...    80      5m
```

**Checkpoint**: ✅ PASS (ALB provisioned)

#### Step 12.5: Check HPA

```bash
kubectl get hpa -n ai
```

**Expected Output**:
```
NAME                    REFERENCE                   TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
ai-app-backend-hpa      Deployment/ai-app-backend   15%/70%, 20%/80%   2         10        2          5m
```

**Checkpoint**: ✅ PASS

#### Step 12.6: Check External Secrets

```bash
kubectl get externalsecret -n ai
kubectl get secret ai-app-secrets -n ai
```

**Expected Output**:
```
NAME                      STORE                  REFRESH INTERVAL   STATUS         READY
ai-app-external-secret    aws-secrets-manager    1h                 SecretSynced   True

NAME              TYPE     DATA   AGE
ai-app-secrets    Opaque   1      5m
```

**Checkpoint**: ✅ PASS (Secret synced)

---

### Checkpoint 13: Application Health

**Objective**: Verify application endpoints are responding.

#### Step 13.1: Get ALB DNS

```bash
ALB_DNS=$(kubectl get ingress ai-app-ingress -n ai \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "ALB DNS: $ALB_DNS"
```

**Expected Output**:
```
ALB DNS: k8s-ai-aiappingr-xxx-yyy.us-east-1.elb.amazonaws.com
```

**Checkpoint**: ✅ PASS

#### Step 13.2: Test Backend Health (via ALB)

```bash
curl -f http://$ALB_DNS/api/health
```

**Expected Output**:
```json
{
  "status": "ok",
  "service": "ai-app-backend"
}
```

**Checkpoint**: ✅ PASS (200 OK)

#### Step 13.3: Test Backend Health (via Ingress Host)

```bash
curl -f https://ai-dev.rdhcloudlab.com/api/health
```

**Expected Output**:
```json
{
  "status": "ok",
  "service": "ai-app-backend"
}
```

**Checkpoint**: ✅ PASS (200 OK with SSL)

#### Step 13.4: Test Chat Endpoint

```bash
curl -X POST https://ai-dev.rdhcloudlab.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, AI!"}' | jq
```

**Expected Output**:
```json
{
  "answer": "Echo: Hello, AI! (This is a stub response...)",
  "trace_id": "abc123-def456-..."
}
```

**Checkpoint**: ✅ PASS (200 OK with trace_id)

#### Step 13.5: Test Frontend

```bash
curl -f https://ai-dev.rdhcloudlab.com/ | grep "AI Chat Application"
```

**Expected Output**:
```html
<h1 style="...">AI Chat Application</h1>
```

**Checkpoint**: ✅ PASS (200 OK)

#### Step 13.6: Browser Test

1. Open browser: `https://ai-dev.rdhcloudlab.com`
2. Verify page loads
3. Enter message: "Test message"
4. Click "Send Message"
5. Verify response appears with trace ID

**Checkpoint**: ✅ PASS (UI functional)

---

### Checkpoint 14: Helm Release Status

**Objective**: Verify Helm release is healthy.

#### Step 14.1: List Releases

```bash
helm list -n ai
```

**Expected Output**:
```
NAME    NAMESPACE  REVISION  UPDATED                   STATUS    CHART         APP VERSION
ai-app  ai         1         2026-01-09 09:30:00 IST   deployed  ai-app-1.0.0  1.0.0
```

**Checkpoint**: ✅ PASS (Status: deployed)

#### Step 14.2: Get Release Status

```bash
helm status ai-app -n ai
```

**Expected Output**:
```
NAME: ai-app
LAST DEPLOYED: ...
NAMESPACE: ai
STATUS: deployed
REVISION: 1
...
```

**Checkpoint**: ✅ PASS

#### Step 14.3: Get Release Values

```bash
helm get values ai-app -n ai
```

**Expected Output**:
```yaml
USER-SUPPLIED VALUES:
backend:
  image:
    tag: abc123
env: dev
frontend:
  image:
    tag: abc123
ingressHost: ai-dev.rdhcloudlab.com
```

**Checkpoint**: ✅ PASS

---

### Checkpoint 15: Logging and Monitoring

**Objective**: Verify logs are being generated correctly.

#### Step 15.1: Check Backend Logs

```bash
kubectl logs -n ai -l app=ai-app-backend --tail=20
```

**Expected Output**:
```
2026-01-09 09:30:00 - app.main - INFO - Starting AI App Backend v1.0.0
2026-01-09 09:30:00 - app.main - INFO - Environment: dev
2026-01-09 09:30:05 - app.main - INFO - Request started
...
```

**Checkpoint**: ✅ PASS (Logs present, no errors)

#### Step 15.2: Check Frontend Logs

```bash
kubectl logs -n ai -l app=ai-app-frontend --tail=20
```

**Expected Output**:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
...
```

**Checkpoint**: ✅ PASS (Logs present, no errors)

#### Step 15.3: Check for Errors

```bash
kubectl logs -n ai --all-containers=true --tail=100 | grep -i "error\|exception\|fatal"
```

**Expected Output**:
```
(no output or only expected errors)
```

**Checkpoint**: ✅ PASS (No critical errors)

---

### Checkpoint 16: ALB Target Health

**Objective**: Verify ALB targets are healthy.

#### Step 16.1: Get ALB ARN

```bash
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?contains(LoadBalancerName, 'k8s-ai')].LoadBalancerArn" \
  --output text)
echo "ALB ARN: $ALB_ARN"
```

**Checkpoint**: ✅ PASS

#### Step 16.2: Get Target Groups

```bash
aws elbv2 describe-target-groups --load-balancer-arn $ALB_ARN \
  --query 'TargetGroups[].{Name:TargetGroupName,Port:Port}' --output table
```

**Expected Output**:
```
-----------------------------------------
|        DescribeTargetGroups          |
+----------------------+---------------+
|        Name          |     Port      |
+----------------------+---------------+
|  k8s-ai-backend-xxx  |     8000      |
|  k8s-ai-frontend-yyy |     3000      |
+----------------------+---------------+
```

**Checkpoint**: ✅ PASS

#### Step 16.3: Check Target Health

```bash
TG_ARN=$(aws elbv2 describe-target-groups --load-balancer-arn $ALB_ARN \
  --query "TargetGroups[0].TargetGroupArn" --output text)

aws elbv2 describe-target-health --target-group-arn $TG_ARN \
  --query 'TargetHealthDescriptions[].{Target:Target.Id,Health:TargetHealth.State}' \
  --output table
```

**Expected Output**:
```
-----------------------------------------
|      DescribeTargetHealth            |
+------------------+-------------------+
|     Health       |      Target       |
+------------------+-------------------+
|  healthy         |  10.0.1.x:8000    |
|  healthy         |  10.0.2.y:8000    |
+------------------+-------------------+
```

**Checkpoint**: ✅ PASS (All targets healthy)

---

## Rollback Procedures

### Checkpoint 17: Rollback Preparation

**Objective**: Document current state before rollback.

#### Step 17.1: Get Current Revision

```bash
helm history ai-app -n ai
```

**Expected Output**:
```
REVISION  UPDATED                   STATUS      CHART         APP VERSION  DESCRIPTION
1         2026-01-09 09:30:00 IST   deployed    ai-app-1.0.0  1.0.0        Install complete
```

**Current Revision**: _____ (record this)

**Checkpoint**: ✅ Documented

---

### Checkpoint 18: Execute Rollback

**Objective**: Rollback to previous working version.

#### Step 18.1: Rollback to Previous Version

```bash
helm rollback ai-app -n ai
```

**Expected Output**:
```
Rollback was a success! Happy Helming!
```

**Checkpoint**: ✅ PASS

#### Step 18.2: Verify Rollback

```bash
kubectl rollout status deployment/ai-app-backend -n ai
kubectl rollout status deployment/ai-app-frontend -n ai
```

**Expected Output**:
```
deployment "ai-app-backend" successfully rolled out
deployment "ai-app-frontend" successfully rolled out
```

**Checkpoint**: ✅ PASS

#### Step 18.3: Test Application After Rollback

```bash
curl -f https://ai-dev.rdhcloudlab.com/api/health
```

**Expected Output**:
```json
{"status":"ok","service":"ai-app-backend"}
```

**Checkpoint**: ✅ PASS

---

## Troubleshooting

### Issue 1: Pods Not Starting

**Symptoms**: Pods in `Pending`, `CrashLoopBackOff`, or `ImagePullBackOff` state

**Diagnosis**:
```bash
kubectl get pods -n ai
kubectl describe pod <pod-name> -n ai
kubectl logs <pod-name> -n ai
```

**Common Causes**:
1. Image pull errors → Check ECR permissions
2. Resource constraints → Check node capacity
3. Application errors → Check logs

**Resolution Steps**:
```bash
# Check events
kubectl get events -n ai --sort-by='.lastTimestamp' | tail -20

# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n ai
```

**Checkpoint**: ✅ Resolved / ❌ Escalate

---

### Issue 2: Ingress Not Working

**Symptoms**: 503 errors, ALB not created, or DNS not resolving

**Diagnosis**:
```bash
kubectl get ingress -n ai
kubectl describe ingress ai-app-ingress -n ai
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
```

**Common Causes**:
1. ALB controller not running
2. Incorrect annotations
3. Target health issues

**Resolution Steps**:
```bash
# Check ALB controller
kubectl get deployment -n kube-system aws-load-balancer-controller

# Check ingress events
kubectl get events -n ai | grep ingress

# Check target health (see Checkpoint 16.3)
```

**Checkpoint**: ✅ Resolved / ❌ Escalate

---

### Issue 3: External Secrets Not Syncing

**Symptoms**: Secret not created, pods can't start due to missing secret

**Diagnosis**:
```bash
kubectl get externalsecret -n ai
kubectl describe externalsecret ai-app-external-secret -n ai
kubectl logs -n external-secrets -l app.kubernetes.io/name=external-secrets
```

**Common Causes**:
1. Secret doesn't exist in AWS Secrets Manager
2. IAM permissions missing
3. Wrong secret name

**Resolution Steps**:
```bash
# Verify secret in AWS
aws secretsmanager get-secret-value --secret-id ai-app/dev/openai

# Check IAM role
kubectl describe sa ai-app-sa -n ai

# Force sync
kubectl annotate externalsecret ai-app-external-secret -n ai \
  force-sync=$(date +%s) --overwrite
```

**Checkpoint**: ✅ Resolved / ❌ Escalate

---

### Issue 4: HPA Not Scaling

**Symptoms**: HPA shows `<unknown>` for metrics, not scaling

**Diagnosis**:
```bash
kubectl get hpa -n ai
kubectl describe hpa ai-app-backend-hpa -n ai
kubectl top pods -n ai
```

**Common Causes**:
1. Metrics server not running
2. Resource requests not defined
3. Insufficient load

**Resolution Steps**:
```bash
# Check metrics server
kubectl get deployment -n kube-system metrics-server

# Check metrics availability
kubectl top nodes
kubectl top pods -n ai

# Verify resource requests in deployment
kubectl get deployment ai-app-backend -n ai -o yaml | grep -A 5 resources
```

**Checkpoint**: ✅ Resolved / ❌ Escalate

---

## Summary Checklist

### Pre-Deployment (Checkpoints 1-9)
- [ ] Repository structure validated
- [ ] Helm chart linted successfully
- [ ] Backend code validated
- [ ] Frontend code validated
- [ ] CI/CD pipeline validated
- [ ] Security checks passed
- [ ] AWS infrastructure ready
- [ ] Secrets created
- [ ] Configuration updated

### Deployment (Checkpoints 10-11)
- [ ] Jenkins pipeline configured
- [ ] First deployment successful
- [ ] All pipeline stages passed

### Post-Deployment (Checkpoints 12-16)
- [ ] Kubernetes resources healthy
- [ ] Application endpoints responding
- [ ] Helm release deployed
- [ ] Logs available
- [ ] ALB targets healthy

### Rollback (Checkpoints 17-18)
- [ ] Current state documented
- [ ] Rollback procedure tested
- [ ] Application functional after rollback

---

## Appendix

### Quick Reference Commands

```bash
# Check everything
kubectl get all -n ai

# Get logs
kubectl logs -n ai -l app=ai-app-backend --tail=50 -f

# Port forward for local testing
kubectl port-forward -n ai svc/ai-app-backend 8000:8000

# Restart deployment
kubectl rollout restart deployment/ai-app-backend -n ai

# Scale deployment
kubectl scale deployment/ai-app-backend -n ai --replicas=3

# Delete and redeploy
helm uninstall ai-app -n ai
helm install ai-app ./helm/ai-app -n ai
```

### Contact Information

- **DevOps Team**: devops@rdhcloudlab.com
- **Slack Channel**: #ai-app-support
- **On-Call**: PagerDuty rotation

---

**End of Runbook**