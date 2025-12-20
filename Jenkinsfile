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

        stage("Test Infra") {
            steps {
                sh """
                    docker --version
                    kubectl get nodes
                    helm version
                """
            }
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
                        docker logout
                    """
                }
            }
        }

        stage("Deploy DEV") {
            when { branch "dev" }
            steps {
                sh """
                    helm upgrade --install fastapiapp ./charts \
                        --namespace dev \
                        --create-namespace \
                        -f charts/values-dev.yaml \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.tag=cast.${BUILD_NUMBER}
                """
            }
        }

        stage("Deploy QA") {
            when { branch "qa" }
            steps {
                sh """
                    helm upgrade --install fastapiapp ./charts \
                        --namespace qa \
                        --create-namespace \
                        -f charts/values-qa.yaml \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.tag=cast.${BUILD_NUMBER}
                """
            }
        }

        stage("Deploy STAGING") {
            when { branch "staging" }
            steps {
                sh """
                    helm upgrade --install fastapiapp ./charts \
                        --namespace staging \
                        --create-namespace \
                        -f charts/values-staging.yaml \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.tag=cast.${BUILD_NUMBER}
                """
            }
        }

        stage("Approval PROD") {
            when { branch "master" }
            steps {
                input message: "Déployer en PROD ?", ok: "Oui, déployer"
            }
        }

        stage("Deploy PROD") {
            when { branch "master" }
            steps {
                sh """
                    helm upgrade --install fastapiapp ./charts \
                        --namespace prod \
                        --create-namespace \
                        -f charts/values-prod.yaml \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.tag=cast.${BUILD_NUMBER}
                """
            }
        }
    }

    post {
        success {
            echo "🚀 Pipeline terminé avec succès sur ${BRANCH_NAME}"
        }
        failure {
            echo "❌ Pipeline échoué sur ${BRANCH_NAME}"
        }
    }
}
