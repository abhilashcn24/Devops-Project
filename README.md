# 🚀 The Launchpad — Smart Notes CI/CD

> Git → GitHub → Jenkins → Docker → Live in minutes.

## Project Structure

```
launchpad/
├── app.py               # Flask application
├── templates/
│   ├── index.html       # Notes dashboard
│   └── edit.html        # Edit note view
├── requirements.txt     # Python deps
├── Dockerfile           # Container definition
├── Jenkinsfile          # Pipeline-as-code
└── .dockerignore
```

## Quick Start (Local)

```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

## Run with Docker

```bash
docker build -t notes-app:latest .
docker run -d -p 5000:5000 --name notes-app-live notes-app:latest
# → http://localhost:5000
```

## CI/CD Setup

### 1. Jenkins Prerequisites
- Jenkins with **Pipeline** + **Docker Pipeline** plugins
- Docker installed on the Jenkins agent
- DockerHub credential stored as `dockerhub-creds` (username/password)

### 2. Configure the Jenkinsfile
Edit line 7 in `Jenkinsfile`:
```groovy
REGISTRY = "your-dockerhub-username"   // ← your Docker Hub username
```

### 3. Create Jenkins Pipeline Job
1. New Item → Pipeline
2. Pipeline Definition → **Pipeline script from SCM**
3. SCM → Git → paste your repo URL
4. Script Path → `Jenkinsfile`
5. Enable **GitHub hook trigger for GITScm polling**

### 4. Add GitHub Webhook
In your GitHub repo → Settings → Webhooks → Add:
```
Payload URL:  http://<your-jenkins-host>:8080/github-webhook/
Content type: application/json
Trigger:      Just the push event
```

### Pipeline Stages

| Stage | What Happens |
|-------|-------------|
| Checkout | Jenkins pulls latest code from GitHub |
| Build Image | Dockerfile builds a versioned image |
| Smoke Test | Temp container spun up; `/health` checked |
| Push to Registry | Image pushed to Docker Hub |
| Deploy | Old container stopped; new one launched |
| Health Check | Live container's `/health` verified |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Notes dashboard |
| `/add` | POST | Create a note |
| `/edit/<id>` | GET/POST | Edit a note |
| `/delete/<id>` | POST | Delete a note |
| `/health` | GET | Liveness probe → `{"status":"ok"}` |
