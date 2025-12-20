pipeline {
    agent any

    environment {
        DOCKER_REPO = "wafajemai/jenkins-devops"
        KUBECONFIG = "/var/lib/jenkins/.kube/config"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Build Docker Images") {
            steps {
                sh """
                    docker build -t ${DOCKER_REPO}:movie-${BUILD_NUMBER} movie-service
                    docker build -t ${DOCKER_REPO}:cast-${BUILD_NUMBER} cast-service
                """
            }
        }

        stage("Test Infra") {
            steps {
                sh """
                    docker --version
                    kubectl version --client
                    helm version
                    kubectl get nodes
                """
            }
        }

        stage("Push Docker Images") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_REPO}:movie-${BUILD_NUMBER}
                        docker push ${DOCKER_REPO}:cast-${BUILD_NUMBER}
                        docker logout
                    """
                }
            }
        }

        stage("Deploy DEV") {
            when { branch "dev" }
            steps {
                sh """
                    helm upgrade --install jenkins-exam-dev ./charts \
                      -f charts/values-dev.yaml \
                      --namespace dev \
                      --create-namespace \
                      --set movie.image.repository=${DOCKER_REPO} \
                      --set movie.image.tag=movie-${BUILD_NUMBER} \
                      --set cast.image.repository=${DOCKER_REPO} \
                      --set cast.image.tag=cast-${BUILD_NUMBER}
                """
            }
        }

        stage("Approval PROD") {
            when { branch "master" }
            steps {
                input message: "Valider le déploiement en PRODUCTION ?"
            }
        }

        stage("Deploy PROD") {
            when { branch "master" }
            steps {
                sh """
                    helm upgrade --install jenkins-exam-prod ./charts \
                      -f charts/values-prod.yaml \
                      --namespace prod \
                      --create-namespace \
                      --set movie.image.repository=${DOCKER_REPO} \
                      --set movie.image.tag=movie-${BUILD_NUMBER} \
                      --set cast.image.repository=${DOCKER_REPO} \
                      --set cast.image.tag=cast-${BUILD_NUMBER}
                """
            }
        }
    }

    post {
        always {
            echo "Fin du pipeline — ${BRANCH_NAME} — build ${BUILD_NUMBER}"
        }
        success {
            echo "✅ PIPELINE OK"
        }
        failure {
            echo "❌ PIPELINE KO"
        }
    }
}

