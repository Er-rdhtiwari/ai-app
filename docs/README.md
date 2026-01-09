# AI App Documentation

**Complete Guide to Using the AI App Repository**

---

## 📚 Documentation Overview

This documentation provides a complete, step-by-step guide for using the ai-app repository to deploy and manage a production-ready AI application on AWS EKS using Jenkins CI/CD.

### What This Repository Does

The `ai-app` repository is a **GitOps-style application repository** that contains:
- **Application Code**: FastAPI backend and Next.js frontend
- **Deployment Configuration**: Helm charts for Kubernetes
- **CI/CD Pipeline**: Jenkinsfile for automated deployments
- **Documentation**: Complete operational runbooks

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Complete Workflow                         │
└─────────────────────────────────────────────────────────────┘

1. DEVELOPER (You)
   ↓
   Work on Local Machine → Make Code Changes → Commit to Git
   
2. GITHUB
   ↓
   Repository Stores Code → Triggers Jenkins (optional webhook)
   
3. JENKINS SERVER (Permanent)
   ↓
   Reads Jenkinsfile → Builds Docker Images → Deploys to EKS
   
4. AWS EKS
   ↓
   Runs Application → Serves Users via ALB
```

---

## 🎯 Quick Start Guide

### For First-Time Users

Follow these runbooks in order:

1. **[Runbook 01: Initial Setup](RUNBOOK-01-INITIAL-SETUP.md)** (30-45 min)
   - Verify prerequisites
   - Configure AWS resources
   - Set up secrets
   - Update configuration

2. **[Runbook 02: Jenkins Configuration](RUNBOOK-02-JENKINS-CONFIGURATION.md)** (20-30 min)
   - Create Jenkins pipeline job
   - Configure parameters
   - Execute first deployment
   - Verify application

3. **[Runbook 03: Day-to-Day Operations](RUNBOOK-03-DAY-TO-DAY-OPERATIONS.md)** (Reference)
   - Make code changes
   - Deploy updates
   - Monitor applications
   - Handle common scenarios

4. **[Runbook 04: Advanced Operations](RUNBOOK-04-ADVANCED-OPERATIONS.md)** (Reference)
   - Advanced deployment strategies
   - Troubleshooting guide
   - Performance optimization
   - Disaster recovery

### For Experienced Users

**Quick Reference**:
- Make changes → Commit → Push → Jenkins UI → Build with Parameters → Monitor → Verify

---

## 📖 Runbook Descriptions

### Runbook 01: Initial Setup and Prerequisites

**Purpose**: Set up your environment for the first time

**What You'll Do**:
- ✅ Verify AWS infrastructure (EKS, ECR, VPC, etc.)
- ✅ Check Jenkins server and tools
- ✅ Validate platform add-ons (ALB Controller, External Secrets)
- ✅ Configure AWS resources in Helm values
- ✅ Create AWS Secrets Manager secrets
- ✅ Commit configuration changes

**When to Use**: 
- First time setting up the repository
- Setting up a new environment (dev/stage/prod)
- Onboarding new team members

**Duration**: 30-45 minutes

**[→ Go to Runbook 01](RUNBOOK-01-INITIAL-SETUP.md)**

---

### Runbook 02: Jenkins Configuration and Pipeline Setup

**Purpose**: Configure Jenkins to deploy from this repository

**What You'll Do**:
- ✅ Access Jenkins UI
- ✅ Create pipeline job
- ✅ Configure job parameters
- ✅ Set up Git integration
- ✅ Execute first deployment
- ✅ Verify deployment success

**When to Use**:
- After completing Runbook 01
- Setting up Jenkins for the first time
- Recreating Jenkins job after server rebuild

**Duration**: 20-30 minutes

**[→ Go to Runbook 02](RUNBOOK-02-JENKINS-CONFIGURATION.md)**

---

### Runbook 03: Day-to-Day Operations and Code Changes

**Purpose**: Daily development and deployment workflow

**What You'll Do**:
- ✅ Make code changes locally
- ✅ Test changes
- ✅ Commit and push to GitHub
- ✅ Deploy via Jenkins UI
- ✅ Monitor and verify deployments
- ✅ Handle common scenarios

**When to Use**:
- Every day for normal development
- Deploying code changes
- Updating configuration
- Deploying to different environments
- Rolling back deployments

**Duration**: Varies (15 min - 1 hour per deployment)

**[→ Go to Runbook 03](RUNBOOK-03-DAY-TO-DAY-OPERATIONS.md)**

---

### Runbook 04: Advanced Operations and Troubleshooting

**Purpose**: Advanced scenarios and problem resolution

**What You'll Do**:
- ✅ Blue-green deployments
- ✅ Canary deployments
- ✅ Troubleshoot common issues
- ✅ Optimize performance
- ✅ Disaster recovery
- ✅ Production deployment

**When to Use**:
- Troubleshooting deployment issues
- Implementing advanced deployment strategies
- Optimizing application performance
- Preparing for production
- Disaster recovery scenarios

**Duration**: Varies by scenario

**[→ Go to Runbook 04](RUNBOOK-04-ADVANCED-OPERATIONS.md)**

---

## 🔑 Key Concepts

### Where You Work

| Task | Location | Access Method |
|------|----------|---------------|
| **Code Changes** | Your Local Machine | IDE (VS Code, etc.) |
| **Git Operations** | Your Local Machine | Terminal/Git CLI |
| **Trigger Builds** | Jenkins UI | Web Browser |
| **Monitor Builds** | Jenkins UI | Web Browser |
| **Verify Deployments** | Your Local Machine | Terminal/kubectl |
| **View Application** | Any Device | Web Browser |

### Important: You DON'T Need to...

❌ Log into Jenkins server for normal operations  
❌ Manually run Docker commands  
❌ Manually run kubectl commands for deployment  
❌ Manually run Helm commands for deployment  

### What Jenkins Does Automatically

✅ Clones repository from GitHub  
✅ Runs tests  
✅ Builds Docker images  
✅ Pushes images to ECR  
✅ Deploys to Kubernetes via Helm  
✅ Verifies deployment  

---

## 🎓 Learning Path

### Beginner Path

```
Week 1: Setup
├─ Day 1-2: Complete Runbook 01 (Initial Setup)
├─ Day 3-4: Complete Runbook 02 (Jenkins Configuration)
└─ Day 5: First successful deployment

