pipeline {
    agent any

    environment {
        DOCKER_REPO = "wafajemai/jenkins-devops"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Test Infra") {
            steps {
                sh '''
                    whoami
                    kubectl get nodes
                    kubectl get ns
                    helm version
                    docker version
                '''
            }
        }

        stage("Build Docker Images") {
            steps {
                sh '''
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} cast-service
                '''
            }
        }

        stage("Push Docker Images") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_REPO}:movie.${BUILD_NUMBER}
                        docker push ${DOCKER_REPO}:cast.${BUILD_NUMBER}
                        docker logout
                    '''
                }
            }
        }

        stage("Deploy DEV") {
            when {
                branch "dev"
            }
            steps {
                sh '''
                    helm upgrade --install jenkins-exam-dev ./charts \
                      --namespace dev \
                      -f charts/values-dev.yaml \
                      --set movie.image.repository=${DOCKER_REPO} \
                      --set movie.image.tag=movie.${BUILD_NUMBER} \
                      --set cast.image.repository=${DOCKER_REPO} \
                      --set cast.image.tag=cast.${BUILD_NUMBER}
                '''
            }
        }
    }

    post {
        success {
            echo "✅ DEV déployé avec succès"
        }
        failure {
            echo "❌ Échec du pipeline DEV"
        }
    }
}
