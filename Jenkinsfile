pipeline {
    agent any

    environment {
      
        DOCKER_CRED = credentials('dockerhub')

        DOCKER_REPO = "wafajemai/jenkins-devops"
    }

    stages {

        /* ----------------------- CHECKOUT ----------------------- */
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        /* ----------------------- BUILD IMAGES ----------------------- */
        stage('Build Docker images') {
            steps {
                echo "Build des images Docker..."
                sh """
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        /* ----------------------- TEST INFRA K8S ----------------------- */
        stage('Test Infra (kubectl/helm)') {
            steps {
                echo "Test de l'infrastructure Kubernetes & Helm"
                configFileProvider([configFile(fileId: 'kubeconfig', targetLocation: 'kubeconfig')]) {
                    sh """
                        export KUBECONFIG=kubeconfig
                        kubectl get nodes
                        helm version
                    """
                }
            }
        }

        /* ----------------------- PUSH DOCKER IMAGES ----------------------- */
        stage('Push Docker Images') {
            steps {
                echo "Push des images vers DockerHub..."

                sh """
                    echo "${DOCKER_CRED_PSW}" | docker login -u "${DOCKER_CRED_USR}" --password-stdin

                    docker push ${DOCKER_REPO}:movie.${BUILD_NUMBER}
                    docker push ${DOCKER_REPO}:cast.${BUILD_NUMBER}

                    docker logout
                """
            }
        }

        /* ============================================================
            DEPLOY DEV — branch = dev
           ============================================================ */
        stage('Deploy to DEV') {
            when { branch 'dev' }
            steps {
                echo "Déploiement en DEV..."
                configFileProvider([configFile(fileId: 'kubeconfig', targetLocation: 'kubeconfig')]) {
                    sh """
                        export KUBECONFIG=kubeconfig
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
        }

        /* ============================================================
            DEPLOY QA — branch = qa
           ============================================================ */
        stage('Deploy to QA') {
            when { branch 'qa' }
            steps {
                echo "Déploiement en QA..."
                configFileProvider([configFile(fileId: 'kubeconfig', targetLocation: 'kubeconfig')]) {
                    sh """
                        export KUBECONFIG=kubeconfig
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
        }

        /* ============================================================
            DEPLOY STAGING — branch = staging
           ============================================================ */
        stage('Deploy to STAGING') {
            when { branch 'staging' }
            steps {
                echo "Déploiement en STAGING..."
                configFileProvider([configFile(fileId: 'kubeconfig', targetLocation: 'kubeconfig')]) {
                    sh """
                        export KUBECONFIG=kubeconfig
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
        }

        /* ============================================================
            PROD — branch = master + APPROVAL
           ============================================================ */

        stage('Approval for PROD') {
            when { branch 'master' }
            steps {
                script {
                    input message: "Déployer en PRODUCTION ?", ok: "Déployer"
                }
            }
        }

        stage('Deploy to PROD') {
            when { branch 'master' }
            steps {
                echo "Déploiement en PROD..."
                configFileProvider([configFile(fileId: 'kubeconfig', targetLocation: 'kubeconfig')]) {
                    sh """
                        export KUBECONFIG=kubeconfig
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
    }

    post {
        always {
            echo "Fin du pipeline pour ${env.BRANCH_NAME} — build #${env.BUILD_NUMBER}"
        }
        success {
            echo "✅ Pipeline OK"
        }
        failure {
            echo "❌ Pipeline KO"
        }
    }
}