Week 2: Practice
├─ Day 1-2: Make simple code changes (Runbook 03)
├─ Day 3-4: Deploy to different environments
└─ Day 5: Practice rollback procedures

Week 3: Advanced
├─ Day 1-2: Study Runbook 04 (Advanced Operations)
├─ Day 3-4: Practice troubleshooting scenarios
└─ Day 5: Implement performance optimizations
```

### Intermediate Path

```
Day 1: Review Runbook 01 & 02 (if needed)
Day 2: Master Runbook 03 workflows
Day 3: Practice advanced scenarios from Runbook 04
Day 4: Implement custom improvements
Day 5: Document team-specific procedures
```

---

## 📋 Common Workflows

### Workflow 1: Deploy Code Change

```
1. Pull latest code: git pull origin main
2. Create branch: git checkout -b feature/my-change
3. Make changes in your IDE
4. Test locally (optional)
5. Commit: git commit -m "Description"
6. Push: git push origin feature/my-change
7. Merge to main (via PR or direct)
8. Jenkins UI → ai-app-deploy → Build with Parameters
9. Monitor build in Console Output
10. Verify deployment with kubectl/curl
```

**Time**: 15-30 minutes  
**Reference**: [Runbook 03 - Scenario 1](RUNBOOK-03-DAY-TO-DAY-OPERATIONS.md#scenario-1-making-a-backend-code-change)

---

### Workflow 2: Deploy to New Environment

```
1. Ensure code is in main branch
2. Create environment secret in AWS Secrets Manager
3. Jenkins UI → ai-app-deploy → Build with Parameters
4. Change ENV parameter (dev/stage/prod)
5. Update INGRESS_HOST for environment
6. Build and monitor
7. Verify deployment
```

**Time**: 20-30 minutes  
**Reference**: [Runbook 03 - Scenario 4](RUNBOOK-03-DAY-TO-DAY-OPERATIONS.md#scenario-4-deploying-to-different-environment)

---

### Workflow 3: Rollback Deployment

```
1. Identify issue (logs, metrics, user reports)
2. Option A: Helm rollback
   - helm history ai-app -n ai
   - helm rollback ai-app -n ai
3. Option B: Jenkins rebuild
   - Find last successful build
   - Click "Rebuild"
