pipeline {
    agent any

    environment {
        DOCKER_REPO = "wafajemai/jenkins-devops"
        KUBECONFIG = "/var/jenkins_home/kubeconfig"
    }

    stages {

        /* ================= CHECKOUT ================= */
        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        /* ================= BUILD ================= */
        stage("Build Docker Images") {
            steps {
                echo "Build des images Docker"
                sh """
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        /* ================= TEST INFRA ================= */
        stage("Test Infra") {
            steps {
                echo "Vérification Docker / Kubectl / Helm"
                sh """
                    docker --version
                    kubectl version --client
                    helm version
                    kubectl get nodes
                """
            }
        }

        /* ================= PUSH ================= */
        stage("Push Docker Images") {
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

        /* ================= DEV ================= */
        stage("Deploy DEV") {
            when { branch "dev" }
            steps {
                sh """
                    kubectl get ns dev || kubectl create ns dev
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

        /* ================= QA ================= */
        stage("Deploy QA") {
            when { branch "qa" }
            steps {
                sh """
                    kubectl get ns qa || kubectl create ns qa
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

        /* ================= STAGING ================= */
        stage("Deploy STAGING") {
            when { branch "staging" }
            steps {
                sh """
                    kubectl get ns staging || kubectl create ns staging
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

        /* ================= PROD – VALIDATION ================= */
        stage("Approval PROD") {
            when { branch "master" }
            steps {
                input message: "Valider le déploiement en PRODUCTION ?", ok: "Déployer PROD"
            }
        }

        stage("Deploy PROD") {
            when { branch "master" }
            steps {
                sh """
                    kubectl get ns prod || kubectl create ns prod
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

    post {
        always {
            echo "🔚 Fin du pipeline — branche ${BRANCH_NAME}, build #${BUILD_NUMBER}"
        }
        success {
            echo "✅ PIPELINE OK"
        }
        failure {
            echo "❌ PIPELINE KO"
        }
    }
}
