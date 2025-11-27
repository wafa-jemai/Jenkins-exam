pipeline {
    agent any

    environment {
        DOCKER_CREDS = credentials('dockerhub')
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
                echo "Building Docker images..."
                sh """
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        stage('Test infra') {
            steps {
                sh """
                    docker --version
                    kubectl version --client
                    helm version
                """
            }
        }

        stage('Push images') {
            steps {
                sh """
                    echo "${DOCKER_CREDS_PSW}" | docker login -u "${DOCKER_CREDS_USR}" --password-stdin

                    docker push ${DOCKER_REPO}:movie.${BUILD_NUMBER}
                    docker push ${DOCKER_REPO}:cast.${BUILD_NUMBER}

                    docker logout
                """
            }
        }

        /* Deploy DEV */
        stage('Deploy DEV') {
            when { branch 'dev' }
            steps {
                sh """
                    kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -
                    helm upgrade --install exam-dev ./charts \
                      -n dev \
                      -f charts/values-dev.yaml \
                      --set movie.image.tag="movie.${BUILD_NUMBER}" \
                      --set movie.image.repository="${DOCKER_REPO}" \
                      --set cast.image.tag="cast.${BUILD_NUMBER}" \
                      --set cast.image.repository="${DOCKER_REPO}"
                """
            }
        }

        /* Deploy QA */
        stage('Deploy QA') {
            when { branch 'qa' }
            steps {
                sh """
                    kubectl create namespace qa --dry-run=client -o yaml | kubectl apply -f -
                    helm upgrade --install exam-qa ./charts \
                      -n qa \
                      -f charts/values-qa.yaml \
                      --set movie.image.tag="movie.${BUILD_NUMBER}" \
                      --set movie.image.repository="${DOCKER_REPO}" \
                      --set cast.image.tag="cast.${BUILD_NUMBER}" \
                      --set cast.image.repository="${DOCKER_REPO}"
                """
            }
        }

        /* Deploy Staging */
        stage('Deploy STAGING') {
            when { branch 'staging' }
            steps {
                sh """
                    kubectl create namespace staging --dry-run=client -o yaml | kubectl apply -f -
                    helm upgrade --install exam-staging ./charts \
                      -n staging \
                      -f charts/values-staging.yaml \
                      --set movie.image.tag="movie.${BUILD_NUMBER}" \
                      --set movie.image.repository="${DOCKER_REPO}" \
                      --set cast.image.tag="cast.${BUILD_NUMBER}" \
                      --set cast.image.repository="${DOCKER_REPO}"
                """
            }
        }

        /* PROD Approval */
        stage('Approve PROD') {
            when { branch 'master' }
            steps {
                script {
                    input message: "Déployer en PRODUCTION ?", ok: "Déployer"
                }
            }
        }

        /* Deploy PROD */
        stage('Deploy PROD') {
            when { branch 'master' }
            steps {
                sh """
                    kubectl create namespace prod --dry-run=client -o yaml | kubectl apply -f -
                    helm upgrade --install exam-prod ./charts \
                      -n prod \
                      -f charts/values-prod.yaml \
                      --set movie.image.tag="movie.${BUILD_NUMBER}" \
                      --set movie.image.repository="${DOCKER_REPO}" \
                      --set cast.image.tag="cast.${BUILD_NUMBER}" \
                      --set cast.image.repository="${DOCKER_REPO}"
                """
            }
        }
    }

    post {
        success { echo "Pipeline OK ✅" }
        failure { echo "Pipeline KO ❌" }
        always {
            echo "Fin du pipeline pour ${env.BRANCH_NAME} - Build #${env.BUILD_NUMBER}"
        }
    }
}
