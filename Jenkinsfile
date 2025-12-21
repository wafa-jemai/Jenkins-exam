pipeline {
    agent any

    environment {
        DOCKER_REPO   = "wafajemai/jenkins-devops"
        RELEASE_NAME  = "jenkins-exam"
        KUBECONFIG    = "/var/lib/jenkins/.kube/config"
    }

    stages {

        stage("Checkout") {
            steps { checkout scm }
        }

        stage("Build Docker Images") {
            steps {
                sh """
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

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
                    """
                }
            }
        }

        stage("Deploy DEV") {
            when { branch "dev" }
            steps {
                sh """
                    helm upgrade --install jenkins-exam ./charts \
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

        stage("Deploy QA") {
            when { branch "qa" }
            steps {
                sh """
                    helm upgrade --install jenkins-exam ./charts \
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

        stage("Deploy STAGING") {
            when { branch "staging" }
            steps {
                sh """
                    helm upgrade --install jenkins-exam ./charts \
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

        stage("Approval PROD") {
            when { branch "master" }
            steps {
                input message: "Déployer en PROD ?", ok: "OUI"
            }
        }

        stage("Deploy PROD") {
            when { branch "master" }
            steps {
                sh """
                    helm upgrade --install jenkins-exam ./charts \
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
        success { echo "✔️ Pipeline SUCCESS ${BRANCH_NAME}" }
        failure { echo "❌ Pipeline FAIL ${BRANCH_NAME}" }
    }
}
