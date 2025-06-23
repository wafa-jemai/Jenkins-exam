/**
 * Jenkins Declarative Pipeline for building, pushing, and deploying microservices.
 * This pipeline handles Docker image creation and deployment to Kubernetes for
 * multiple independent services (e.g., movie-service, cast-service).
 *
 * Key Features:
 * - Centralized environment variable management.
 * - Reusable function for Docker build and push with error handling.
 * - Credential management using Jenkins' built-in `withCredentials` for PATs.
 * - Explicit Docker Hub authentication validation using PAT.
 * - Placeholder for Kubernetes deployment and smoke tests.
 * - Post-build actions for cleanup and notifications.
 */

// =================================================================================================
// GLOBAL UTILITY FUNCTIONS
// These functions are defined at the top-level of the pipeline for reusability across stages.
// =================================================================================================

/**
 * Builds a Docker image for a given service and pushes it to the configured Docker registry.
 * Includes robust error handling for build and push operations.
 *
 * @param serviceName The name of the microservice (e.g., 'movie-service', 'cast-service').
 * This maps to the subdirectory containing the Dockerfile.
 * @param buildTag The unique tag for the image (e.g., Git commit hash, build number).
 * @throws Exception if Docker build or push fails.
 */
def buildAndPushServiceImage(serviceName, buildTag) {
    // Construct the full image name: <DockerHubID>/<DockerRepo>-<Service>-<Tag>
    // Example: "tdksoft/jenkins-devops-exams-movie-service:123-abcde"
    def imageFullName = "${env.DOCKER_HUB_ID}/${env.DOCKER_REPO}-${serviceName}:${buildTag}"
    
    // Path to the service's Dockerfile relative to the workspace root
    def dockerfilePath = "${serviceName}/Dockerfile"

    try {
        echo "🚀 Attempting to build Docker image for '${serviceName}' with tag '${buildTag}'..."
        
        // Execute the Docker build command.
        // Docker build uses the previously logged-in session.
        docker.build(imageFullName, "-f ${dockerfilePath} .")
        echo "✅ Docker image for '${serviceName}' built successfully: ${imageFullName}"

        echo "📦 Initiating push of Docker image '${imageFullName}' to registry..."
        
        // Push the uniquely tagged image. This also uses the pre-established login.
        docker.image(imageFullName).push()
        echo "✅ Image ${imageFullName} pushed."

        // Also push with a 'latest' tag for the specific service for easy access
        // This creates a tag like "tdksoft/jenkins-devops-exams-movie-service:latest"
        docker.image(imageFullName).push("${env.DOCKER_REPO}-${serviceName}:latest")
        echo "✅ Image ${serviceName}:latest also pushed."
        
        echo "🎉 Successfully pushed all tags for '${serviceName}'."

    } catch (Exception e) {
        // Catch any error during build or push
        error("💥 Failed to build or push Docker image for service '${serviceName}': ${e.message}")
    }
}


// =================================================================================================
// DECLARATIVE PIPELINE DEFINITION
// =================================================================================================

