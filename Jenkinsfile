pipeline {
    agent any

    environment {
        DOCKER_CREDS = credentials('dockerhub')     
        GITHUB_CREDS = credentials('github-token')   
        DOCKER_REPO  = "wafajemai/jenkins-devops"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker images') {
            steps {
                echo "Build des images Docker..."
                sh """
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        stage('Test infra') {
            steps {
                echo "Vérification de kubectl et helm..."
                sh "kubectl version --client"
                sh "helm version"
            }
        }

        stage('Push Docker images') {
            steps {
                echo "Push des images vers DockerHub..."

                sh """
                    echo "${DOCKER_CREDS_PSW}" | docker login -u "${DOCKER_CREDS_USR}" --password-stdin
                    docker push ${DOCKER_REPO}:movie.${BUILD_NUMBER}
                    docker push ${DOCKER_REPO}:cast.${BUILD_NUMBER}
                    docker logout
                """
            }
        }

        stage('Deploy to DEV') {
            when { branch 'dev' }
            steps {
                echo "Déploiement en DEV..."
                sh """
                    kubectl get namespace dev || kubectl create namespace dev

                    helm upgrade --install jenkins-exam-dev ./charts \
                        -f charts/values-dev.yaml \
                        --namespace dev \
                        --set movie.image.repository=${DOCKER_REPO} \
                        --set movie.image.tag="movie.${BUILD_NUMBER}" \
                        --set cast.image.repository=${DOCKER_REPO} \
                        --set cast.image.tag="cast.${BUILD_NUMBER}"
                """
            }
        }

        stage('Approval for PROD') {
            when { branch 'master' }
            steps {
                script {
                    input message: "Déployer en PROD ?", ok: "Oui"
                }
            }
        }

        stage('Deploy to PROD') {
            when { branch 'master' }
            steps {
                echo "Déploiement en prod..."
                sh """
                    kubectl get namespace prod || kubectl create namespace prod

                    helm upgrade --install jenkins-exam-prod ./charts \
                        -f charts/values-prod.yaml \
                        --namespace prod \
                        --set movie.image.repository=${DOCKER_REPO} \
                        --set movie.image.tag="movie.${BUILD_NUMBER}" \
                        --set cast.image.repository=${DOCKER_REPO} \
                        --set cast.image.tag="cast.${BUILD_NUMBER}"
                """
            }
        }
    }

    post {
        always {
            echo "Fin du pipeline pour ${env.BRANCH_NAME}, build #${env.BUILD_NUMBER}"
        }
        success {
            echo "Pipeline OK ✅"
        }
        failure {
            echo "Pipeline KO ❌"
        }
    }
}
