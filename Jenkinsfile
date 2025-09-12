
pipeline {
    agent any

    stages {


        stage('Checkout') {
            steps {
                checkout scm
                
            }
        }
        
        stage('Build Docker images') {
            steps {
                echo 'Building..'
            }
        } 
        stage('Push Docker images') {
            steps {
                echo 'Pushing..'
            }
        }
        stage('Test') {
            steps {
                sh 'kubectl get nodes'
                echo 'Testing..'
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
