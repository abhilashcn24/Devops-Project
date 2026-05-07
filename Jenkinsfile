pipeline {
    agent any

    environment {
        IMAGE_NAME   = "notes-app"
        IMAGE_TAG    = "v${BUILD_NUMBER}"
        CONTAINER    = "notes-app-live"
        REGISTRY     = "abhilashcn2004"
        PORT         = "5000"
        PATH         = "C:\\Program Files\\Git\\bin;${env.PATH}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Code pulled: branch=${env.GIT_BRANCH}, commit=${env.GIT_COMMIT[0..6]}"
            }
        }

        stage('Build Image') {
            steps {
                script {
                    docker.build("${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}")
                }
                echo "🐳 Image built: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Smoke Test') {
            steps {
                script {
                    def testId = "smoke-${BUILD_NUMBER}"
                    bat "docker rm -f ${testId} || exit 0"
                    bat "docker run -d --name ${testId} -p 5100:5000 ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    sleep 5

                    def status = bat(
                        script: '@echo off\r\ncurl -s -o NUL -w "%%{http_code}" http://127.0.0.1:5100/health || echo 000',
                        returnStdout: true
                    ).trim()[-3..-1]

                    bat "docker rm -f ${testId} || exit 0"

                    if (status != '200') {
                        error("❌ Smoke test failed — /health returned ${status}")
                    }
                    echo "✅ Smoke test passed (HTTP ${status})"
                }
            }
        }

        stage('Push to Registry') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    bat 'docker login -u "%DH_USER%" -p "%DH_PASS%"'
                    bat "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    bat "docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest"
                    bat "docker push ${REGISTRY}/${IMAGE_NAME}:latest"
                }
                echo "📦 Image pushed to Docker Hub"
            }
        }

        stage('Deploy') {
            steps {
                script {
                    bat "docker stop ${CONTAINER} || exit 0"
                    bat "docker rm   ${CONTAINER} || exit 0"
                    bat "docker pull ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    bat "docker run -d --name ${CONTAINER} --restart unless-stopped -p ${PORT}:5000 ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                }
                echo "🚀 Container deployed on port ${PORT}"
            }
        }

        stage('Health Check') {
            steps {
                script {
                    sleep 5

                    def status = bat(
                        script: '@echo off\r\ncurl -s -o NUL -w "%%{http_code}" http://127.0.0.1:5000/health || echo 000',
                        returnStdout: true
                    ).trim()[-3..-1]

                    if (status != '200') {
                        error("❌ Post-deploy health check failed — HTTP ${status}")
                    }
                    echo "✅ Health check passed — app is live!"
                }
            }
        }

    }

    post {
        success {
            echo "🎉 Pipeline SUCCESS — ${IMAGE_NAME}:${IMAGE_TAG} is live on port ${PORT}"
            bat "docker image prune -f"
        }
        failure {
            echo "🔥 Pipeline FAILED — check logs above"
        }
    }

}