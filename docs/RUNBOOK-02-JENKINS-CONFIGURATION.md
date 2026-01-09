# Runbook 02: Jenkins Configuration and Pipeline Setup

**Purpose**: Configure Jenkins to use the ai-app repository and set up the deployment pipeline  
**Audience**: Jenkins Administrators, DevOps Engineers  
**Duration**: 20-30 minutes  
**Prerequisites**: Runbook 01 completed successfully

---

## Table of Contents

1. [Overview](#overview)
2. [Access Methods](#access-methods)
3. [Jenkins Job Configuration](#jenkins-job-configuration)
4. [Pipeline Testing](#pipeline-testing)
5. [Validation](#validation)

---

## Overview

### What You'll Do

In this runbook, you will:
1. Access Jenkins UI as an administrator
2. Create a new Pipeline job
3. Configure the job to read from the ai-app repository
4. Set up job parameters
5. Test the pipeline with a dry-run
6. Execute the first deployment

### Jenkins and Repository Relationship

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Workflow                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        ↓                                           ↓
┌───────────────────┐                    ┌──────────────────┐
│  Jenkins UI       │                    │ Jenkins Server   │
│  (Web Browser)    │                    │ (SSH/CLI)        │
│                   │                    │                  │
│  - Create Jobs    │                    │  - View Logs     │
│  - Trigger Builds │                    │  - Debug Issues  │
│  - View Results   │                    │  - Check Files   │
└───────────────────┘                    └──────────────────┘
        ↓                                           ↓
        └─────────────────────┬─────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │ Jenkins Pipeline │
                    │ Reads Jenkinsfile│
                    │ from GitHub      │
                    └──────────────────┘
```

**Key Point**: You'll primarily use the **Jenkins UI** for configuration and monitoring. You'll only need **SSH access to Jenkins server** for troubleshooting.

---

## Access Methods

### Method 1: Jenkins UI Access (Primary Method)

**When to Use**: 
- Creating and configuring jobs
- Triggering builds
- Viewing build results
- Managing Jenkins settings

**How to Access**:

```bash
# Open your web browser and navigate to:
http://jenkins.rdhcloudlab.com:8080
# Or
https://jenkins.rdhcloudlab.com

# If Jenkins is on localhost:
http://localhost:8080
```

**Login Credentials**:
- Username: `admin` (or your Jenkins admin username)
- Password: [Your Jenkins admin password]

**✅ Checkpoint 2.1**: Successfully logged into Jenkins UI

---

### Method 2: Jenkins Server CLI Access (Troubleshooting Only)

**When to Use**:
- Debugging pipeline failures
- Checking file permissions
- Viewing detailed logs
- Installing additional tools

**How to Access**:

```bash
# SSH to Jenkins server
ssh -i ~/.ssh/jenkins-key.pem ec2-user@jenkins.rdhcloudlab.com

# Or if Jenkins is on local machine
# Just open terminal

# Verify you're on Jenkins server
hostname
# Expected: jenkins.rdhcloudlab.com or similar

# Check Jenkins home directory
ls -la /var/lib/jenkins/
# Expected: jobs/, workspace/, plugins/, etc.
```

**✅ Checkpoint 2.2**: Can access Jenkins server via SSH (if needed)

---

## Jenkins Job Configuration

### Step 1: Create New Pipeline Job

**Location**: Jenkins UI (Web Browser)

**Step 1.1**: Navigate to Jenkins Dashboard

```
1. Open Jenkins UI: http://jenkins.rdhcloudlab.com:8080
2. Login with admin credentials
3. You should see the Jenkins Dashboard
```

**Step 1.2**: Create New Item

```
1. Click "New Item" in the left sidebar
   (or click "Create a job" if this is your first job)

2. Enter job name: ai-app-deploy

3. Select "Pipeline" as the job type

4. Click "OK" at the bottom
```

**✅ Checkpoint 2.3**: New pipeline job created

**Screenshot Reference**:
```
┌─────────────────────────────────────────────┐
│ Jenkins                                      │
├─────────────────────────────────────────────┤
│ New Item                                     │
│                                              │
│ Enter an item name:                          │
│ ┌─────────────────────────────────────────┐ │
│ │ ai-app-deploy                           │ │
│ └─────────────────────────────────────────┘ │
│                                              │
│ ○ Freestyle project                          │
│ ● Pipeline                                   │
│ ○ Multi-configuration project               │
│                                              │
│                          [OK]    [Cancel]    │
└─────────────────────────────────────────────┘
```

---

### Step 2: Configure General Settings

**Location**: Jenkins UI → ai-app-deploy → Configure

**Step 2.1**: Add Description

```
Description:
AI App deployment pipeline for FastAPI backend and Next.js frontend.
Deploys to AWS EKS using Helm charts.

Environments: dev, stage, prod
```

**Step 2.2**: Configure GitHub Project (Optional)

```
☑ GitHub project
Project url: https://github.com/your-org/ai-app
```

**Step 2.3**: Configure Build Triggers (Optional)

```
☑ GitHub hook trigger for GITScm polling
(This allows automatic builds when you push to GitHub)
```

**✅ Checkpoint 2.4**: General settings configured

---

### Step 3: Configure Pipeline Parameters

**Location**: Jenkins UI → ai-app-deploy → Configure → General

**Step 3.1**: Enable Parameters

```
☑ This project is parameterized
```

**Step 3.2**: Add Parameters (Click "Add Parameter" for each)

**Parameter 1: ENV**
```
Type: Choice Parameter
Name: ENV
Choices: (one per line)
  dev
  stage
  prod
Description: Deployment environment
```

**Parameter 2: AWS_REGION**
```
Type: String Parameter
Name: AWS_REGION
Default Value: us-east-1
Description: AWS Region for deployment
```

**Parameter 3: AWS_ACCOUNT_ID**
```
Type: String Parameter
Name: AWS_ACCOUNT_ID
Default Value: 123456789012
Description: AWS Account ID (update with your actual account ID)
```

**Parameter 4: CLUSTER_NAME**
```
Type: String Parameter
Name: CLUSTER_NAME
Default Value: rdh-eks-cluster
Description: EKS Cluster Name
```

**Parameter 5: NAMESPACE**
```
Type: String Parameter
Name: NAMESPACE
Default Value: ai
Description: Kubernetes namespace for deployment
```

**Parameter 6: INGRESS_HOST**
```
Type: String Parameter
Name: INGRESS_HOST
Default Value: ai-dev.rdhcloudlab.com
Description: Ingress hostname (update based on environment)
```

**✅ Checkpoint 2.5**: All 6 parameters configured

**Visual Reference**:
```
┌─────────────────────────────────────────────────────────┐
│ This project is parameterized                            │
├─────────────────────────────────────────────────────────┤
│ Choice Parameter                                         │
│ Name: ENV                                                │
│ Choices: dev                                             │
│          stage                                           │
│          prod                                            │
│ Description: Deployment environment                      │
├─────────────────────────────────────────────────────────┤
│ String Parameter                                         │
│ Name: AWS_REGION                                         │
│ Default Value: us-east-1                                 │
│ Description: AWS Region for deployment                   │
├─────────────────────────────────────────────────────────┤
│ ... (4 more parameters)                                  │
└─────────────────────────────────────────────────────────┘
```

---

### Step 4: Configure Pipeline Definition

**Location**: Jenkins UI → ai-app-deploy → Configure → Pipeline

**Step 4.1**: Set Pipeline Definition

```
Definition: Pipeline script from SCM
```

**Step 4.2**: Configure SCM

```
SCM: Git

Repository URL: https://github.com/your-org/ai-app.git
(Or use SSH: git@github.com:your-org/ai-app.git)

Credentials: 
  - If public repo: none
  - If private repo: Add GitHub credentials
    (Click "Add" → Jenkins → Username with password or SSH key)

Branches to build:
  Branch Specifier: */main
  (or */master depending on your default branch)
```

**Step 4.3**: Configure Script Path

```
Script Path: Jenkinsfile

☑ Lightweight checkout
(This makes Jenkins only checkout the Jenkinsfile initially)
```

**✅ Checkpoint 2.6**: Pipeline definition configured

**Visual Reference**:
```
┌─────────────────────────────────────────────────────────┐
│ Pipeline                                                 │
├─────────────────────────────────────────────────────────┤
│ Definition: Pipeline script from SCM                     │
│                                                          │
│ SCM: Git                                                 │
│                                                          │
│ Repository URL:                                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ https://github.com/your-org/ai-app.git           │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ Credentials: - none -                                    │
│                                                          │
│ Branches to build:                                       │
│ Branch Specifier: */main                                 │
│                                                          │
│ Script Path: Jenkinsfile                                 │
│                                                          │
│ ☑ Lightweight checkout                                  │
└─────────────────────────────────────────────────────────┘
```

---

### Step 5: Save Configuration

**Step 5.1**: Review Settings

```
Scroll through the configuration page and verify:
- Job name: ai-app-deploy
- 6 parameters configured
- Pipeline reads from Git repository
- Script path is Jenkinsfile
```

**Step 5.2**: Save

```
Click "Save" button at the bottom of the page
```

**Step 5.3**: Verify Job Created

```
You should be redirected to the job page:
http://jenkins.rdhcloudlab.com:8080/job/ai-app-deploy/

You should see:
- Job name at the top
- "Build with Parameters" button in the left sidebar
- No builds yet (empty build history)
```

**✅ Checkpoint 2.7**: Job configuration saved successfully

---

## Pipeline Testing

### Step 6: Dry-Run Test (Validation Only)

**Purpose**: Test that Jenkins can read the Jenkinsfile without actually deploying

**Step 6.1**: Access Job Page

```
Navigate to: http://jenkins.rdhcloudlab.com:8080/job/ai-app-deploy/
```

**Step 6.2**: Click "Build with Parameters"

```
You should see a form with all 6 parameters
```

**Step 6.3**: Set Parameters for Dry-Run

```
ENV: dev
AWS_REGION: us-east-1
AWS_ACCOUNT_ID: [Your actual AWS account ID]
CLUSTER_NAME: rdh-eks-cluster
NAMESPACE: ai
INGRESS_HOST: ai-dev.rdhcloudlab.com
```

**Step 6.4**: Start Build

```
Click "Build" button at the bottom
```

**Step 6.5**: Monitor Build

```
1. You'll see a new build appear in "Build History" (left sidebar)
   Example: #1

2. Click on the build number (#1)

3. Click "Console Output" to see real-time logs

4. Watch the pipeline execute each stage
```

**Expected Output in Console**:
```
Started by user admin
Running in Durability level: MAX_SURVIVABILITY
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in /var/lib/jenkins/workspace/ai-app-deploy
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Declarative: Checkout SCM)
[Pipeline] checkout
Cloning repository https://github.com/your-org/ai-app.git
...
[Pipeline] stage
[Pipeline] { (Validate Tools)
[Pipeline] sh
+ aws --version
aws-cli/2.13.0 Python/3.11.4 Linux/5.10.0-1160.el7.x86_64
+ docker --version
Docker version 24.0.5, build ced0996
...
```

**✅ Checkpoint 2.8**: Pipeline starts and validates tools successfully

---

### Step 7: Monitor Pipeline Stages

**Location**: Jenkins UI → Build #1 → Console Output

**Expected Stages** (in order):

```
Stage 1: Validate Tools ✓
  - Checks aws, docker, kubectl, helm, git

Stage 2: AWS Identity Check ✓
  - Verifies AWS credentials
  - Shows account ID and region

Stage 3: Backend Tests ✓
  - Creates Python virtual environment
  - Installs dependencies
  - Runs pytest

Stage 4: Build Frontend ✓
  - Installs npm dependencies
  - Runs linting

Stage 5: ECR Login ✓
  - Authenticates to AWS ECR

Stage 6: Build and Push Backend Image ✓
  - Builds Docker image
  - Tags with git commit SHA
  - Pushes to ECR

Stage 7: Build and Push Frontend Image ✓
  - Builds Docker image
  - Tags with git commit SHA
  - Pushes to ECR

Stage 8: Update Kubeconfig ✓
  - Configures kubectl for EKS

Stage 9: Create Namespace ✓
  - Creates 'ai' namespace if not exists

Stage 10: Helm Deploy ✓
  - Deploys application using Helm
  - Sets image tags and configuration

Stage 11: Verify Rollout ✓
  - Waits for pods to be ready
  - Checks deployment status

Stage 12: Helm Status ✓
  - Shows Helm release information

Stage 13: Verification Commands ✓
  - Prints commands to verify deployment
  - Tests health endpoint
```

**Duration**: Approximately 10-15 minutes for first build

**✅ Checkpoint 2.9**: All stages complete successfully

---

### Step 8: Verify Build Success

**Step 8.1**: Check Build Status

```
Location: Jenkins UI → ai-app-deploy → Build #1

Look for:
- Blue ball icon (success) or Red ball icon (failure)
- "SUCCESS" in console output
- All stages marked with ✓
```

**Step 8.2**: Review Console Output

```
Scroll to the bottom of Console Output

Expected final messages:
========================================
DEPLOYMENT COMPLETE!
========================================
Environment: dev
Namespace: ai
Backend Image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-app-backend:abc123
Frontend Image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-app-frontend:abc123
Ingress Host: ai-dev.rdhcloudlab.com

Access your application at: https://ai-dev.rdhcloudlab.com
========================================
Finished: SUCCESS
```

**✅ Checkpoint 2.10**: Build completed successfully

---

### Step 9: Verify Deployment (Quick Check)

**Step 9.1**: Check from Jenkins Console Output

```
Look for the "ACTUAL RESOURCE STATUS" section in console output

Expected:
NAME                               READY   STATUS    RESTARTS   AGE
pod/ai-app-backend-xxx-yyy        1/1     Running   0          2m
pod/ai-app-backend-xxx-zzz        1/1     Running   0          2m
pod/ai-app-frontend-aaa-bbb       1/1     Running   0          2m
pod/ai-app-frontend-aaa-ccc       1/1     Running   0          2m

NAME                      TYPE        CLUSTER-IP       PORT(S)
service/ai-app-backend    ClusterIP   10.100.x.x       8000/TCP
service/ai-app-frontend   ClusterIP   10.100.y.y       3000/TCP
```

**Step 9.2**: Test Health Endpoint (from Console Output)

```
Look for "TESTING BACKEND HEALTH ENDPOINT" section

Expected:
{"status":"ok","service":"ai-app-backend"}
```

**✅ Checkpoint 2.11**: Application deployed and responding

---

## Validation

### Validation from Jenkins UI

**Checkpoint 2.12**: Job Configuration Validation

```
Navigate to: Jenkins → ai-app-deploy → Configure

Verify:
☑ Job name is "ai-app-deploy"
☑ 6 parameters are configured
☑ Pipeline definition is "Pipeline script from SCM"
☑ Repository URL is correct
☑ Branch is */main
☑ Script Path is "Jenkinsfile"
```

**Checkpoint 2.13**: Build History Validation

```
Navigate to: Jenkins → ai-app-deploy

Verify:
☑ At least one build in history
☑ Build #1 shows blue ball (success)
☑ Build duration is reasonable (10-15 minutes)
☑ Console output is accessible
```

---

### Validation from Jenkins Server (CLI)

**Only if you need to troubleshoot**

**Checkpoint 2.14**: Workspace Validation

```bash
# SSH to Jenkins server
ssh ec2-user@jenkins.rdhcloudlab.com

# Check workspace
ls -la /var/lib/jenkins/workspace/ai-app-deploy/

# Expected: Repository files
# backend/  frontend/  helm/  Jenkinsfile  README.md  etc.
```

**Checkpoint 2.15**: Build Logs Validation

```bash
# Check build logs directory
ls -la /var/lib/jenkins/jobs/ai-app-deploy/builds/

# Expected: Directories for each build (1, 2, 3, etc.)

# View specific build log
cat /var/lib/jenkins/jobs/ai-app-deploy/builds/1/log
```

---

### Validation from kubectl (Application Level)

**Checkpoint 2.16**: Kubernetes Resources Validation

```bash
# From your local machine or Jenkins server
# (wherever kubectl is configured)

# Check namespace
kubectl get namespace ai

# Check pods
kubectl get pods -n ai

# Expected:
# NAME                               READY   STATUS    RESTARTS   AGE
# ai-app-backend-xxx-yyy            1/1     Running   0          5m
# ai-app-backend-xxx-zzz            1/1     Running   0          5m
# ai-app-frontend-aaa-bbb           1/1     Running   0          5m
# ai-app-frontend-aaa-ccc           1/1     Running   0          5m

# Check services
kubectl get svc -n ai

# Check ingress
kubectl get ingress -n ai
```

**✅ Checkpoint 2.17**: All Kubernetes resources are healthy

---

## Troubleshooting Common Issues

### Issue 1: "Permission Denied" When Cloning Repository

**Symptoms**: Build fails at "Checkout SCM" stage

**Diagnosis**:
```
Console Output shows:
ERROR: Error cloning remote repo 'origin'
Permission denied (publickey)
```

**Solution**:

**Option A: Use HTTPS (Public Repo)**
```
1. Go to Jenkins → ai-app-deploy → Configure
2. Change Repository URL to HTTPS:
   https://github.com/your-org/ai-app.git
3. Save
4. Rebuild
```

**Option B: Add SSH Credentials (Private Repo)**
```
1. Go to Jenkins → Manage Jenkins → Credentials
2. Click "System" → "Global credentials"
3. Click "Add Credentials"
4. Kind: SSH Username with private key
5. ID: github-ssh-key
6. Username: git
7. Private Key: Enter directly (paste your SSH private key)
8. Click "OK"

9. Go back to job configuration
10. Repository URL: git@github.com:your-org/ai-app.git
11. Credentials: Select "github-ssh-key"
12. Save and rebuild
```

---

### Issue 2: "AWS Credentials Not Found"

**Symptoms**: Build fails at "AWS Identity Check" stage

**Diagnosis**:
```
Console Output shows:
Unable to locate credentials
```

**Solution**:

**Option A: Use IAM Role (Recommended)**
```
1. SSH to Jenkins server
2. Verify IAM role is attached:
   aws sts get-caller-identity
   
3. If not attached, attach IAM role to Jenkins EC2 instance:
   - Go to AWS Console → EC2 → Instances
   - Select Jenkins instance
   - Actions → Security → Modify IAM role
   - Attach role with ECR, EKS, Secrets Manager permissions
```

**Option B: Add AWS Credentials to Jenkins**
```
1. Go to Jenkins → Manage Jenkins → Credentials
2. Add AWS credentials
3. Update Jenkinsfile to use credentials
   (Not recommended for production)
```

---

### Issue 3: "Docker Command Not Found"

**Symptoms**: Build fails at "Build and Push Backend Image" stage

**Diagnosis**:
```
Console Output shows:
docker: command not found
```

**Solution**:
```bash
# SSH to Jenkins server
ssh ec2-user@jenkins.rdhcloudlab.com

# Install Docker
sudo yum install docker -y

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add Jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# Rebuild job
```

---

### Issue 4: "Helm Deploy Timeout"

**Symptoms**: Build fails at "Helm Deploy" stage after 10 minutes

**Diagnosis**:
```
Console Output shows:
Error: timed out waiting for the condition
```

**Solution**:
```bash
# Check pod status
kubectl get pods -n ai

# Check pod events
kubectl describe pod <pod-name> -n ai

# Common causes:
# 1. Image pull errors → Check ECR permissions
# 2. Resource constraints → Check node capacity
# 3. Application errors → Check pod logs

# View pod logs
kubectl logs <pod-name> -n ai

# Fix the issue and rebuild
```

---

## Best Practices

### 1. Job Naming Convention

```
Format: <app-name>-<action>-<environment>

Examples:
- ai-app-deploy-dev
- ai-app-deploy-stage
- ai-app-deploy-prod

Or use parameters (current approach):
- ai-app-deploy (with ENV parameter)
```

### 2. Build Retention

```
Configure in Jenkins → ai-app-deploy → Configure → General

☑ Discard old builds
Strategy: Log Rotation
Days to keep builds: 30
Max # of builds to keep: 50
```

### 3. Build Notifications

```
Configure in Jenkins → ai-app-deploy → Configure → Post-build Actions

Add:
- Email notification
- Slack notification
- GitHub status update
```

### 4. Concurrent Builds

```
Configure in Jenkins → ai-app-deploy → Configure → General

☑ Do not allow concurrent builds
(Prevents conflicts when deploying to same environment)
```

---

## Summary Checklist

### Jenkins UI Configuration
- [ ] Logged into Jenkins UI successfully
- [ ] Created pipeline job "ai-app-deploy"
- [ ] Configured 6 job parameters
- [ ] Set pipeline to read from Git repository
- [ ] Configured Jenkinsfile path
- [ ] Saved job configuration

### Pipeline Execution
- [ ] Triggered first build with parameters
- [ ] All 13 stages completed successfully
- [ ] Build marked as SUCCESS
- [ ] Console output shows deployment complete
- [ ] Application endpoints responding

### Validation
- [ ] Job appears in Jenkins dashboard
- [ ] Build history shows successful build
- [ ] Kubernetes resources created
- [ ] Application accessible via ingress

---

## What You've Accomplished

After completing this runbook:
- ✅ Configured Jenkins pipeline job
- ✅ Connected Jenkins to GitHub repository
- ✅ Set up deployment parameters
- ✅ Executed first successful deployment
- ✅ Verified application is running

---

## Next Steps

Proceed to **Runbook 03: Day-to-Day Operations** to learn:
- How to make code changes
- How to trigger deployments
- How to monitor applications
- How to handle common scenarios

---

**Runbook Version**: 1.0.0  
**Last Updated**: 2026-01-09  
**Next Review**: 2026-04-09