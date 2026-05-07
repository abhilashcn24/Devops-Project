pipeline {
    agent any

    environment {
        IMAGE_NAME   = "notes-app"
        IMAGE_TAG    = "v${BUILD_NUMBER}"
        CONTAINER    = "notes-app-live"
        REGISTRY     = "abhilashcn2004"        // ← configured Docker Hub ID
        PORT         = "5000"
        PATH         = "C:\\Program Files\\Git\\bin;${env.PATH}"
    }

    stages {

        // ── 1. Source ─────────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Code pulled: branch=${env.GIT_BRANCH}, commit=${env.GIT_COMMIT[0..6]}"
            }
        }

        // ── 2. Build ──────────────────────────────────────────────────────
        stage('Build Image') {
            steps {
                script {
                    docker.build("${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}")
                }
                echo "🐳 Image built: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        // ── 3. Test (Smoke) ───────────────────────────────────────────────
        stage('Smoke Test') {
            steps {
                script {
                    def testId = "smoke-${BUILD_NUMBER}"
                    bat "docker rm -f ${testId} || exit 0"
                    bat "docker run -d --name ${testId} -p 5100:5000 ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

                    def status = ''
                    try {
                        timeout(time: 60, unit: 'SECONDS') {
                            waitUntil {
                                status = bat(
                                    script: '@echo off\r\ncurl -s -o NUL -w "%%{http_code}" http://127.0.0.1:5100/health || echo 000',
                                    returnStdout: true
                                ).trim().takeRight(3)
                                return status == '200'
                            }
                        }
                    } finally {
                        if (status != '200') {
                            bat "docker ps -a --filter name=${testId}"
                            bat "docker logs ${testId} || exit 0"
                        }
                        bat "docker rm -f ${testId} || exit 0"
                    }

                    if (status != '200') {
                        error("❌ Smoke test failed — /health returned ${status}. Check docker logs above.")
                    }
                    echo "✅ Smoke test passed (HTTP ${status})"
                }
            }
        }

        // ── 4. Push ───────────────────────────────────────────────────────
        stage('Push to Registry') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    bat 'docker login -u "%DH_USER%" -p "%DH_PASS%"'
                    bat "docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    // Also tag as latest
                    bat "docker tag ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest"
                    bat "docker push ${REGISTRY}/${IMAGE_NAME}:latest"
                }
                echo "📦 Image pushed to Docker Hub"
            }
        }

        // ── 5. Deploy ─────────────────────────────────────────────────────
        stage('Deploy') {
            steps {
                script {
                    // Gracefully stop the old container (ignore error if not running)
                    bat "docker stop ${CONTAINER} || exit 0"
                    bat "docker rm   ${CONTAINER} || exit 0"

                    // Pull latest and launch
                    bat """
                        docker pull ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker run -d --name ${CONTAINER} --restart unless-stopped -p ${PORT}:5000 ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                    """
                }
                echo "🚀 Container deployed on port ${PORT}"
            }
        }

        // ── 6. Health Check ───────────────────────────────────────────────
        stage('Health Check') {
            steps {
                script {
                    def status = ''
                    try {
                        timeout(time: 60, unit: 'SECONDS') {
                            waitUntil {
                                status = bat(
                                    script: '@echo off\r\ncurl -s -o NUL -w "%%{http_code}" http://127.0.0.1:%PORT%/health || echo 000',
                                    returnStdout: true
                                ).trim().takeRight(3)
                                return status == '200'
                            }
                        }
                    } finally {
                        if (status != '200') {
                            bat "docker ps -a --filter name=${CONTAINER}"
                            bat "docker logs ${CONTAINER} || exit 0"
                        }
                    }

                    if (status != '200') {
                        error("❌ Post-deploy health check failed — HTTP ${status}")
                    }
                    echo "✅ Health check passed — app is live!"
                }
            }
        }

    }   // end stages

    post {
        success {
            echo "🎉 Pipeline SUCCESS — ${IMAGE_NAME}:${IMAGE_TAG} is live on port ${PORT}"
            // Prune dangling images to keep the host clean
            bat "docker image prune -f"
        }
        failure {
            echo "🔥 Pipeline FAILED — check logs above"
        }
    }

}
