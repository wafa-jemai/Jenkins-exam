pipeline {
    agent any

    environment {
        DOCKER_REPO = "wafajemai/jenkins-devops"
    }

    stages {

        /* ===================== CHECKOUT ===================== */
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        /* ===================== BUILD IMAGES ===================== */
        stage('Build Docker images') {
            steps {
                echo "Build des images Docker..."
                sh """
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        /* ===================== TEST INFRA ===================== */
        stage('Test infra (kubectl / helm)') {
            steps {
                echo "Vérification de l'infra (Docker, kubectl, helm)..."
                sh """
                    docker --version
                    kubectl version --client
                    helm version
                """
            }
        }

        /* ===================== PUSH IMAGES ===================== */
        stage('Push Docker images') {
            steps {
                echo "Push des images DockerHub..."

                withCredentials([
                    usernamePassword(
                        credentialsId: 'DOCKER_USERNAME',
                        usernameVariable: 'DOCKER_USERNAME_USR',
                        passwordVariable: 'DOCKER_USERNAME_PSW'
                    )
                ]) {
                    sh """
                        echo "${DOCKER_USERNAME_PSW}" | docker login -u "${DOCKER_USERNAME_USR}" --password-stdin

                        docker push ${DOCKER_REPO}:movie.${BUILD_NUMBER}
                        docker push ${DOCKER_REPO}:cast.${BUILD_NUMBER}

                        docker logout
                    """
                }
            }
        }

        /* ===================== DEPLOY DEV ===================== */
        stage('Deploy DEV') {
            when { branch 'dev' }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    echo "Déploiement en DEV..."
                    sh """
                        kubectl get namespace dev || kubectl create namespace dev

                        helm upgrade --install jenkins-exam-dev ./charts \
                          -f charts/values-dev.yaml \
                          --namespace dev \
                          --set movie.image.repository=${DOCKER_REPO} \
                          --set movie.image.tag=movie.${BUILD_NUMBER} \
                          --set cast.image.repository=${DOCKER_REPO} \
                          --set cast.image.tag=cast.${BUILD_NUMBER}
                    """
                }
            }
        }

        /* ===================== DEPLOY QA ===================== */
        stage('Deploy QA') {
            when { branch 'qa' }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    echo "Déploiement en QA..."
                    sh """
                        kubectl get namespace qa || kubectl create namespace qa

                        helm upgrade --install jenkins-exam-qa ./charts \
                          -f charts/values-qa.yaml \
                          --namespace qa \
                          --set movie.image.repository=${DOCKER_REPO} \
                          --set movie.image.tag=movie.${BUILD_NUMBER} \
                          --set cast.image.repository=${DOCKER_REPO} \
                          --set cast.image.tag=cast.${BUILD_NUMBER}
                    """
                }
            }
        }

        /* ===================== DEPLOY STAGING ===================== */
        stage('Deploy STAGING') {
            when { branch 'staging' }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    echo "Déploiement en STAGING..."
                    sh """
                        kubectl get namespace staging || kubectl create namespace staging

                        helm upgrade --install jenkins-exam-staging ./charts \
                          -f charts/values-staging.yaml \
                          --namespace staging \
                          --set movie.image.repository=${DOCKER_REPO} \
                          --set movie.image.tag=movie.${BUILD_NUMBER} \
                          --set cast.image.repository=${DOCKER_REPO} \
                          --set cast.image.tag=cast.${BUILD_NUMBER}
                    """
                }
            }
        }

        /* ===================== APPROVAL PROD ===================== */
        stage('Approval PROD') {
            when { branch 'master' }
            steps {
                script {
                    input message: "Confirmer le déploiement en PRODUCTION ?", ok: "Déployer"
                }
            }
        }

        /* ===================== DEPLOY PROD ===================== */
        stage('Deploy PROD') {
            when { branch 'master' }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    echo "Déploiement en PROD..."
                    sh """
                        kubectl get namespace prod || kubectl create namespace prod

                        helm upgrade --install jenkins-exam-prod ./charts \
                          -f charts/values-prod.yaml \
                          --namespace prod \
                          --set movie.image.repository=${DOCKER_REPO} \
                          --set movie.image.tag=movie.${BUILD_NUMBER} \
                          --set cast.image.repository=${DOCKER_REPO} \
                          --set cast.image.tag=cast.${BUILD_NUMBER}
                    """
                }
            }
        }
    }

    /* ===================== POST ===================== */
    post {
        always {
            echo "Fin du pipeline (${env.BRANCH_NAME}) – Build #${env.BUILD_NUMBER}"
        }
        success {
            echo "✅ Pipeline OK"
        }
        failure {
            echo "❌ Pipeline KO"
        }
    }
}
