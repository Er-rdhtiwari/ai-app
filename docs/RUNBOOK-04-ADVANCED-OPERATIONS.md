# Runbook 04: Advanced Operations and Troubleshooting

**Purpose**: Advanced scenarios, troubleshooting, and production best practices  
**Audience**: Senior DevOps Engineers, SREs  
**Duration**: Varies by scenario  
**Prerequisites**: Runbooks 01, 02, and 03 completed successfully

---

## Table of Contents

1. [Advanced Deployment Strategies](#advanced-deployment-strategies)
2. [Troubleshooting Guide](#troubleshooting-guide)
3. [Performance Optimization](#performance-optimization)
4. [Disaster Recovery](#disaster-recovery)
5. [Security Hardening](#security-hardening)
6. [Production Deployment](#production-deployment)

---

## Advanced Deployment Strategies

### Blue-Green Deployment

**Purpose**: Zero-downtime deployment with instant rollback capability

#### Step 1: Prepare Blue-Green Setup

```bash
# Current deployment (Blue)
kubectl get deployment ai-app-backend -n ai -o yaml > blue-deployment.yaml

# Create Green deployment
cp blue-deployment.yaml green-deployment.yaml

# Edit green-deployment.yaml
# Change:
# - name: ai-app-backend-green
# - labels: version: green
# - image tag: new version
```

#### Step 2: Deploy Green Version

```bash
# Deploy green version
kubectl apply -f green-deployment.yaml -n ai

# Wait for green pods to be ready
kubectl wait --for=condition=ready pod -l version=green -n ai --timeout=300s

# Test green version internally
kubectl run -it --rm test --image=curlimages/curl --restart=Never -- \
  curl http://ai-app-backend-green.ai.svc.cluster.local:8000/api/health
```

#### Step 3: Switch Traffic

```bash
# Update service selector to point to green
kubectl patch service ai-app-backend -n ai -p \
  '{"spec":{"selector":{"version":"green"}}}'

# Verify traffic switched
curl https://ai-dev.rdhcloudlab.com/api/health
```

#### Step 4: Cleanup or Rollback

```bash
# If successful, delete blue deployment
kubectl delete deployment ai-app-backend -n ai

# If issues, rollback
kubectl patch service ai-app-backend -n ai -p \
  '{"spec":{"selector":{"version":"blue"}}}'
```

**✅ Complete**: Blue-green deployment executed

---

### Canary Deployment

**Purpose**: Gradual rollout to subset of users

#### Step 1: Deploy Canary Version

```bash
# Scale down main deployment
kubectl scale deployment ai-app-backend -n ai --replicas=3

# Create canary deployment (1 replica)
kubectl create deployment ai-app-backend-canary -n ai \
  --image=123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-app-backend:new-version \
  --replicas=1

# Label canary pods
kubectl label pods -l app=ai-app-backend-canary -n ai version=canary
```

#### Step 2: Monitor Canary

```bash
# Watch canary logs
kubectl logs -n ai -l version=canary -f

# Monitor error rates
kubectl logs -n ai -l version=canary | grep -i error | wc -l

# Compare with stable version
kubectl logs -n ai -l app=ai-app-backend,version!=canary | grep -i error | wc -l
```

#### Step 3: Promote or Rollback

```bash
# If canary is healthy, promote
kubectl set image deployment/ai-app-backend -n ai \
  backend=123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-app-backend:new-version

# Delete canary
kubectl delete deployment ai-app-backend-canary -n ai

# If issues, just delete canary
kubectl delete deployment ai-app-backend-canary -n ai
```

**✅ Complete**: Canary deployment executed

---

## Troubleshooting Guide

### Issue 1: Pods Stuck in Pending State

**Symptoms**:
```bash
kubectl get pods -n ai
# NAME                               READY   STATUS    RESTARTS   AGE
# ai-app-backend-xxx-yyy            0/1     Pending   0          5m
```

**Diagnosis**:

```bash
# Check pod events
kubectl describe pod ai-app-backend-xxx-yyy -n ai

# Common causes in events:
# 1. "Insufficient cpu" or "Insufficient memory"
# 2. "No nodes available"
# 3. "FailedScheduling"
```

**Solution 1: Insufficient Resources**

```bash
# Check node capacity
kubectl top nodes

# Check resource requests
kubectl describe deployment ai-app-backend -n ai | grep -A 5 "Requests:"

# Solution: Reduce resource requests in values.yaml
cd ~/workspace/ai-app
nano helm/ai-app/values.yaml

# Change:
backend:
  resources:
    requests:
      cpu: 250m      # Reduce from 500m
      memory: 512Mi  # Reduce from 1Gi

# Commit and redeploy
git add helm/ai-app/values.yaml
git commit -m "Reduce backend resource requests"
git push origin main

# Trigger Jenkins build
```

**Solution 2: Node Scaling**

```bash
# Check node count
kubectl get nodes

# Scale EKS node group
aws eks update-nodegroup-config \
  --cluster-name rdh-eks-cluster \
  --nodegroup-name rdh-nodegroup \
  --scaling-config minSize=2,maxSize=5,desiredSize=3 \
  --region us-east-1
```

**✅ Resolved**: Pods now running

---

### Issue 2: CrashLoopBackOff

**Symptoms**:
```bash
kubectl get pods -n ai
# NAME                               READY   STATUS             RESTARTS   AGE
# ai-app-backend-xxx-yyy            0/1     CrashLoopBackOff   5          10m
```

**Diagnosis**:

```bash
# Check current logs
kubectl logs ai-app-backend-xxx-yyy -n ai

# Check previous container logs
kubectl logs ai-app-backend-xxx-yyy -n ai --previous

# Common errors:
# 1. "ModuleNotFoundError" - Missing dependencies
# 2. "Connection refused" - Can't connect to dependency
# 3. "Permission denied" - File permission issues
```

**Solution 1: Application Error**

```bash
# View detailed logs
kubectl logs ai-app-backend-xxx-yyy -n ai --previous | tail -50

# Example error: "ModuleNotFoundError: No module named 'fastapi'"

# Fix: Update requirements.txt
cd ~/workspace/ai-app/backend
nano requirements.txt
# Ensure all dependencies are listed

# Rebuild and redeploy
git add backend/requirements.txt
git commit -m "Fix missing dependencies"
git push origin main
# Trigger Jenkins build
```

**Solution 2: Configuration Error**

```bash
# Check environment variables
kubectl exec -n ai ai-app-backend-xxx-yyy -- env

# Check secret exists
kubectl get secret ai-app-secrets -n ai

# Check secret content
kubectl get secret ai-app-secrets -n ai -o yaml

# If secret missing, check External Secret
kubectl describe externalsecret ai-app-external-secret -n ai
```

**✅ Resolved**: Pods running successfully

---

### Issue 3: Ingress Not Working (503 Errors)

**Symptoms**:
```bash
curl https://ai-dev.rdhcloudlab.com/api/health
# HTTP/1.1 503 Service Temporarily Unavailable
```

**Diagnosis**:

```bash
# Check ingress
kubectl get ingress -n ai
kubectl describe ingress ai-app-ingress -n ai

# Check ALB
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?contains(LoadBalancerName, 'k8s-ai')].LoadBalancerArn" \
  --output text)

# Check target groups
aws elbv2 describe-target-groups --load-balancer-arn $ALB_ARN

# Check target health
TG_ARN=$(aws elbv2 describe-target-groups --load-balancer-arn $ALB_ARN \
  --query "TargetGroups[0].TargetGroupArn" --output text)

aws elbv2 describe-target-health --target-group-arn $TG_ARN
```

**Solution 1: Unhealthy Targets**

```bash
# Check pod readiness
kubectl get pods -n ai

# Check readiness probe
kubectl describe pod ai-app-backend-xxx-yyy -n ai | grep -A 10 "Readiness:"

# Test health endpoint from pod
kubectl exec -n ai ai-app-backend-xxx-yyy -- \
  curl -f http://localhost:8000/api/health

# If health check fails, check application logs
kubectl logs ai-app-backend-xxx-yyy -n ai
```

**Solution 2: Security Group Issues**

```bash
# Get ALB security group
SG_ID=$(aws elbv2 describe-load-balancers --load-balancer-arn $ALB_ARN \
  --query "LoadBalancers[0].SecurityGroups[0]" --output text)

# Check security group rules
aws ec2 describe-security-groups --group-ids $SG_ID

# Ensure inbound rules allow:
# - Port 80 from 0.0.0.0/0
# - Port 443 from 0.0.0.0/0

# Add rules if missing
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

**✅ Resolved**: Ingress working, returning 200 OK

---

### Issue 4: High Memory Usage / OOMKilled

**Symptoms**:
```bash
kubectl get pods -n ai
# NAME                               READY   STATUS      RESTARTS   AGE
# ai-app-backend-xxx-yyy            0/1     OOMKilled   3          15m
```

**Diagnosis**:

```bash
# Check pod events
kubectl describe pod ai-app-backend-xxx-yyy -n ai | grep -A 5 "Events:"

# Check memory usage
kubectl top pod ai-app-backend-xxx-yyy -n ai

# Check memory limits
kubectl describe deployment ai-app-backend -n ai | grep -A 5 "Limits:"
```

**Solution 1: Increase Memory Limits**

```bash
cd ~/workspace/ai-app
nano helm/ai-app/values.yaml

# Increase memory limits
backend:
  resources:
    limits:
      memory: 2Gi  # Increase from 1Gi

# Commit and redeploy
git add helm/ai-app/values.yaml
git commit -m "Increase backend memory limits"
git push origin main
# Trigger Jenkins build
```

**Solution 2: Fix Memory Leak**

```bash
# Profile application memory usage
kubectl exec -n ai ai-app-backend-xxx-yyy -- \
  python -m memory_profiler app/main.py

# Review code for memory leaks
# Common issues:
# - Large objects not being garbage collected
# - Circular references
# - Caching without limits
```

**✅ Resolved**: Pods running within memory limits

---

### Issue 5: External Secrets Not Syncing

**Symptoms**:
```bash
kubectl get externalsecret -n ai
# NAME                      STORE                  STATUS         READY
# ai-app-external-secret    aws-secrets-manager    SecretSyncedError   False
```

**Diagnosis**:

```bash
# Check External Secret status
kubectl describe externalsecret ai-app-external-secret -n ai

# Check External Secrets Operator logs
kubectl logs -n external-secrets -l app.kubernetes.io/name=external-secrets

# Common errors:
# 1. "AccessDeniedException" - IAM permissions
# 2. "ResourceNotFoundException" - Secret doesn't exist
# 3. "ValidationException" - Wrong secret format
```

**Solution 1: IAM Permissions**

```bash
# Check service account
kubectl describe sa ai-app-sa -n ai

# Check IAM role annotation
kubectl get sa ai-app-sa -n ai -o yaml | grep eks.amazonaws.com/role-arn

# If missing, add IAM role
kubectl annotate sa ai-app-sa -n ai \
  eks.amazonaws.com/role-arn=arn:aws:iam::123456789012:role/external-secrets-role

# Restart External Secrets Operator
kubectl rollout restart deployment -n external-secrets external-secrets
```

**Solution 2: Secret Format**

```bash
# Check secret in AWS
aws secretsmanager get-secret-value \
  --secret-id ai-app/dev/openai \
  --region us-east-1

# Ensure format is correct JSON
# Expected: {"openaiApiKey":"sk-..."}

# If wrong format, update
aws secretsmanager update-secret \
  --secret-id ai-app/dev/openai \
  --secret-string '{"openaiApiKey":"sk-correct-format"}' \
  --region us-east-1

# Force sync
kubectl annotate externalsecret ai-app-external-secret -n ai \
  force-sync=$(date +%s) --overwrite
```

**✅ Resolved**: Secret syncing successfully

---

## Performance Optimization

### Optimize Backend Performance

#### Step 1: Enable Caching

```python
# Edit backend/app/main.py
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_response(message: str):
    # Cache responses for repeated messages
    return process_message(message)
```

#### Step 2: Add Connection Pooling

```python
# Edit backend/app/settings.py
class Settings(BaseSettings):
    # Add connection pool settings
    pool_size: int = 10
    max_overflow: int = 20
```

#### Step 3: Optimize Docker Image

```dockerfile
# Edit backend/Dockerfile
# Use multi-stage build
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app/ ./app/
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Step 4: Tune HPA

```yaml
# Edit helm/ai-app/values.yaml
backend:
  autoscaling:
    enabled: true
    minReplicas: 3  # Increase minimum
    maxReplicas: 20  # Increase maximum
    targetCPUUtilizationPercentage: 60  # Lower threshold
    targetMemoryUtilizationPercentage: 70
```

**✅ Complete**: Performance optimizations applied

---

### Optimize Frontend Performance

#### Step 1: Enable Next.js Optimizations

```javascript
// Edit frontend/next.config.js
module.exports = {
  reactStrictMode: true,
  output: 'standalone',
  compress: true,
  poweredByHeader: false,
  generateEtags: true,
  images: {
    domains: ['ai-dev.rdhcloudlab.com'],
    formats: ['image/webp'],
  },
}
```

#### Step 2: Add Service Worker

```javascript
// Create frontend/public/sw.js
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('v1').then((cache) => {
      return cache.addAll(['/']);
    })
  );
});
```

**✅ Complete**: Frontend optimizations applied

---

## Disaster Recovery

### Backup Strategy

#### Step 1: Backup Helm Values

```bash
# Create backup script
cat > backup-helm-values.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="backups/helm-values"
mkdir -p $BACKUP_DIR

# Backup current values
helm get values ai-app -n ai > $BACKUP_DIR/values-$DATE.yaml

# Backup full release
helm get all ai-app -n ai > $BACKUP_DIR/release-$DATE.yaml

echo "Backup created: $BACKUP_DIR/values-$DATE.yaml"
EOF

chmod +x backup-helm-values.sh
./backup-helm-values.sh
```

#### Step 2: Backup Kubernetes Resources

```bash
# Backup all resources in namespace
kubectl get all -n ai -o yaml > backup-ai-namespace-$(date +%Y%m%d).yaml

# Backup secrets (encrypted)
kubectl get secrets -n ai -o yaml > backup-secrets-$(date +%Y%m%d).yaml
```

#### Step 3: Backup to S3

```bash
# Upload backups to S3
aws s3 cp backups/ s3://rdh-backups/ai-app/ --recursive

# Verify backup
aws s3 ls s3://rdh-backups/ai-app/
```

**✅ Complete**: Backups created and stored

---

### Disaster Recovery Procedure

#### Scenario: Complete Cluster Failure

**Step 1: Verify Backup Availability**

```bash
# List available backups
aws s3 ls s3://rdh-backups/ai-app/

# Download latest backup
aws s3 cp s3://rdh-backups/ai-app/helm-values/values-latest.yaml ./
```

**Step 2: Restore to New Cluster**

```bash
# Update kubeconfig for new cluster
aws eks update-kubeconfig --name rdh-eks-cluster-dr --region us-east-1

# Create namespace
kubectl create namespace ai

# Restore Helm release
helm install ai-app ./helm/ai-app \
  -n ai \
  -f values-latest.yaml

# Verify restoration
kubectl get all -n ai
```

**Step 3: Update DNS**

```bash
# Get new ALB DNS
NEW_ALB=$(kubectl get ingress ai-app-ingress -n ai \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Update Route53 (or your DNS provider)
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "ai-dev.rdhcloudlab.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "'$NEW_ALB'"}]
      }
    }]
  }'
```

**✅ Complete**: Application restored in DR cluster

---

## Security Hardening

### Enable Pod Security Standards

```yaml
# Create pod security policy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

### Enable Network Policies

```yaml
# Create network policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-app-network-policy
  namespace: ai
spec:
  podSelector:
    matchLabels:
      app: ai-app-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: ai-app-frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
```

**✅ Complete**: Security hardening applied

---

## Production Deployment

### Pre-Production Checklist

- [ ] **Code Quality**
  - [ ] All tests passing
  - [ ] Code reviewed
  - [ ] No security vulnerabilities
  - [ ] Performance tested

- [ ] **Infrastructure**
  - [ ] Production cluster ready
  - [ ] Monitoring configured
  - [ ] Alerting set up
  - [ ] Backups configured

- [ ] **Configuration**
  - [ ] Production secrets created
  - [ ] Resource limits appropriate
  - [ ] HPA configured
  - [ ] Network policies applied

- [ ] **Documentation**
  - [ ] Runbooks updated
  - [ ] Architecture documented
  - [ ] Incident response plan ready

### Production Deployment Steps

#### Step 1: Final Testing in Staging

```bash
# Deploy to staging
# Jenkins → Build with Parameters → ENV: stage

# Run load tests
kubectl run -it --rm load-test --image=williamyeh/wrk --restart=Never -- \
  wrk -t12 -c400 -d30s https://ai-stage.rdhcloudlab.com/api/health

# Monitor for 24 hours
# Check logs, metrics, errors
```

#### Step 2: Production Deployment

```bash
# Create production secrets
aws secretsmanager create-secret \
  --name ai-app/prod/openai \
  --secret-string '{"openaiApiKey":"sk-prod-key"}' \
  --region us-east-1

# Deploy to production
# Jenkins → Build with Parameters
# ENV: prod
# INGRESS_HOST: ai.rdhcloudlab.com
# Build
```

#### Step 3: Post-Deployment Monitoring

```bash
# Monitor for 1 hour minimum
watch -n 10 'kubectl get pods -n ai'

# Check logs continuously
kubectl logs -n ai -l app=ai-app-backend -f | grep -i error

# Monitor metrics
kubectl top pods -n ai

# Test endpoints
curl https://ai.rdhcloudlab.com/api/health
```

**✅ Complete**: Production deployment successful

---

## Summary

### What You've Learned

- ✅ Advanced deployment strategies (blue-green, canary)
- ✅ Comprehensive troubleshooting techniques
- ✅ Performance optimization methods
- ✅ Disaster recovery procedures
- ✅ Security hardening practices
- ✅ Production deployment best practices

### Key Takeaways

1. **Always test in staging first**
2. **Monitor after every deployment**
3. **Have rollback plan ready**
4. **Keep backups current**
5. **Document everything**
6. **Automate where possible**

---

**Runbook Version**: 1.0.0  
**Last Updated**: 2026-01-09  
**Next Review**: 2026-04-09