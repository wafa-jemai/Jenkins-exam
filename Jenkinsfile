pipeline {
    agent any

    environment {
        DOCKER_REPO = "wafajemai/jenkins-devops"
        KUBECONFIG = "/var/lib/jenkins/.kube/config"
    }

    stages {

        /* ===== CHECKOUT ===== */
        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        /* ===== TEST INFRA ===== */
        stage("Test Infra") {
            steps {
                sh """
                    echo "User: $(whoami)"
                    docker --version
                    kubectl version --client
                    kubectl get nodes
                    helm version
                """
            }
        }

        /* ===== BUILD ===== */
        stage("Build Docker Images") {
            when { 
                anyOf { branch "dev"; branch "qa"; branch "staging"; branch "master" }
            }
            steps {
                sh """
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        /* ===== PUSH ===== */
        stage("Push Docker Images") {
            when { 
                anyOf { branch "dev"; branch "qa"; branch "staging"; branch "master" }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_REPO}:movie.${BUILD_NUMBER}
                        docker push ${DOCKER_REPO}:cast.${BUILD_NUMBER}
                        docker logout
                    """
                }
            }
        }

        /* ===== DEV ===== */
        stage("Deploy DEV") {
            when { branch "dev" }
            steps {
                sh """
                    helm upgrade --install jenkins-exam-dev ./charts \
                        --namespace dev \
                        --create-namespace \
                        -f charts/values-dev.yaml \
                        --set movie.image.repository=${DOCKER_REPO} \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.repository=${DOCKER_REPO} \
                        --set cast.image.tag=cast.${BUILD_NUMBER}
                """
            }
        }

        /* ===== QA ===== */
        stage("Deploy QA") {
            when { branch "qa" }
            steps {
                sh """
                    helm upgrade --install jenkins-exam-qa ./charts \
                        --namespace qa \
                        --create-namespace \
                        -f charts/values-qa.yaml \
                        --set movie.image.repository=${DOCKER_REPO} \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.repository=${DOCKER_REPO} \
                        --set cast.image.tag=cast.${BUILD_NUMBER}
                """
            }
        }

        /* ===== STAGING ===== */
        stage("Deploy STAGING") {
            when { branch "staging" }
            steps {
                sh """
                    helm upgrade --install jenkins-exam-staging ./charts \
                        --namespace staging \
                        --create-namespace \
                        -f charts/values-staging.yaml \
                        --set movie.image.repository=${DOCKER_REPO} \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.repository=${DOCKER_REPO} \
                        --set cast.image.tag=cast.${BUILD_NUMBER}
                """
            }
        }

        /* ===== PROD VALIDATION ===== */
        stage("Approval PROD") {
            when { branch "master" }
            steps {
                input message: "Valider le déploiement PROD ?", ok: "Déployer"
            }
        }

        /* ===== PROD DEPLOY ===== */
        stage("Deploy PROD") {
            when { branch "master" }
            steps {
                sh """
                    helm upgrade --install jenkins-exam-prod ./charts \
                        --namespace prod \
                        --create-namespace \
                        -f charts/values-prod.yaml \
                        --set movie.image.repository=${DOCKER_REPO} \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.repository=${DOCKER_REPO} \
                        --set cast.image.tag=cast.${BUILD_NUMBER}
                """
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline réussi sur ${BRANCH_NAME}"
        }
        failure {
            echo "❌ Pipeline échoué sur ${BRANCH_NAME}"
        }
    }
}
