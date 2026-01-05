pipeline {
  agent any

  environment {
    DOCKER_REPO = "wafajemai/jenkins-devops"
    IMAGE_TAG   = "${BUILD_NUMBER}"
  }

  stages {

    stage("Checkout") {
      steps {
        checkout scm
      }
    }

    stage("Build Images") {
      steps {
        sh """
          docker build -t $DOCKER_REPO:movie.$IMAGE_TAG ./movie-service
          docker build -t $DOCKER_REPO:cast.$IMAGE_TAG ./cast-service
        """
      }
    }

    stage("Push Images") {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub',
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          sh """
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker push $DOCKER_REPO:movie.$IMAGE_TAG
            docker push $DOCKER_REPO:cast.$IMAGE_TAG
            docker logout
          """
        }
      }
    }

    stage("Deploy DEV") {
      when { branch "dev" }
      steps {
        sh """
          helm upgrade --install jenkins-exam ./charts \
            -n dev --create-namespace \
            -f charts/values-dev.yaml \
            --set movie.image.tag=movie.$IMAGE_TAG \
            --set cast.image.tag=cast.$IMAGE_TAG
        """
      }
    }

    stage("Deploy QA") {
      when { branch "qa" }
      steps {
        sh """
          helm upgrade --install jenkins-exam ./charts \
            -n qa --create-namespace \
            -f charts/values-qa.yaml \
            --set movie.image.tag=movie.$IMAGE_TAG \
            --set cast.image.tag=cast.$IMAGE_TAG
        """
      }
    }

    stage("Deploy STAGING") {
      when { branch "staging" }
      steps {
        sh """
          helm upgrade --install jenkins-exam ./charts \
            -n staging --create-namespace \
            -f charts/values-staging.yaml \
            --set movie.image.tag=movie.$IMAGE_TAG \
            --set cast.image.tag=cast.$IMAGE_TAG
        """
      }
    }

    stage("Deploy PROD") {
      when { branch "master" }
      steps {
        sh """
          helm upgrade --install jenkins-exam ./charts \
            -n prod --create-namespace \
            -f charts/values-prod.yaml \
            --set movie.image.tag=movie.$IMAGE_TAG \
            --set cast.image.tag=cast.$IMAGE_TAG
        """
      }
    }
  }
}

