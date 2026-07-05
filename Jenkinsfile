pipeline {
    agent none

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
            agent { label 'test' }
            steps {
                echo "Fetching latest code from GitHub..."
                checkout scm
            }
        }
    

        stage('Build Docker Image') {
           agent { label 'test' }
            steps {
                script {
                    echo "Building Docker image of frontend..."
                    sh """
                        sudo docker build -t ${IMAGE_NAME_Frontend}:${IMAGE_TAG_Frontend} ./frontend
                        sudo docker build -t ${IMAGE_NAME_Backend}:${IMAGE_TAG_Backend} ./backend
                        
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
                            echo "$DOCKER_PASS" | sudo docker login -u "$DOCKER_USER" --password-stdin
                            sudo docker push ${IMAGE_NAME_Frontend}:${IMAGE_TAG_Frontend}
                            sudo docker push ${IMAGE_NAME_Backend}:${IMAGE_TAG_Backend} 
                            sudo docker logout
                         """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Docker Build, Test and Push completed successfully! Now cleaning up"
            }
        
        failure {
            echo "Docker Build, Test and Push failed! Now cleaning up"
            }
        }
    }
        
