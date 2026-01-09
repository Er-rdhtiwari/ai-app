# Runbook 03: Day-to-Day Operations and Code Changes

**Purpose**: Guide for daily development workflow, code changes, and deployments  
**Audience**: Developers, DevOps Engineers  
**Duration**: Varies by task  
**Prerequisites**: Runbooks 01 and 02 completed successfully

---

## Table of Contents

1. [Overview](#overview)
2. [Development Workflow](#development-workflow)
3. [Making Code Changes](#making-code-changes)
4. [Deploying Changes](#deploying-changes)
5. [Monitoring and Verification](#monitoring-and-verification)
6. [Common Scenarios](#common-scenarios)

---

## Overview

### Daily Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Daily Workflow                       │
└─────────────────────────────────────────────────────────────┘

1. LOCAL DEVELOPMENT
   ↓
   Clone repo → Make changes → Test locally → Commit
   
2. PUSH TO GITHUB
   ↓
   git push origin main
   
3. JENKINS DEPLOYMENT
   ↓
   Trigger build → Monitor → Verify
   
4. VALIDATION
   ↓
   Test application → Check logs → Monitor metrics
```

### Where You Work

| Activity | Location | Tool |
|----------|----------|------|
| Code Changes | Your Local Machine | IDE (VS Code, etc.) |
| Git Operations | Your Local Machine | Terminal/Git |
| Trigger Deployments | Jenkins UI | Web Browser |
| Monitor Builds | Jenkins UI | Web Browser |
| Verify Deployments | Your Local Machine | Terminal/kubectl |
| View Application | Web Browser | Browser |

**Key Point**: You work on your local machine, push to GitHub, and use Jenkins UI to deploy. You don't need to log into the Jenkins server for normal operations.

---

## Development Workflow

### Scenario 1: Making a Backend Code Change

**Example**: Update the chat endpoint to return a different message

#### Step 1: Pull Latest Code

```bash
# Navigate to your local repository
cd ~/workspace/ai-app

# Pull latest changes from GitHub
git pull origin main

# Verify you're on main branch
git branch
# Expected: * main
```

**✅ Checkpoint 3.1**: Local repository is up to date

---

#### Step 2: Create Feature Branch (Best Practice)

```bash
# Create and switch to new branch
git checkout -b feature/update-chat-response

# Verify branch
git branch
# Expected: * feature/update-chat-response
```

**✅ Checkpoint 3.2**: Feature branch created

---

#### Step 3: Make Code Changes

**Edit File**: `backend/app/routers/chat.py`

```bash
# Open in your editor
code backend/app/routers/chat.py
# Or: vim, nano, etc.
```

**Example Change** (Line ~50):

```python
# BEFORE:
stub_answer = f"Echo: {chat_request.message} (This is a stub response. Configure OPENAI_API_KEY to enable AI responses.)"

# AFTER:
stub_answer = f"AI Response: {chat_request.message} - Thank you for your message! (Stub mode active)"
```

**Save the file**

**✅ Checkpoint 3.3**: Code changes made

---

#### Step 4: Test Locally (Optional but Recommended)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Expected Output:
# test_health.py::test_health_endpoint PASSED
# test_health.py::test_chat_endpoint_valid_message PASSED
# ... all tests PASSED

# Run application locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, test the endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Test"}' | jq

# Expected: New response message

# Stop the server (Ctrl+C)
deactivate
```

**✅ Checkpoint 3.4**: Changes tested locally

---

#### Step 5: Commit Changes

```bash
# Navigate back to repository root
cd ~/workspace/ai-app

# Check what changed
git status
# Expected: Modified: backend/app/routers/chat.py

# Review changes
git diff backend/app/routers/chat.py

# Stage changes
git add backend/app/routers/chat.py

# Commit with descriptive message
git commit -m "Update chat endpoint response message

- Changed stub response to be more user-friendly
- Updated message format for better clarity
- Tested locally and all tests pass"

# View commit
git log -1
```

**✅ Checkpoint 3.5**: Changes committed locally

---

#### Step 6: Push to GitHub

```bash
# Push feature branch to GitHub
git push origin feature/update-chat-response

# Expected Output:
# Enumerating objects: 7, done.
# Counting objects: 100% (7/7), done.
# ...
# To github.com:your-org/ai-app.git
#  * [new branch]      feature/update-chat-response -> feature/update-chat-response
```

**✅ Checkpoint 3.6**: Changes pushed to GitHub

---

#### Step 7: Create Pull Request (Best Practice)

**Location**: GitHub Web UI

```
1. Go to: https://github.com/your-org/ai-app

2. You'll see a banner:
   "feature/update-chat-response had recent pushes"
   [Compare & pull request]

3. Click "Compare & pull request"

4. Fill in PR details:
   Title: Update chat endpoint response message
   Description:
   - Changed stub response format
   - Improved user-friendly messaging
   - All tests passing

5. Click "Create pull request"

6. Request review from team member (optional)

7. After approval, click "Merge pull request"

8. Click "Confirm merge"

9. Delete branch (optional): Click "Delete branch"
```

**Alternative**: Merge directly to main (for small changes)

```bash
# Switch to main branch
git checkout main

# Merge feature branch
git merge feature/update-chat-response

# Push to GitHub
git push origin main

# Delete feature branch (optional)
git branch -d feature/update-chat-response
```

**✅ Checkpoint 3.7**: Changes merged to main branch

---

## Deploying Changes

### Step 8: Trigger Jenkins Deployment

**Location**: Jenkins UI (Web Browser)

#### Step 8.1: Access Jenkins

```
1. Open browser: http://jenkins.rdhcloudlab.com:8080

2. Login with admin credentials

3. Navigate to: ai-app-deploy job
```

#### Step 8.2: Start Build with Parameters

```
1. Click "Build with Parameters" (left sidebar)

2. Set parameters:
   ENV: dev
   AWS_REGION: us-east-1
   AWS_ACCOUNT_ID: [Your account ID]
   CLUSTER_NAME: rdh-eks-cluster
   NAMESPACE: ai
   INGRESS_HOST: ai-dev.rdhcloudlab.com

3. Click "Build"
```

**✅ Checkpoint 3.8**: Build triggered

---

#### Step 8.3: Monitor Build Progress

```
1. Build appears in "Build History" (e.g., #2)

2. Click on build number (#2)

3. Click "Console Output"

4. Watch stages execute:
   ✓ Validate Tools
   ✓ AWS Identity Check
   ✓ Backend Tests
   ✓ Build Frontend
   ✓ ECR Login
   ✓ Build and Push Backend Image
   ✓ Build and Push Frontend Image
   ✓ Update Kubeconfig
   ✓ Create Namespace
   ✓ Helm Deploy
   ✓ Verify Rollout
   ✓ Helm Status
   ✓ Verification Commands

5. Wait for "Finished: SUCCESS"
```

**Duration**: 10-15 minutes

**✅ Checkpoint 3.9**: Build completed successfully

---

### Step 9: Verify Deployment

#### Step 9.1: Check from Jenkins Console

```
Scroll to bottom of Console Output

Look for:
========================================
DEPLOYMENT COMPLETE!
========================================
Environment: dev
Backend Image: ...abc123 (new git SHA)
Frontend Image: ...abc123 (new git SHA)
Access your application at: https://ai-dev.rdhcloudlab.com
========================================
```

**✅ Checkpoint 3.10**: Deployment confirmed in Jenkins

---

#### Step 9.2: Verify with kubectl

```bash
# From your local machine (with kubectl configured)

# Check pods are running with new image
kubectl get pods -n ai

# Check pod age (should be recent)
# Expected: AGE column shows "2m" or similar

# Describe pod to see image tag
kubectl describe pod -n ai -l app=ai-app-backend | grep Image:
# Expected: Image with new git SHA

# Check rollout status
kubectl rollout status deployment/ai-app-backend -n ai
# Expected: deployment "ai-app-backend" successfully rolled out
```

**✅ Checkpoint 3.11**: Pods running with new version

---

#### Step 9.3: Test Application

```bash
# Test backend health
curl https://ai-dev.rdhcloudlab.com/api/health

# Expected:
# {"status":"ok","service":"ai-app-backend"}

# Test chat endpoint with new message
curl -X POST https://ai-dev.rdhcloudlab.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}' | jq

# Expected: New response format
# {
#   "answer": "AI Response: Hello - Thank you for your message! (Stub mode active)",
#   "trace_id": "..."
# }
```

**✅ Checkpoint 3.12**: Application responding with new code

---

#### Step 9.4: Browser Test

```
1. Open browser: https://ai-dev.rdhcloudlab.com

2. Enter message: "Test message"

3. Click "Send Message"

4. Verify response shows new format

5. Check trace ID is displayed
```

**✅ Checkpoint 3.13**: UI working with new backend

---

## Monitoring and Verification

### Continuous Monitoring

#### Check Application Logs

```bash
# Backend logs
kubectl logs -n ai -l app=ai-app-backend --tail=50 -f

# Frontend logs
kubectl logs -n ai -l app=ai-app-frontend --tail=50 -f

# All logs
kubectl logs -n ai --all-containers=true --tail=100

# Stop following logs: Ctrl+C
```

#### Check Pod Status

```bash
# Get pod status
kubectl get pods -n ai

# Get detailed pod info
kubectl describe pod <pod-name> -n ai

# Check pod events
kubectl get events -n ai --sort-by='.lastTimestamp' | tail -20
```

#### Check Service Status

```bash
# Get services
kubectl get svc -n ai

# Test service internally
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://ai-app-backend.ai.svc.cluster.local:8000/api/health
```

#### Check Ingress Status

```bash
# Get ingress
kubectl get ingress -n ai

# Describe ingress
kubectl describe ingress ai-app-ingress -n ai

# Check ALB
aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?contains(LoadBalancerName, 'k8s-ai')]" \
  --output table
```

---

## Common Scenarios

### Scenario 2: Updating Frontend UI

**Example**: Change the page title

#### Step 1: Make Changes

```bash
cd ~/workspace/ai-app

# Create branch
git checkout -b feature/update-page-title

# Edit file
code frontend/pages/index.js

# Change line ~52:
# BEFORE: <title>AI App</title>
# AFTER: <title>AI Chat Assistant</title>

# Save file
```

#### Step 2: Test Locally (Optional)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Run dev server
npm run dev

# Open browser: http://localhost:3000
# Verify title changed

# Stop server: Ctrl+C
```

#### Step 3: Commit and Push

```bash
cd ~/workspace/ai-app

git add frontend/pages/index.js
git commit -m "Update page title to 'AI Chat Assistant'"
git push origin feature/update-page-title

# Merge to main (via PR or directly)
git checkout main
git merge feature/update-page-title
git push origin main
```

#### Step 4: Deploy via Jenkins

```
1. Jenkins UI → ai-app-deploy
2. Build with Parameters
3. Same parameters as before
4. Build
5. Wait for SUCCESS
6. Verify: https://ai-dev.rdhcloudlab.com (check browser tab title)
```

**✅ Complete**: Frontend updated and deployed

---

### Scenario 3: Updating Helm Configuration

**Example**: Increase backend replicas from 2 to 3

#### Step 1: Update Values

```bash
cd ~/workspace/ai-app

git checkout -b config/increase-backend-replicas

# Edit file
code helm/ai-app/values.yaml

# Change line ~15:
# BEFORE: replicaCount: 2
# AFTER: replicaCount: 3

# Save file
```

#### Step 2: Commit and Push

```bash
git add helm/ai-app/values.yaml
git commit -m "Increase backend replicas to 3 for better availability"
git push origin config/increase-backend-replicas

# Merge to main
git checkout main
git merge config/increase-backend-replicas
git push origin main
```

#### Step 3: Deploy via Jenkins

```
Same as before - Jenkins will use updated values.yaml
```

#### Step 4: Verify

```bash
# Check pod count
kubectl get pods -n ai -l app=ai-app-backend

# Expected: 3 pods running
```

**✅ Complete**: Configuration updated and deployed

---

### Scenario 4: Deploying to Different Environment

**Example**: Deploy to staging environment

#### Step 1: Ensure Code is Ready

```bash
# Make sure main branch has all changes
git checkout main
git pull origin main
```

#### Step 2: Update Secrets (if needed)

```bash
# Verify staging secret exists
aws secretsmanager get-secret-value \
  --secret-id ai-app/stage/openai \
  --region us-east-1

# If not exists, create it
aws secretsmanager create-secret \
  --name ai-app/stage/openai \
  --secret-string '{"openaiApiKey":"sk-stage-key"}' \
  --region us-east-1
```

#### Step 3: Deploy via Jenkins

```
1. Jenkins UI → ai-app-deploy
2. Build with Parameters
3. Change parameters:
   ENV: stage  ← Changed
   AWS_REGION: us-east-1
   AWS_ACCOUNT_ID: [Your account ID]
   CLUSTER_NAME: rdh-eks-cluster
   NAMESPACE: ai  ← Or use 'ai-stage' for isolation
   INGRESS_HOST: ai-stage.rdhcloudlab.com  ← Changed
4. Build
5. Wait for SUCCESS
```

#### Step 4: Verify

```bash
# Check staging namespace
kubectl get pods -n ai

# Test staging endpoint
curl https://ai-stage.rdhcloudlab.com/api/health
```

**✅ Complete**: Deployed to staging environment

---

### Scenario 5: Rolling Back a Deployment

**Example**: New deployment has issues, need to rollback

#### Step 5.1: Identify Issue

```bash
# Check pod status
kubectl get pods -n ai

# Check logs for errors
kubectl logs -n ai -l app=ai-app-backend --tail=100 | grep -i error

# Test endpoint
curl https://ai-dev.rdhcloudlab.com/api/health
# If returns error or timeout, rollback needed
```

#### Step 5.2: Rollback via Helm

```bash
# Check Helm history
helm history ai-app -n ai

# Expected:
# REVISION  UPDATED                   STATUS      CHART         DESCRIPTION
# 1         2026-01-09 09:30:00 IST   superseded  ai-app-1.0.0  Install complete
# 2         2026-01-09 10:45:00 IST   deployed    ai-app-1.0.0  Upgrade complete

# Rollback to previous revision
helm rollback ai-app -n ai

# Or rollback to specific revision
helm rollback ai-app 1 -n ai
```

#### Step 5.3: Verify Rollback

```bash
# Check rollout status
kubectl rollout status deployment/ai-app-backend -n ai
kubectl rollout status deployment/ai-app-frontend -n ai

# Check pods
kubectl get pods -n ai

# Test application
curl https://ai-dev.rdhcloudlab.com/api/health
```

#### Step 5.4: Rollback via Jenkins (Alternative)

```
1. Jenkins UI → ai-app-deploy
2. Find last successful build (e.g., #5)
3. Click on build #5
4. Click "Rebuild" button
5. Confirm parameters
6. Build
7. This redeploys the previous working version
```

**✅ Complete**: Rolled back to previous working version

---

### Scenario 6: Viewing Build History

**Purpose**: See all previous deployments

#### From Jenkins UI

```
1. Jenkins UI → ai-app-deploy

2. View "Build History" (left sidebar)
   #10 - 2 hours ago - SUCCESS
   #9  - 5 hours ago - SUCCESS
   #8  - 1 day ago - FAILURE
   #7  - 1 day ago - SUCCESS

3. Click on any build to see:
   - Console Output
   - Changes (git commits)
   - Parameters used
   - Duration
   - Artifacts (if any)

4. Click "Changes" to see git commits in that build
```

#### From kubectl

```bash
# Check Helm release history
helm history ai-app -n ai

# Check deployment rollout history
kubectl rollout history deployment/ai-app-backend -n ai
```

**✅ Complete**: Reviewed deployment history

---

### Scenario 7: Updating Secrets

**Example**: Rotate OpenAI API key

#### Step 1: Update Secret in AWS

```bash
# Update existing secret
aws secretsmanager update-secret \
  --secret-id ai-app/dev/openai \
  --secret-string '{"openaiApiKey":"sk-new-api-key-here"}' \
  --region us-east-1

# Verify update
aws secretsmanager get-secret-value \
  --secret-id ai-app/dev/openai \
  --region us-east-1 \
  --query 'SecretString' --output text
```

#### Step 2: Force Secret Sync

```bash
# External Secrets Operator will sync automatically (default: 1 hour)
# To force immediate sync:

kubectl annotate externalsecret ai-app-external-secret -n ai \
  force-sync=$(date +%s) --overwrite

# Verify secret updated
kubectl get secret ai-app-secrets -n ai -o yaml
```

#### Step 3: Restart Pods (if needed)

```bash
# Restart backend deployment to pick up new secret
kubectl rollout restart deployment/ai-app-backend -n ai

# Wait for rollout
kubectl rollout status deployment/ai-app-backend -n ai
```

**✅ Complete**: Secret rotated and pods restarted

---

## Best Practices

### 1. Branch Strategy

```
main (production-ready code)
  ↓
feature/feature-name (new features)
bugfix/bug-description (bug fixes)
config/config-change (configuration updates)
```

### 2. Commit Messages

```
Good:
✓ "Add user authentication to chat endpoint"
✓ "Fix memory leak in backend service"
✓ "Update Helm chart to support HPA"

Bad:
✗ "Update"
✗ "Fix bug"
✗ "Changes"
```

### 3. Testing Before Deploy

```
Always test locally:
1. Run unit tests: pytest
2. Run application: uvicorn app.main:app
3. Test endpoints: curl
4. Check logs for errors
```

### 4. Deployment Timing

```
Best times to deploy:
✓ During business hours (for immediate issue detection)
✓ After code review
✓ After successful tests

Avoid:
✗ Friday evenings
✗ Before holidays
✗ During high-traffic periods
```

### 5. Monitoring After Deploy

```
After deployment, monitor for 15-30 minutes:
1. Check pod status
2. Review logs
3. Test endpoints
4. Monitor error rates
5. Check resource usage
```

---

## Quick Reference Commands

### Git Operations

```bash
# Pull latest
git pull origin main

# Create branch
git checkout -b feature/my-feature

# Stage changes
git add .

# Commit
git commit -m "Description"

# Push
git push origin feature/my-feature

# Merge to main
git checkout main
git merge feature/my-feature
git push origin main
```

### Jenkins Operations

```
Access: http://jenkins.rdhcloudlab.com:8080
Job: ai-app-deploy
Action: Build with Parameters
Monitor: Console Output
```

### Kubernetes Operations

```bash
# Check pods
kubectl get pods -n ai

# Check logs
kubectl logs -n ai -l app=ai-app-backend --tail=50 -f

# Check services
kubectl get svc -n ai

# Check ingress
kubectl get ingress -n ai

# Restart deployment
kubectl rollout restart deployment/ai-app-backend -n ai

# Rollback
helm rollback ai-app -n ai
```

### Testing

```bash
# Health check
curl https://ai-dev.rdhcloudlab.com/api/health

# Chat endpoint
curl -X POST https://ai-dev.rdhcloudlab.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}' | jq
```

---

## Summary Checklist

### For Each Code Change
- [ ] Pull latest code from main
- [ ] Create feature branch
- [ ] Make code changes
- [ ] Test locally
- [ ] Commit with descriptive message
- [ ] Push to GitHub
- [ ] Create/merge pull request
- [ ] Trigger Jenkins build
- [ ] Monitor build progress
- [ ] Verify deployment
- [ ] Test application
- [ ] Monitor for issues

### For Each Deployment
- [ ] Ensure code is in main branch
- [ ] Access Jenkins UI
- [ ] Select correct environment
- [ ] Set correct parameters
- [ ] Trigger build
- [ ] Monitor console output
- [ ] Wait for SUCCESS
- [ ] Verify with kubectl
- [ ] Test application endpoints
- [ ] Monitor logs for 15-30 minutes

---

## What You've Learned

After completing this runbook:
- ✅ How to make code changes locally
- ✅ How to commit and push changes
- ✅ How to trigger deployments via Jenkins
- ✅ How to monitor and verify deployments
- ✅ How to handle common scenarios
- ✅ How to rollback if needed
- ✅ Best practices for daily operations

---

## Next Steps

Proceed to **Runbook 04: Advanced Operations and Troubleshooting** to learn:
- Advanced debugging techniques
- Performance optimization
- Disaster recovery
- Production deployment strategies

---

**Runbook Version**: 1.0.0  
**Last Updated**: 2026-01-09  
**Next Review**: 2026-04-09