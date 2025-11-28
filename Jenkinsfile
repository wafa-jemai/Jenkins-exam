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
                sh """
                    docker build -t ${DOCKERHUB_REPO}:movie.${BUILD_NUMBER} ./movie-service
                    docker build -t ${DOCKERHUB_REPO}:cast.${BUILD_NUMBER} ./cast-service
                """
            }
        }

        stage("Push Docker Images") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
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

        /* ENV DEPLOY FUNCTION */
        stage("Deploy Environment") {
            when { anyOf { branch "dev"; branch "qa"; branch "staging"; branch "master" } }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {

                    script {
                        def ns = ""
                        def envFile = ""

                        if (env.BRANCH_NAME == "dev") {
                            ns = "dev"
                            envFile = "charts/values-dev.yaml"
                        }
                        if (env.BRANCH_NAME == "qa") {
                            ns = "qa"
                            envFile = "charts/values-qa.yaml"
                        }
                        if (env.BRANCH_NAME == "staging") {
                            ns = "staging"
                            envFile = "charts/values-staging.yaml"
                        }
                        if (env.BRANCH_NAME == "master") {
                            ns = "prod"
                            envFile = "charts/values-prod.yaml"
                        }

                        sh """
                            echo "Using kubeconfig at: $KUBECONFIG"

                            kubectl get ns ${ns} || kubectl create ns ${ns}

                            helm upgrade --install jenkins-exam-${ns} ./charts \
                                -f ${envFile} \
                                --namespace ${ns} \
                                --set movie.image.repository=${DOCKERHUB_REPO} \
                                --set movie.image.tag=movie.${BUILD_NUMBER} \
                                --set cast.image.repository=${DOCKERHUB_REPO} \
                                --set cast.image.tag=cast.${BUILD_NUMBER}
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline OK"
        }
        failure {
            echo "Pipeline KO"
        }
    }
}
