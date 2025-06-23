pipeline {
    agent {
        label 'any'  
        // TODO Use Dedicated agent with Docker/Kubectl pre-installed
    }

    environment {
        // Public
        DOCKER_HUB_ID = "tdksoft"  
        DOCKER_REPO = "jenkins-devops-exams"  // Docker repository name
        
        // Private (stored in Jenkins Credentials)
        DOCKER_HUB_PAT = credentials('docker-hub-pat')  
        KUBECONFIG = credentials('kubeconfig')  // For Kubernetes
        
        // Dynamic
        GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        DOCKER_IMAGE = "${DOCKER_HUB_ID}/${DOCKER_REPO}:${env.BUILD_NUMBER}-${GIT_COMMIT_SHORT}"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        retry(2)  // Automatic retry in case of temporary failure
        disableConcurrentBuilds()  // Prevents version conflicts
        buildDiscarder(logRotator(numToKeepStr: '30'))  // Clean up old builds
    }

    stages {
        // ---------------------
        // 1. Pre-checks
        // ---------------------
        stage("Validate Docker Hub Access") {
            steps {
                script {
                    try {
                        // Connection test + permission check (read/write)
                        def loginStatus = sh(
                            script: """
                                echo ${DOCKER_HUB_PAT} | docker login -u ${DOCKER_HUB_ID} --password-stdin && \\
                                docker pull ${DOCKER_HUB_ID}/${DOCKER_REPO}:latest || true
                            """,
                            returnStatus: true
                        )
                        
                        if (loginStatus != 0) {
                            error("❌ Docker Hub authentication failed. Check PAT and permissions.")
                        }
                        
                        echo "✅ Connected to Docker Hub with required permissions."
                    } catch (err) {
                        currentBuild.result = 'FAILURE'
                        error("Validation Docker Hub failed: ${err.message}")
                    }
                }
            }
        }

        // ---------------------
        // 2. Build & Push
        // ---------------------
        stage("Build and Push Docker Image") {
            steps {
                script {
                    docker.build(DOCKER_IMAGE)
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-creds') {
                        docker.image(DOCKER_IMAGE).push()
                        // Additional tag for 'latest'
                        // docker.image(DOCKER_IMAGE).push('latest')
                    }
                }
            }
        }

        // ---------------------
        // 3. K8s Deployment
        // ---------------------
        stage("Deploy to Kubernetes") {
            when {
                branch 'main'  // Execute only on the main/prod branch
            }
            steps {
                script {
                    /*
                    // Use 'envsubst' to inject dynamic variables
                    sh """
                        export IMAGE_VERSION="${DOCKER_IMAGE}"
                        envsubst < k8s/deployment.yaml | kubectl apply -f -
                    """
                    
                    // Deployment verification
                    sh "kubectl rollout status deployment/my-app --timeout=300s"
                    */
                    sh "echo Here come the Kubernetes deployment commands"
                }
            }
        }

        // ---------------------
        // 4. Post-Deploy Tests
        // ---------------------
        stage("Smoke Tests") {
            steps {
                script {
                    /*
                    def testStatus = sh(
                        script: "curl -sSf http://${K8S_SERVICE_URL}/health",
                        returnStatus: true
                    )
                    
                    if (testStatus != 0) {
                        error("❌ Smoke tests failed. Deployment may be unstable.")
                    }*/
                    sh "echo Here come the smoke tests"
                }
            }
        }
    }

    post {
        always {
            // Cleanup
            sh "docker logout || true"
            cleanWs()
            
            // Archive K8s logs
            // archiveArtifacts artifacts: 'k8s/logs/*.log', allowEmptyArchive: true
        }
        success {
            slackSend(
                color: '#00FF00',
                message: "SUCCESS: Pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.GIT_COMMIT_SHORT})"
            )
        }
        failure {
            slackSend(
                color: '#FF0000',
                message: "FAILED: Pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Logs>)"
            )
            
            // Automatic rollback if deployment fails
           // sh "kubectl rollout undo deployment/my-app || true"
        }
    }
}
