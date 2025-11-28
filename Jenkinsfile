pipeline {
    agent any

    environment {
        DOCKERHUB = credentials('dockerhub')          // ton user/pass DockerHub
        DOCKER_USERNAME = "${DOCKERHUB_USR}"          // alias
        DOCKER_PASSWORD = "${DOCKERHUB_PSW}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "Branch: ${env.BRANCH_NAME}"
            }
        }

        stage('Build App') {
            steps {
                echo "=== BUILD APPLICATION ==="
                sh '''
                    echo "Compilation / build logic here"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo "=== UNIT TESTS ==="
                sh '''
                    echo "Here you run your tests"
                '''
            }
        }

        stage('Docker Build') {
            when { anyOf { branch 'dev'; branch 'qa'; branch 'staging'; branch 'master' } }
            steps {
                echo "=== DOCKER BUILD ==="

                sh """
                    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                    docker build -t wafa-jemai/jenkins-exam:${env.BRANCH_NAME}-${env.BUILD_NUMBER} .
                    docker push wafa-jemai/jenkins-exam:${env.BRANCH_NAME}-${env.BUILD_NUMBER}
                """
            }
        }

        stage('Deploy to K3s') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'qa'
                    branch 'staging'
                    branch 'master'
                }
            }
            steps {
                echo "=== DEPLOY TO K3S ==="

                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {

                    sh '''
                        echo "[STEP] Checking cluster access"
                        kubectl get nodes

                        echo "[STEP] Updating Helm release"
                        helm upgrade --install jenkins-exam ./helm \
                          --namespace default \
                          -f helm/values-${BRANCH_NAME}.yaml \
                          --set image.tag=${BRANCH_NAME}-${BUILD_NUMBER}

                        echo "[STEP] Deployment DONE"
                    '''
                }
            }
        }

    }

    post {
        success {
            echo "Pipeline for ${env.BRANCH_NAME} SUCCESS ✔️"
        }
        failure {
            echo "Pipeline for ${env.BRANCH_NAME} FAILED ❌"
        }
    }
}
