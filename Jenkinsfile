pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ENV',
            choices: ['dev', 'stage', 'prod'],
            description: 'Deployment environment'
        )
        string(
            name: 'AWS_REGION',
            defaultValue: 'us-east-1',
            description: 'AWS Region'
        )
        string(
            name: 'AWS_ACCOUNT_ID',
            defaultValue: '123456789012',
            description: 'AWS Account ID'
        )
        string(
            name: 'CLUSTER_NAME',
            defaultValue: 'rdh-eks-cluster',
            description: 'EKS Cluster Name'
        )
        string(
            name: 'NAMESPACE',
            defaultValue: 'ai',
            description: 'Kubernetes Namespace'
        )
        string(
            name: 'INGRESS_HOST',
            defaultValue: 'ai-dev.rdhcloudlab.com',
            description: 'Ingress hostname'
        )
    }
    
    environment {
        GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        BACKEND_IMAGE = "${params.AWS_ACCOUNT_ID}.dkr.ecr.${params.AWS_REGION}.amazonaws.com/ai-app-backend"
        FRONTEND_IMAGE = "${params.AWS_ACCOUNT_ID}.dkr.ecr.${params.AWS_REGION}.amazonaws.com/ai-app-frontend"
        BACKEND_IMAGE_TAG = "${GIT_COMMIT_SHORT}"
        FRONTEND_IMAGE_TAG = "${GIT_COMMIT_SHORT}"
    }
    
    stages {
        stage('Validate Tools') {
            steps {
                script {
                    echo "=== Validating Required Tools ==="
                    sh '''
                        echo "Checking AWS CLI..."
                        aws --version
                        
                        echo "Checking Docker..."
                        docker --version
                        
                        echo "Checking kubectl..."
                        kubectl version --client
                        
                        echo "Checking Helm..."
                        helm version
                        
                        echo "All required tools are available!"
                    '''
                }
            }
        }
        
        stage('AWS Identity Check') {
            steps {
                script {
                    echo "=== Verifying AWS Identity ==="
                    sh '''
                        aws sts get-caller-identity
                        echo "AWS Region: ${AWS_REGION}"
                        echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
                    '''
                }
            }
        }
        
        stage('Backend Tests') {
            steps {
                script {
                    echo "=== Running Backend Tests ==="
                    dir('backend') {
                        sh '''
                            # Create virtual environment
                            python3 -m venv venv
                            . venv/bin/activate
                            
                            # Install dependencies
                            pip install --upgrade pip
                            pip install -r requirements.txt
                            
                            # Run tests
                            pytest tests/ -v --tb=short
                            
                            # Cleanup
                            deactivate
                        '''
                    }
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                script {
                    echo "=== Building Frontend ==="
                    dir('frontend') {
                        sh '''
                            # Install dependencies
                            npm ci
                            
                            # Run linting
                            npm run lint || true
                            
                            echo "Frontend build preparation complete"
                        '''
                    }
                }
            }
        }
        
        stage('ECR Login') {
            steps {
                script {
                    echo "=== Logging into ECR ==="
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | \
                        docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                    '''
                }
            }
        }
        
        stage('Build and Push Backend Image') {
            steps {
                script {
                    echo "=== Building Backend Docker Image ==="
                    dir('backend') {
                        sh """
                            docker build -t ${BACKEND_IMAGE}:${BACKEND_IMAGE_TAG} .
                            docker tag ${BACKEND_IMAGE}:${BACKEND_IMAGE_TAG} ${BACKEND_IMAGE}:latest
                            
                            echo "Pushing backend image to ECR..."
                            docker push ${BACKEND_IMAGE}:${BACKEND_IMAGE_TAG}
                            docker push ${BACKEND_IMAGE}:latest
                            
                            echo "Backend image pushed: ${BACKEND_IMAGE}:${BACKEND_IMAGE_TAG}"
                        """
                    }
                }
            }
        }
        
        stage('Build and Push Frontend Image') {
            steps {
                script {
                    echo "=== Building Frontend Docker Image ==="
                    dir('frontend') {
                        sh """
                            docker build -t ${FRONTEND_IMAGE}:${FRONTEND_IMAGE_TAG} .
                            docker tag ${FRONTEND_IMAGE}:${FRONTEND_IMAGE_TAG} ${FRONTEND_IMAGE}:latest
                            
                            echo "Pushing frontend image to ECR..."
                            docker push ${FRONTEND_IMAGE}:${FRONTEND_IMAGE_TAG}
                            docker push ${FRONTEND_IMAGE}:latest
                            
                            echo "Frontend image pushed: ${FRONTEND_IMAGE}:${FRONTEND_IMAGE_TAG}"
                        """
                    }
                }
            }
        }
        
        stage('Update Kubeconfig') {
            steps {
                script {
                    echo "=== Updating Kubeconfig ==="
                    sh """
                        aws eks update-kubeconfig \
                            --region ${AWS_REGION} \
                            --name ${CLUSTER_NAME}
                        
                        kubectl config current-context
                        kubectl cluster-info
                    """
                }
            }
        }
        
        stage('Create Namespace') {
            steps {
                script {
                    echo "=== Ensuring Namespace Exists ==="
                    sh """
                        kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                        kubectl label namespace ${NAMESPACE} environment=${ENV} --overwrite
                    """
                }
            }
        }
        
        stage('Helm Deploy') {
            steps {
                script {
                    echo "=== Deploying with Helm ==="
                    dir('helm') {
                        sh """
                            helm upgrade --install ai-app ./ai-app \
                                --namespace ${NAMESPACE} \
                                --create-namespace \
                                --set env=${ENV} \
                                --set ingressHost=${INGRESS_HOST} \
                                --set backend.image.repository=${BACKEND_IMAGE} \
                                --set backend.image.tag=${BACKEND_IMAGE_TAG} \
                                --set frontend.image.repository=${FRONTEND_IMAGE} \
                                --set frontend.image.tag=${FRONTEND_IMAGE_TAG} \
                                --set externalSecrets.secretName=ai-app/${ENV}/openai \
                                --wait \
                                --timeout 10m \
                                --atomic
                            
                            echo "Helm deployment completed successfully!"
                        """
                    }
                }
            }
        }
        
        stage('Verify Rollout') {
            steps {
                script {
                    echo "=== Verifying Deployment Rollout ==="
                    sh """
                        echo "Checking backend deployment..."
                        kubectl rollout status deployment/ai-app-backend -n ${NAMESPACE} --timeout=5m
                        
                        echo "Checking frontend deployment..."
                        kubectl rollout status deployment/ai-app-frontend -n ${NAMESPACE} --timeout=5m
                        
                        echo "Getting pod status..."
                        kubectl get pods -n ${NAMESPACE} -l app=ai-app-backend
                        kubectl get pods -n ${NAMESPACE} -l app=ai-app-frontend
                        
                        echo "Rollout verification completed!"
                    """
                }
            }
        }
        
        stage('Helm Status') {
            steps {
                script {
                    echo "=== Helm Release Status ==="
                    sh """
                        helm list -n ${NAMESPACE}
                        helm status ai-app -n ${NAMESPACE}
                        helm get values ai-app -n ${NAMESPACE}
                    """
                }
            }
        }
        
        stage('Verification Commands') {
            steps {
                script {
                    echo "=== Deployment Verification Information ==="
                    sh """
                        echo "=========================================="
                        echo "DEPLOYMENT VERIFICATION COMMANDS"
                        echo "=========================================="
                        echo ""
                        echo "1. Check Pods:"
                        echo "   kubectl get pods -n ${NAMESPACE}"
                        echo ""
                        echo "2. Check Services:"
                        echo "   kubectl get svc -n ${NAMESPACE}"
                        echo ""
                        echo "3. Check Ingress:"
                        echo "   kubectl get ingress -n ${NAMESPACE}"
                        echo ""
                        echo "4. Get Ingress Details:"
                        echo "   kubectl describe ingress ai-app-ingress -n ${NAMESPACE}"
                        echo ""
                        echo "5. Check HPA:"
                        echo "   kubectl get hpa -n ${NAMESPACE}"
                        echo ""
                        echo "6. Check External Secrets:"
                        echo "   kubectl get externalsecret -n ${NAMESPACE}"
                        echo "   kubectl get secret ai-app-secrets -n ${NAMESPACE}"
                        echo ""
                        echo "7. Test Backend Health:"
                        echo "   curl -k https://${INGRESS_HOST}/api/health"
                        echo ""
                        echo "8. Test Frontend:"
                        echo "   curl -k https://${INGRESS_HOST}/"
                        echo ""
                        echo "9. View Backend Logs:"
                        echo "   kubectl logs -n ${NAMESPACE} -l app=ai-app-backend --tail=50"
                        echo ""
                        echo "10. View Frontend Logs:"
                        echo "   kubectl logs -n ${NAMESPACE} -l app=ai-app-frontend --tail=50"
                        echo ""
                        echo "=========================================="
                        echo "ACTUAL RESOURCE STATUS"
                        echo "=========================================="
                        
                        kubectl get all -n ${NAMESPACE}
                        
                        echo ""
                        echo "=========================================="
                        echo "INGRESS DETAILS"
                        echo "=========================================="
                        kubectl describe ingress ai-app-ingress -n ${NAMESPACE} || true
                        
                        echo ""
                        echo "=========================================="
                        echo "TESTING BACKEND HEALTH ENDPOINT"
                        echo "=========================================="
                        
                        # Wait for ALB to be ready
                        sleep 30
                        
                        # Try to get the ALB DNS name
                        ALB_DNS=\$(kubectl get ingress ai-app-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
                        
                        if [ -n "\$ALB_DNS" ]; then
                            echo "ALB DNS: \$ALB_DNS"
                            echo "Testing health endpoint via ALB..."
                            curl -f http://\$ALB_DNS/api/health || echo "Health check via ALB failed (may need DNS propagation)"
                        else
                            echo "ALB not yet provisioned. Check ingress status in a few minutes."
                        fi
                        
                        echo ""
                        echo "=========================================="
                        echo "DEPLOYMENT COMPLETE!"
                        echo "=========================================="
                        echo "Environment: ${ENV}"
                        echo "Namespace: ${NAMESPACE}"
                        echo "Backend Image: ${BACKEND_IMAGE}:${BACKEND_IMAGE_TAG}"
                        echo "Frontend Image: ${FRONTEND_IMAGE}:${FRONTEND_IMAGE_TAG}"
                        echo "Ingress Host: ${INGRESS_HOST}"
                        echo ""
                        echo "Access your application at: https://${INGRESS_HOST}"
                        echo "=========================================="
                    """
                }
            }
        }
    }
    
    post {
        success {
            echo "=== Pipeline Completed Successfully ==="
            echo "Deployment to ${params.ENV} environment completed!"
        }
        failure {
            echo "=== Pipeline Failed ==="
            echo "Check the logs above for error details."
            sh """
                echo "Getting recent pod events..."
                kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp' | tail -20 || true
                
                echo "Getting pod status..."
                kubectl get pods -n ${NAMESPACE} || true
            """
        }
        always {
            echo "=== Cleaning Up ==="
            sh '''
                # Cleanup Docker images to save space
                docker system prune -f || true
            '''
        }
    }
}