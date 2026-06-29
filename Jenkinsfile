pipeline {
    agent any

    environment {
        REGISTRY          = "custom-registry"
        FRONTEND_IMAGE    = "portal-frontend"
        BOOKING_IMAGE     = "service-env-booking"
        BUILD_TAG         = "${BUILD_NUMBER}"
        KUBECONFIG_CRED   = "k8s-cluster-secret"
    }

    stages {
        stage('Snyk Lint & Code Validation') {
            steps {
                echo 'Validating Python components packages...'
                sh 'pip install flake8 && flake8 --ignore=E501 .'
            }
        }

        stage('Build Artifact Packages') {
            parallel {
                stage('Build UI Wrapper Component') {
                    steps {
                        sh "docker build -t ${REGISTRY}/${FRONTEND_IMAGE}:${BUILD_TAG} ./frontend"
                        sh "docker tag ${REGISTRY}/${FRONTEND_IMAGE}:${BUILD_TAG} ${REGISTRY}/${FRONTEND_IMAGE}:latest"
                    }
                }
                stage('Build Booking Microservice') {
                    steps {
                        sh "docker build -t ${REGISTRY}/${BOOKING_IMAGE}:${BUILD_TAG} ./backend-services/env-booking"
                        sh "docker tag ${REGISTRY}/${BOOKING_IMAGE}:${BUILD_TAG} ${REGISTRY}/${BOOKING_IMAGE}:latest"
                    }
                }
            }
        }

        stage('Secure Push Target Registry') {
            steps {
                sh "docker push ${REGISTRY}/${FRONTEND_IMAGE}:${BUILD_TAG}"
                sh "docker push ${REGISTRY}/${BOOKING_IMAGE}:${BUILD_TAG}"
                sh "docker push ${REGISTRY}/${FRONTEND_IMAGE}:latest"
                sh "docker push ${REGISTRY}/${BOOKING_IMAGE}:latest"
            }
        }

        stage('Production Kubernetes Rolling Deployment') {
            steps {
                withCredentials([file(credentialsId: "${KUBECONFIG_CRED}", variable: 'KUBECONFIG')]) {
                    sh "sed -i 's/:latest/:${BUILD_TAG}/g' k8s-deployment.yaml"
                    sh "kubectl apply -f k8s-deployment.yaml --kubeconfig=\$KUBECONFIG"
                }
            }
        }
    }
    
    post {
        always {
            sh "docker image prune -f"
        }
    }
}