pipeline {
    // Agent definition: 'any' means the pipeline can run on any available agent.
    agent any

    // Environment variables for the pipeline.
    // Sensitive credentials are retrieved using the `credentials()` helper *within `withCredentials` blocks*.
    environment {
        // Docker Registry Configuration
        DOCKER_HUB_ID = "tdksoft"                                // Your Docker Hub username or organization
        DOCKER_REPO = "jenkins-devops-exams"                     // Base repository name on Docker Hub
        DOCKER_HUB_PAT_CREDENTIAL_ID = 'docker-hub-pat'          // Jenkins Credential ID for Docker Hub PAT (Secret Text)

        // Kubernetes Configuration (placeholder for now)
        KUBECONFIG_CREDENTIAL_ID = 'config'                      // Jenkins Credential ID for Kubernetes Kubeconfig (Secret File)

        // Dynamic Build Information
        GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        
        // Define common tag suffix based on build number and commit hash
        BUILD_TAG = "${env.BUILD_NUMBER}-${GIT_COMMIT_SHORT}"

        // Service Names (should match subdirectory names)
        MOVIE_SERVICE_NAME = "movie-service"
        CAST_SERVICE_NAME = "cast-service"
    }

    // Pipeline options for robustness and cleanup.
    options {
        // Set a timeout for the entire pipeline to prevent hanging builds.
        timeout(time: 30, unit: 'MINUTES')
        // Optional: retry(2) // Automatic retry in case of temporary failure
        // Optional: disableConcurrentBuilds() // Prevents concurrent builds from interfering
        // Optional: buildDiscarder(logRotator(numToKeepStr: '30')) // Keep last 30 build logs
    }

    // =============================================================================================
    // PIPELINE STAGES
    // =============================================================================================

    stages {
        // ---------------------
        // 1. Source Code Checkout
        // ---------------------
        stage('Checkout Source Code') {
            steps {
                // Checkout the SCM repository (e.g., Git) defined in the job configuration.
                script {
                    echo "🔍 Checking out source code..."
                    checkout scm
                    echo "✅ Source code checked out."
                }
            }
        }

        // ---------------------
        // 2. Pre-checks: Validate Docker Hub Access
        // This stage now explicitly logs in using the PAT (Secret Text credential).
        // ---------------------
        stage("Validate Docker Hub Access") {
            steps {
                script {
                    // Use withCredentials to expose the Secret Text PAT as an environment variable
                    withCredentials([string(credentialsId: env.DOCKER_HUB_PAT_CREDENTIAL_ID, variable: 'DOCKER_PAT')]) {
                        try {
                            echo "🔑 Attempting to log in to Docker Hub using Personal Access Token..."
                            // Use the DOCKER_PAT variable for non-interactive login
                            sh """
                                echo "${DOCKER_PAT}" | docker login -u ${env.DOCKER_HUB_ID} --password-stdin
                            """
                            // Attempt a pull of a known image (or one from your repo, suppressing errors)
                            // This verifies read access. Write access is implicitly tested during push.
                            sh """
                                docker pull ${env.DOCKER_HUB_ID}/${env.DOCKER_REPO}:latest || true
                            """
                            echo "✅ Successfully logged in and verified Docker Hub access using PAT."
                        } catch (Exception err) {
                            error("❌ Failed to authenticate or verify Docker Hub access: ${err.message}. Please check DOCKER_HUB_ID and DOCKER_HUB_PAT_CREDENTIAL_ID.")
                        }
                    }
                }
            }
        }

        // ---------------------
        // 3. Build & Push All Microservices
        // ---------------------
        stage("Build and Push Docker Images") {
            steps {
                script {
                    echo "🏗️ Starting Docker image build and push for all microservices."
                    
                    // Call the reusable function for each microservice
                    // This function will now rely on the 'docker login' performed in the previous stage.
                    buildAndPushServiceImage(env.MOVIE_SERVICE_NAME, env.BUILD_TAG)
                    buildAndPushServiceImage(env.CAST_SERVICE_NAME, env.BUILD_TAG)
                    
                    echo "🎉 All microservice images processed successfully."
                }
            }
        }

        // ---------------------
        // 4. Kubernetes Deployment
        // ---------------------
        stage("Deploy to Kubernetes") {
            // This stage will only execute if the current branch is 'main'.
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🚀 Deploying microservices to Kubernetes from 'main' branch..."
                    
                    // The following section is commented out as it requires a Kubeconfig file
                    // and a working Kubernetes cluster setup.
                    
                    /*
                    withCredentials([file(credentialsId: env.KUBECONFIG_CREDENTIAL_ID, variable: 'KUBECONFIG_PATH')]) {
                        // Set KUBECONFIG environment variable for kubectl
                        sh "export KUBECONFIG=${KUBECONFIG_PATH}"

                        // --- Deploy Movie Service ---
                        echo "Deploying ${env.MOVIE_SERVICE_NAME}..."
                        // Replace placeholders in k8s manifests with actual image tags
                        sh """
                            export MOVIE_IMAGE_TAG="${env.DOCKER_HUB_ID}/${env.DOCKER_REPO}-${env.MOVIE_SERVICE_NAME}:${env.BUILD_TAG}"
                            envsubst < k8s/${env.MOVIE_SERVICE_NAME}/deployment.yaml | kubectl apply -f -
                            echo "Waiting for ${env.MOVIE_SERVICE_NAME} deployment rollout..."
                            kubectl rollout status deployment/${env.MOVIE_SERVICE_NAME} --timeout=300s
                        """
                        echo "✅ ${env.MOVIE_SERVICE_NAME} deployment complete."

                        // --- Deploy Cast Service ---
                        echo "Deploying ${env.CAST_SERVICE_NAME}..."
                        sh """
                            export CAST_IMAGE_TAG="${env.DOCKER_HUB_ID}/${env.DOCKER_REPO}-${env.CAST_SERVICE_NAME}:${env.BUILD_TAG}"
                            envsubst < k8s/${env.CAST_SERVICE_NAME}/deployment.yaml | kubectl apply -f -
                            echo "Waiting for ${env.CAST_SERVICE_NAME} deployment rollout..."
                            kubectl rollout status deployment/${env.CAST_SERVICE_NAME} --timeout=300s
                        """
                        echo "✅ ${env.CAST_SERVICE_NAME} deployment complete."
                    }
                    */
                    echo "🚧 Kubernetes deployment commands are commented out. Placeholder."
                }
            }
        }

        // ---------------------
        // 5. Post-Deployment Smoke Tests
        // ---------------------
        stage("Smoke Tests") {
            // Only run smoke tests if deployment was successful (and it's on main if using `when` condition)
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    echo "🧪 Executing post-deployment smoke tests..."
                    /*
                    // Example: Test Movie Service endpoint
                    def movieServiceTestStatus = sh(
                        script: "curl -sSf http://${MOVIE_SERVICE_K8S_SVC_URL}/health",
                        returnStatus: true
                    )
                    if (movieServiceTestStatus != 0) {
                        error("❌ Movie Service smoke tests failed. Deployment may be unstable.")
                    }
                    echo "✅ Movie Service smoke tests passed."

                    // Example: Test Cast Service endpoint
                    def castServiceTestStatus = sh(
                        script: "curl -sSf http://${CAST_SERVICE_K8S_SVC_URL}/health",
                        returnStatus: true
                    )
                    if (castServiceTestStatus != 0) {
                        error("❌ Cast Service smoke tests failed. Deployment may be unstable.")
                    }
                    echo "✅ Cast Service smoke tests passed."
                    */
                    echo "🚧 Smoke test commands are commented out. Placeholder."
                }
            }
        }
    }

    // =============================================================================================
    // POST-BUILD ACTIONS
    // Executed regardless of stage success or failure.
    // =============================================================================================
    post {
        // Always run cleanup tasks.
        always {
            echo "🧹 Performing cleanup operations..."
            sh "docker logout || true" // Log out from Docker Hub, suppress errors if not logged in
            cleanWs() // Clean the Jenkins workspace
            echo "✅ Cleanup complete."
        }
        // Actions for a successful pipeline run.
        success {
            echo "✨ Pipeline completed successfully!"
            /*
            slackSend(
                color: '#00FF00', // Green
                message: "SUCCESS: Pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.GIT_COMMIT_SHORT}) completed. <${env.BUILD_URL}|View Build>"
            )
            */
            echo "🔔 SUCCESS: Notification placeholder."
        }
        // Actions for a failed pipeline run.
        failure {
            echo "💥 Pipeline failed!"
            /*
            slackSend(
                color: '#FF0000', // Red
                message: "FAILED: Pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|View Logs>). Check logs for details."
            )
            */
            echo "🔔 FAILED: Notification placeholder."
            // Optional: Implement automatic rollback on failure for production deployments.
            /*
            script {
                echo "Attempting to roll back Kubernetes deployment..."
                // Example rollback for a single deployment, adjust for multiple services
                sh "kubectl rollout undo deployment/${env.MOVIE_SERVICE_NAME} || true"
                sh "kubectl rollout undo deployment/${env.CAST_SERVICE_NAME} || true"
                echo "Rollback initiated (if applicable)."
            }
            */
        }
    }
}
