pipeline {
    agent any
    triggers {
        githubPush()
    }
    environment {
        IMAGE_NAME_Frontend = "raichu08/threetierappfe"
        IMAGE_TAG_Frontend = "v${BUILD_NUMBER}"
        IMAGE_NAME_Backend = "raichu08/threetierappbk"
        IMAGE_TAG_Backend = "v${BUILD_NUMBER}"
    }
    stages {
        stage('Checkout Code') {
            steps {
                echo "Fetching latest code from GitHub..."
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker images..."
                    sh """
                        set -e
                        docker build -t ${IMAGE_NAME_Frontend}:${IMAGE_TAG_Frontend} ./frontend
                        docker build -t ${IMAGE_NAME_Backend}:${IMAGE_TAG_Backend} ./backend
                    """
                }
            }
        }

        stage('Push to Dockerhub and Logout') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'Dhub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh """
                            set -e
                            echo "Logging into Docker..."
                            echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                            docker push ${IMAGE_NAME_Frontend}:${IMAGE_TAG_Frontend}
                            docker push ${IMAGE_NAME_Backend}:${IMAGE_TAG_Backend}
                            docker logout
                        """
                    }
                }
            }
        }
    }
    post {
        always {
            sh """
                docker rmi ${IMAGE_NAME_Frontend}:${IMAGE_TAG_Frontend} || true
                docker rmi ${IMAGE_NAME_Backend}:${IMAGE_TAG_Backend} || true
                docker image prune -f || true
            """
        }
        success {
            echo "Docker Build, Test and Push completed successfully!"
        }
        failure {
            echo "Docker Build, Test and Push failed!"
        }
    }
}
