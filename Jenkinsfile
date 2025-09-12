o
pipeline {
    agent any
    
    environment {
        DOCKER_USERNAME = credentials('DOCKER_USERNAME')
    }

    stages {


        stage('Checkout') {
            steps {
                checkout scm
                
            }
        }
        
        stage('Build Docker images') {
            steps {
                echo 'Building..'
                echo '${DOCKER_USERNAME_USR}'
                //sh 'docker build -t wafajemai/jenkins-devops:${BUILD_NUMBER}  ./movie-service'
            }
        } 

        stage('Test infra') {
            steps {
                sh 'kubectl get nodes'
                sh 'docker login -u ${DOCKER_USERNAME} --password-stdin'
                echo 'Testing..'
            }
        }

        
        stage('Push Docker images') {
            steps {
                echo 'Pushing..'
            }
        }
        
        stage('Deploy to DEV') {
            steps {
                echo 'Deploying....'
            }
        }

         stage('Deploy to QA') {
            steps {
                echo 'Deploying....'
            }
        }

         stage('Deploy to Staging') {
            steps {
                echo 'Deploying....'
            }
        }

         stage('Deploy to Prod') {
             when {
                    branch 'master'
                  }

             input {
                    message "Deploy to production?"
                    ok "Yes, deploy to production"
                 }
            steps {
                echo 'Deploying....'
            }
        }
    }
}
