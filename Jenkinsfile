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
                sh 'docker build -t wafajemai/jenkins-devops:movie.${BUILD_NUMBER} ./movie-service'
                sh 'docker build -t wafajemai/jenkins-devops:cast.${BUILD_NUMBER}  ./cast-service'
            }
        } 

        stage('Test infra') {
            steps {
                sh 'kubectl get nodes'
                sh ' echo ${DOCKER_USERNAME_PSW} | docker login -u ${DOCKER_USERNAME_USR} --password-stdin'
                sh 'helm list'
                echo 'Testing..'
            }
        }

        
        stage('Push Docker images') {
            steps {
                echo 'Pushing..'
                sh '''
                echo ${DOCKER_USERNAME_PSW} | docker login -u ${DOCKER_USERNAME_USR} --password-stdin
                docker push wafajemai/jenkins-devops:movie.${BUILD_NUMBER} 
                docker push wafajemai/jenkins-devops:cast.${BUILD_NUMBER}
                '''
            }
        }
        
        stage('Deploy to DEV') {
            steps {
                echo 'Deploying....'
                sh '''
                    kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -
                    # Deploy using Helm
                    helm upgrade --install jenkins-exam ./charts -f ./charts/values.yaml --namespace dev
                '''
                 

            }
        }

         stage('Deploy to QA') {
            steps {
                echo 'Deploying....'
                     sh '''
                          kubectl create namespace QA --dry-run=client -o yaml | kubectl apply -f -
                          # Deploy using Helm
                          helm upgrade --install jenkins-exam ./charts -f ./charts/values.yaml --namespace QA
                     '''
            }
        }

         stage('Deploy to Staging') {
            steps {
                echo 'Deploying....'
                     sh '''
                        kubectl create namespace staging --dry-run=client -o yaml | kubectl apply -f -
                        # Deploy using Helm
                        helm upgrade --install jenkins-exam ./charts -f ./charts/values.yaml --namespace staging
                     '''
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
                     sh '''
                        kubectl create namespace prod --dry-run=client -o yaml | kubectl apply -f -
                        # Deploy using Helm
                        helm upgrade --install jenkins-exam ./charts -f ./charts/values.yaml --namespace prod
                    '''
            }
        }
    }
}