4. Verify rollback successful
5. Investigate and fix issue
```

**Time**: 5-10 minutes  
**Reference**: [Runbook 03 - Scenario 5](RUNBOOK-03-DAY-TO-DAY-OPERATIONS.md#scenario-5-rolling-back-a-deployment)

---

## 🔍 Troubleshooting Quick Reference

### Issue: Build Fails in Jenkins

**Check**:
1. Console Output for error message
2. Stage where it failed
3. Recent code changes

**Common Causes**:
- Syntax errors in code
- Missing dependencies
- AWS credentials issues
- Network connectivity

**Reference**: [Runbook 02 - Troubleshooting](RUNBOOK-02-JENKINS-CONFIGURATION.md#troubleshooting-common-issues)

---

### Issue: Pods Not Starting

**Check**:
```bash
kubectl get pods -n ai
kubectl describe pod <pod-name> -n ai
kubectl logs <pod-name> -n ai
```

**Common Causes**:
- Image pull errors
- Resource constraints
- Application errors
- Configuration issues

**Reference**: [Runbook 04 - Issue 1](RUNBOOK-04-ADVANCED-OPERATIONS.md#issue-1-pods-stuck-in-pending-state)

---

### Issue: Application Not Accessible

**Check**:
```bash
kubectl get ingress -n ai
curl https://your-host.com/api/health
```

**Common Causes**:
- Ingress not created
- DNS not updated
- Security group rules
- Target health issues

**Reference**: [Runbook 04 - Issue 3](RUNBOOK-04-ADVANCED-OPERATIONS.md#issue-3-ingress-not-working-503-errors)

---

## 📞 Getting Help

### Documentation Resources

1. **This Documentation**: Start here for all operational procedures
2. **Main README.md**: Repository overview and architecture
3. **VALIDATION_REPORT.md**: Dry-run validation results
4. **RUNBOOK.md**: Original comprehensive runbook

### Support Channels

- **Slack**: #ai-app-support
- **Email**: devops@rdhcloudlab.com
- **On-Call**: PagerDuty rotation

### Before Asking for Help

1. ✅ Check relevant runbook section
2. ✅ Review error messages in Jenkins Console Output
3. ✅ Check pod logs: `kubectl logs -n ai <pod-name>`
4. ✅ Verify recent changes: `git log`
5. ✅ Check if issue is environment-specific

---

## 🎯 Success Criteria

### You're Ready When You Can...

- [ ] Clone repository and make code changes
- [ ] Commit and push changes to GitHub
- [ ] Trigger Jenkins build via UI
- [ ] Monitor build progress
- [ ] Verify deployment with kubectl
- [ ] Test application endpoints
- [ ] Rollback if needed
- [ ] Troubleshoot common issues

### Mastery Level

- [ ] Deploy to multiple environments
- [ ] Implement blue-green deployments
- [ ] Optimize application performance
- [ ] Handle disaster recovery
- [ ] Mentor new team members

---

## 📊 Metrics and Monitoring

### Key Metrics to Monitor

| Metric | Tool | Threshold |
|--------|------|-----------|
| Build Success Rate | Jenkins | > 95% |
| Deployment Time | Jenkins | < 15 min |
| Pod Restart Count | kubectl | < 5/day |
| Response Time | curl/browser | < 500ms |
| Error Rate | Logs | < 1% |

### Monitoring Commands

```bash
# Pod health
kubectl get pods -n ai

# Resource usage
kubectl top pods -n ai

# Recent events
kubectl get events -n ai --sort-by='.lastTimestamp' | tail -20

# Application logs
kubectl logs -n ai -l app=ai-app-backend --tail=50
```

---

## 🔐 Security Best Practices

### DO ✅

- Use AWS Secrets Manager for sensitive data
- Rotate secrets regularly
- Use IAM roles instead of access keys
- Review code before merging
- Test in staging before production
- Keep dependencies updated
- Monitor security advisories

### DON'T ❌

- Commit secrets to Git
- Use root user in containers
- Skip testing
- Deploy directly to production
- Share credentials
- Ignore security warnings
- Disable security features

---

## 📝 Maintenance Schedule

### Daily

- [ ] Monitor application health
- [ ] Review error logs
- [ ] Check build success rate

### Weekly

- [ ] Review and merge pending PRs
- [ ] Update dependencies (if needed)
- [ ] Check resource usage trends
- [ ] Review security advisories

### Monthly

- [ ] Rotate secrets
- [ ] Review and update documentation
- [ ] Conduct disaster recovery drill
- [ ] Review and optimize costs

### Quarterly

- [ ] Major dependency updates
- [ ] Architecture review
- [ ] Performance optimization
- [ ] Security audit

---

## 🚀 Next Steps

### New Users

1. **Start Here**: [Runbook 01 - Initial Setup](RUNBOOK-01-INITIAL-SETUP.md)
2. **Then**: [Runbook 02 - Jenkins Configuration](RUNBOOK-02-JENKINS-CONFIGURATION.md)
3. **Practice**: [Runbook 03 - Day-to-Day Operations](RUNBOOK-03-DAY-TO-DAY-OPERATIONS.md)

### Experienced Users

- **Reference**: [Runbook 03](RUNBOOK-03-DAY-TO-DAY-OPERATIONS.md) for daily workflows
- **Advanced**: [Runbook 04](RUNBOOK-04-ADVANCED-OPERATIONS.md) for complex scenarios

### Team Leads

- Review all runbooks
- Customize for your team
- Add team-specific procedures
- Train team members

---

## 📚 Additional Resources

### Internal Documentation

- [Main README.md](../README.md) - Repository overview
- [VALIDATION_REPORT.md](../VALIDATION_REPORT.md) - Validation results
- [RUNBOOK.md](../RUNBOOK.md) - Original comprehensive runbook

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)

---

## 📄 Document Information

**Version**: 1.0.0  
**Last Updated**: 2026-01-09  
**Maintained By**: DevOps Team  
**Next Review**: 2026-04-09

---

## 🤝 Contributing

Found an issue or have a suggestion?

1. Create an issue in the repository
2. Submit a pull request with improvements
3. Contact the DevOps team

---

**Ready to get started? Begin with [Runbook 01: Initial Setup](RUNBOOK-01-INITIAL-SETUP.md)** →