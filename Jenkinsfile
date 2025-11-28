pipeline {
    agent any

    environment {
        DOCKERHUB_REPO = "wafajemai/jenkins-devops"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Build Docker Images") {
            steps {
                echo "🔧 Build des images Docker..."
                sh """
                    docker build -t ${DOCKERHUB_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKERHUB_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        stage("Test Infra") {
            steps {
                echo "🔎 Test Docker / Kubectl / Helm..."
                sh """
                    docker --version
                    kubectl version --client
                    helm version
                """
            }
        }

        stage("Push Docker Images") {
            steps {
                echo "📤 Push des images DockerHub..."
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',          // <<< IMPORTANT: ton vrai credentialsId
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKERHUB_REPO}:movie.${BUILD_NUMBER}
                        docker push ${DOCKERHUB_REPO}:cast.${BUILD_NUMBER}
                        docker logout
                    """
                }
            }
        }

        /* DEV */
        stage("Deploy DEV") {
            when { branch "dev" }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KCFG')]) {
                    sh """
                        export KUBECONFIG=$KCFG
                        kubectl get ns dev || kubectl create ns dev
                        helm upgrade --install jenkins-exam-dev ./charts \
                          -f charts/values-dev.yaml \
                          --namespace dev \
                          --set movie.image.repository=${DOCKERHUB_REPO} \
                          --set movie.image.tag=movie.${BUILD_NUMBER} \
                          --set cast.image.repository=${DOCKERHUB_REPO} \
                          --set cast.image.tag=cast.${BUILD_NUMBER}
                    """
                }
            }
        }

        /* QA */
        stage("Deploy QA") {
            when { branch "qa" }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KCFG')]) {
                    sh """
                        export KUBECONFIG=$KCFG
                        kubectl get ns qa || kubectl create ns qa
                        helm upgrade --install jenkins-exam-qa ./charts \
                          -f charts/values-qa.yaml \
                          --namespace qa \
                          --set movie.image.repository=${DOCKERHUB_REPO} \
                          --set movie.image.tag=movie.${BUILD_NUMBER} \
                          --set cast.image.repository=${DOCKERHUB_REPO} \
                          --set cast.image.tag=cast.${BUILD_NUMBER}
                    """
                }
            }
        }

        /* STAGING */
        stage("Deploy STAGING") {
            when { branch "staging" }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KCFG')]) {
                    sh """
                        export KUBECONFIG=$KCFG
                        kubectl get ns staging || kubectl create ns staging
                        helm upgrade --install jenkins-exam-staging ./charts \
                          -f charts/values-staging.yaml \
                          --namespace staging \
                          --set movie.image.repository=${DOCKERHUB_REPO} \
                          --set movie.image.tag=movie.${BUILD_NUMBER} \
                          --set cast.image.repository=${DOCKERHUB_REPO} \
                          --set cast.image.tag=cast.${BUILD_NUMBER}
                    """
                }
            }
        }

        /* PROD */
        stage("Approval PROD") {
            when { branch "master" }
            steps {
                input message: "Approuvez-vous le déploiement en production ?", ok: "Déployer"
            }
        }

        stage("Deploy PROD") {
            when { branch "master" }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KCFG')]) {
                    sh """
                        export KUBECONFIG=$KCFG
                        kubectl get ns prod || kubectl create ns prod
                        helm upgrade --install jenkins-exam-prod ./charts \
                          -f charts/values-prod.yaml \
                          --namespace prod \
                          --set movie.image.repository=${DOCKERHUB_REPO} \
                          --set movie.image.tag=movie.${BUILD_NUMBER} \
                          --set cast.image.repository=${DOCKERHUB_REPO} \
                          --set cast.image.tag=cast.${BUILD_NUMBER}
                    """
                }
            }
        }
    }

    post {
        always {
            echo "🔚 Fin du pipeline ${BRANCH_NAME} #${BUILD_NUMBER}"
        }
        success {
            echo "✅ Pipeline OK"
        }
        failure {
            echo "❌ Pipeline KO"
        }
    }
}
