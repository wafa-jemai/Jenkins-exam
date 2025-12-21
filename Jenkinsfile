pipeline {
    agent any

    environment {
        DOCKER_REPO = "wafajemai/jenkins-devops"
        KUBECONFIG = "/var/lib/jenkins/.kube/config"
    }

    stages {

        /* ===================== CHECKOUT ===================== */
        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        /* ===================== INFRA TEST ===================== */
        stage("Test Infra") {
            steps {
                sh """
                    whoami
                    docker --version
                    kubectl version --client
                    helm version
                    kubectl get nodes
                """
            }
        }

        /* ===================== DOCKER BUILD ===================== */
        stage("Build Docker Images") {
            steps {
                sh """
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        /* ===================== DOCKER PUSH ===================== */
        stage("Push Docker Images") {
            when { branch "dev" }
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

        /* ===================== DEPLOY DEV ===================== */
        stage("Deploy DEV") {
            when { branch "dev" }
            steps {
                sh """
                    helm upgrade --install fastapiapp ./charts/fastapiapp \
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

        /* ===================== DEPLOY QA ===================== */
        stage("Deploy QA") {
            when { branch "qa" }
            steps {
                sh """
                    helm upgrade --install fastapiapp ./charts/fastapiapp \
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

        /* ===================== DEPLOY STAGING ===================== */
        stage("Deploy STAGING") {
            when { branch "staging" }
            steps {
                sh """
                    helm upgrade --install fastapiapp ./charts/fastapiapp \
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

        /* ===================== PROD APPROVAL ===================== */
        stage("Approval PROD") {
            when { branch "master" }
            steps {
                input message: "Valider le déploiement PROD ?", ok: "Déployer"
            }
        }

        /* ===================== DEPLOY PROD ===================== */
        stage("Deploy PROD") {
            when { branch "master" }
            steps {
                sh """
                    helm upgrade --install fastapiapp ./charts/fastapiapp \
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
            echo "✅ Pipeline success on ${BRANCH_NAME}"
        }
        failure {
            echo "❌ Pipeline failed on ${BRANCH_NAME}"
        }
    }
}
