pipeline {
    agent any

    environment {
        DOCKER_USERNAME = credentials('DOCKER_USERNAME')
        DOCKER_REPO = "wafajemai/jenkins-devops"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker images') {
            steps {
                echo "Build des images Docker movie-service et cast-service..."
                sh """
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        stage('Test infra (kubectl / helm)') {
            steps {
                echo "Vérification de l'infra Kubernetes et Helm..."
                sh """
                    kubectl get nodes
                    helm version
                """
            }
        }

        stage('Push Docker images') {
            steps {
                echo "Push des images vers DockerHub..."
                sh """
                    echo "${DOCKER_USERNAME_PSW}" | docker login -u "${DOCKER_USERNAME_USR}" --password-stdin

                    docker push ${DOCKER_REPO}:movie.${BUILD_NUMBER}
                    docker push ${DOCKER_REPO}:cast.${BUILD_NUMBER}

                    docker logout
                """
            }
        }

        // ===================== DEV =====================
        stage('Deploy to DEV') {
            when {
                branch 'dev'
            }
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

        // ===================== QA ======================
        stage('Deploy to QA') {
            when {
                branch 'qa'
            }
            steps {
                echo "Déploiement en QA..."
                sh """
                    kubectl get namespace qa || kubectl create namespace qa

                    helm upgrade --install jenkins-exam-qa ./charts \
                      -f charts/values-qa.yaml \
                      --namespace qa \
                      --set movie.image.repository=${DOCKER_REPO} \
                      --set movie.image.tag="movie.${BUILD_NUMBER}" \
                      --set cast.image.repository=${DOCKER_REPO} \
                      --set cast.image.tag="cast.${BUILD_NUMBER}"
                """
            }
        }

        // ===================== STAGING =================
        stage('Deploy to STAGING') {
            when {
                branch 'staging'
            }
            steps {
                echo "Déploiement en STAGING..."
                sh """
                    kubectl get namespace staging || kubectl create namespace staging

                    helm upgrade --install jenkins-exam-staging ./charts \
                      -f charts/values-staging.yaml \
                      --namespace staging \
                      --set movie.image.repository=${DOCKER_REPO} \
                      --set movie.image.tag="movie.${BUILD_NUMBER}" \
                      --set cast.image.repository=${DOCKER_REPO} \
                      --set cast.image.tag="cast.${BUILD_NUMBER}"
                """
            }
        }

        // ===================== PROD ====================
        stage('Approval for PROD') {
            when {
                branch 'master'
            }
            steps {
                script {
                    input(
                        message: 'Déployer en PRODUCTION (namespace prod) ?',
                        ok: 'Oui, déployer'
                    )
                }
            }
        }

        stage('Deploy to PROD') {
            when {
                branch 'master'
            }
            steps {
                echo "Déploiement en PROD..."
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
            echo "Fin du pipeline pour la branche ${env.BRANCH_NAME}, build #${env.BUILD_NUMBER}"
        }
        success {
            echo "Pipeline OK ✅"
        }
        failure {
            echo "Pipeline KO ❌"
        }
    }
}
