pipeline {

    agent any

    environment {
        DOCKERHUB_REPO = "wafajemai/jenkins-devops"
    }

    stages {

        stage('Build Movie') {
            when { anyOf { branch 'dev'; branch 'qa'; branch 'staging'; branch 'master' } }
            steps {
                sh """
                echo '------ BUILD MOVIE SERVICE ------'
                docker build -t ${DOCKERHUB_REPO}:movie.${BUILD_NUMBER} movie/
                """
            }
        }

        stage('Build Cast') {
            when { anyOf { branch 'dev'; branch 'qa'; branch 'staging'; branch 'master' } }
            steps {
                sh """
                echo '------ BUILD CAST SERVICE ------'
                docker build -t ${DOCKERHUB_REPO}:cast.${BUILD_NUMBER} cast/
                """
            }
        }

        stage('Test infra') {
            steps {
                sh """
                echo '------ TEST DOCKER / KUBECTL / HELM ------'
                docker --version
                kubectl version --client
                helm version
                """
            }
        }

        stage('Push Docker images') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'DOCKER_USERNAME', usernameVariable: 'USER', passwordVariable: 'PASS')
                ]) {
                    sh """
                    echo '------ LOGIN DOCKERHUB ------'
                    echo "$PASS" | docker login -u "$USER" --password-stdin

                    echo '------ PUSH MOVIE ------'
                    docker push ${DOCKERHUB_REPO}:movie.${BUILD_NUMBER}

                    echo '------ PUSH CAST ------'
                    docker push ${DOCKERHUB_REPO}:cast.${BUILD_NUMBER}
                    """
                }
            }
        }

        /* --------------------------- DEPLOYS ---------------------------- */

        stage('Deploy DEV') {
            when { branch 'dev' }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh """
                    echo '------ DEPLOY DEV ------'
                    export KUBECONFIG=$KUBECONFIG
                    kubectl get nodes

                    helm upgrade --install fastapi charts/ \
                        -f charts/values-dev.yaml \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.tag=cast.${BUILD_NUMBER} \
                        --namespace dev --create-namespace
                    """
                }
            }
        }

        stage('Deploy QA') {
            when { branch 'qa' }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh """
                    echo '------ DEPLOY QA ------'
                    export KUBECONFIG=$KUBECONFIG
                    kubectl get nodes

                    helm upgrade --install fastapi charts/ \
                        -f charts/values-qa.yaml \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.tag=cast.${BUILD_NUMBER} \
                        --namespace qa --create-namespace
                    """
                }
            }
        }

        stage('Deploy STAGING') {
            when { branch 'staging' }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh """
                    echo '------ DEPLOY STAGING ------'
                    export KUBECONFIG=$KUBECONFIG
                    kubectl get nodes

                    helm upgrade --install fastapi charts/ \
                        -f charts/values-staging.yaml \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.tag=cast.${BUILD_NUMBER} \
                        --namespace staging --create-namespace
                    """
                }
            }
        }

        /* --------------------------- PROD ---------------------------- */

        stage('Approval PROD') {
            when { branch 'master' }
            steps {
                script {
                    timeout(time: 1, unit: 'HOURS') {
                        input message: "Déployer en PROD ?", submitter: "admin"
                    }
                }
            }
        }

        stage('Deploy PROD') {
            when { branch 'master' }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh """
                    echo '------ DEPLOY PROD ------'
                    export KUBECONFIG=$KUBECONFIG
                    kubectl get nodes

                    helm upgrade --install fastapi charts/ \
                        -f charts/values-prod.yaml \
                        --set movie.image.tag=movie.${BUILD_NUMBER} \
                        --set cast.image.tag=cast.${BUILD_NUMBER} \
                        --namespace prod --create-namespace
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline OK ✔"
        }
        failure {
            echo "Pipeline KO ❌"
        }
    }
}
