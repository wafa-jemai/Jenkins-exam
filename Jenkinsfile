pipeline {
    agent any


    environment {
        DOCKER_USERNAME = credentials('DOCKER_USERNAME')   // ID du credential DockerHub dans Jenkins
        DOCKER_REPO     = "wafajemai/jenkins-devops"
    }

    stages {

        /***********************
         * 1. Récupération du code
         ***********************/
        stage('Checkout') {
            steps {
                echo "Checkout du dépôt Git..."
                checkout scm
            }
        }

        /***********************
         * 2. Build des images Docker
         ***********************/
        stage('Build Docker images') {
            steps {
                echo "Build des images Docker pour movie-service et cast-service..."
                sh """
                    docker build -t ${DOCKER_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKER_REPO}:cast.${BUILD_NUMBER}  ./cast-service
                """
            }
        }

        /***********************
         * 3. Vérification de l'infra (Docker / kubectl / Helm)
         ***********************/
        stage('Test infra') {
            steps {
                echo "Test de l'infrastructure (docker, kubectl, helm)..."
                sh """
                    docker --version
                    kubectl version --client
                    helm version
                """
            }
        }

        /***********************
         * 4. Push des images sur DockerHub
         ***********************/
        stage('Push Docker images') {
            steps {
                echo "Connexion à DockerHub et push des images..."
                sh """
                    echo "${DOCKER_USERNAME_PSW}" | docker login -u "${DOCKER_USERNAME_USR}" --password-stdin

                    docker push ${DOCKER_REPO}:movie.${BUILD_NUMBER}
                    docker push ${DOCKER_REPO}:cast.${BUILD_NUMBER}

                    docker logout
                """
            }
        }

        /***********************
         * 5. Déploiement DEV (branche dev)
         ***********************/
        stage('Deploy DEV') {
            when {
                branch 'dev'
            }
            steps {
                echo "Déploiement en DEV (namespace dev)..."
                sh """
                    kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -

                    helm upgrade --install jenkins-exam-dev ./charts \
                      -n dev \
                      -f charts/values-dev.yaml \
                      --set movie.image.repository=${DOCKER_REPO} \
                      --set movie.image.tag="movie.${BUILD_NUMBER}" \
                      --set cast.image.repository=${DOCKER_REPO} \
                      --set cast.image.tag="cast.${BUILD_NUMBER}"
                """
            }
        }

        /***********************
         * 6. Déploiement QA (branche qa)
         ***********************/
        stage('Deploy QA') {
            when {
                branch 'qa'
            }
            steps {
                echo "Déploiement en QA (namespace qa)..."
                sh """
                    kubectl create namespace qa --dry-run=client -o yaml | kubectl apply -f -

                    helm upgrade --install jenkins-exam-qa ./charts \
                      -n qa \
                      -f charts/values-qa.yaml \
                      --set movie.image.repository=${DOCKER_REPO} \
                      --set movie.image.tag="movie.${BUILD_NUMBER}" \
                      --set cast.image.repository=${DOCKER_REPO} \
                      --set cast.image.tag="cast.${BUILD_NUMBER}"
                """
            }
        }

        /***********************
         * 7. Déploiement STAGING (branche staging)
         ***********************/
        stage('Deploy STAGING') {
            when {
                branch 'staging'
            }
            steps {
                echo "Déploiement en STAGING (namespace staging)..."
                sh """
                    kubectl create namespace staging --dry-run=client -o yaml | kubectl apply -f -

                    helm upgrade --install jenkins-exam-staging ./charts \
                      -n staging \
                      -f charts/values-staging.yaml \
                      --set movie.image.repository=${DOCKER_REPO} \
                      --set movie.image.tag="movie.${BUILD_NUMBER}" \
                      --set cast.image.repository=${DOCKER_REPO} \
                      --set cast.image.tag="cast.${BUILD_NUMBER}"
                """
            }
        }

        /***********************
         * 8. Approbation pour PROD (branche master)
         ***********************/
        stage('Approval PROD') {
            when {
                branch 'master'
            }
            steps {
                script {
                    input(
                        message: "Déployer en PRODUCTION (namespace prod) ?",
                        ok: "Oui, déployer"
                    )
                }
            }
        }

        /***********************
         * 9. Déploiement PROD (branche master + validation manuelle)
         ***********************/
        stage('Deploy PROD') {
            when {
                branch 'master'
            }
            steps {
                echo "Déploiement en PROD (namespace prod)..."
                sh """
                    kubectl create namespace prod --dry-run=client -o yaml | kubectl apply -f -

                    helm upgrade --install jenkins-exam-prod ./charts \
                      -n prod \
                      -f charts/values-prod.yaml \
                      --set movie.image.repository=${DOCKER_REPO} \
                      --set movie.image.tag="movie.${BUILD_NUMBER}" \
                      --set cast.image.repository=${DOCKER_REPO} \
                      --set cast.image.tag="cast.${BUILD_NUMBER}"
                """
            }
        }
    }

    /***********************
     * Post actions globales
     ***********************/
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
