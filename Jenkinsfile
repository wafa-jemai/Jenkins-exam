pipeline {
    agent any

    environment {
        DOCKER_REPO = "wafajemai/jenkins-devops"
        KUBECONFIG = "/var/jenkins_home/kubeconfig"
        PATH = "/usr/local/bin:/usr/bin:/bin"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Images') {
            steps {
                sh """
                  docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                  docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        stage('Test Infra') {
            steps {
                sh """
                  /usr/local/bin/kubectl version --client
                  /usr/local/bin/helm version
                """
            }
        }

        stage('Push Docker Images') {
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
        stage('Deploy DEV') {
            when { branch 'dev' }
            steps {
                sh """
                  /usr/local/bin/kubectl get ns dev || /usr/local/bin/kubectl create ns dev

                  /usr/local/bin/helm upgrade --install jenkins-exam-dev ./charts \
                    -f charts/values-dev.yaml \
                    -n dev \
                    --set movie.image.repository=${DOCKER_REPO} \
                    --set movie.image.tag=movie.${BUILD_NUMBER} \
                    --set cast.image.repository=${DOCKER_REPO} \
                    --set cast.image.tag=cast.${BUILD_NUMBER}
                """
            }
        }

        /* ================= QA ================= */
        stage('Deploy QA') {
            when { branch 'qa' }
            steps {
                sh """
                  /usr/local/bin/kubectl get ns qa || /usr/local/bin/kubectl create ns qa

                  /usr/local/bin/helm upgrade --install jenkins-exam-qa ./charts \
                    -f charts/values-qa.yaml \
                    -n qa
                """
            }
        }

        /* ================= STAGING ================= */
        stage('Deploy STAGING') {
            when { branch 'staging' }
            steps {
                sh """
                  /usr/local/bin/kubectl get ns staging || /usr/local/bin/kubectl create ns staging

                  /usr/local/bin/helm upgrade --install jenkins-exam-staging ./charts \
                    -f charts/values-staging.yaml \
                    -n staging
                """
            }
        }

        /* ================= PROD ================= */
        stage('Approval PROD') {
            when { branch 'master' }
            steps {
                input message: 'Valider le déploiement PROD ?', ok: 'Déployer'
            }
        }

        stage('Deploy PROD') {
            when { branch 'master' }
            steps {
                sh """
                  /usr/local/bin/kubectl get ns prod || /usr/local/bin/kubectl create ns prod

                  /usr/local/bin/helm upgrade --install jenkins-exam-prod ./charts \
                    -f charts/values-prod.yaml \
                    -n prod
                """
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline OK"
        }
        failure {
            echo "❌ Pipeline KO"
        }
    }
}
