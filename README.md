[README.md](https://github.com/user-attachments/files/30736373/README.md)
# Automated FastAPI Deployment Pipeline Using GitHub Actions and a Self-Hosted WSL Runner

A DevOps / Cloud Engineering portfolio project: a FastAPI **Ecommerce API**, developed in a WSL Ubuntu environment, hosted as a persistent `systemd` service, and released automatically through a self-hosted **GitHub Actions** CI/CD pipeline.

## Overview

Every push to `main` triggers an automated pipeline that pulls the latest code, reinstalls dependencies, and restarts the live FastAPI service — no manual deployment steps required.

```
Developer → git push origin main → GitHub → GitHub Actions
   → Self-Hosted Runner (WSL Ubuntu) → deploy.sh
   → git pull · pip install -r requirements.txt · systemctl restart fastapi
   → Running FastAPI Application
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI 0.109.0, Python 3.14 |
| Server | Uvicorn 0.27.0, Gunicorn 21.2.0 |
| OS / Host | Ubuntu (WSL 2) |
| Process supervision | systemd (`fastapi.service`, `Restart=always`) |
| CI/CD | GitHub Actions, self-hosted runner |
| Automation | Bash (`deploy.sh`) |
| Docs | Swagger UI / OpenAPI 3.1 (`/docs`) |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Home |
| GET | `/products` | List products |
| GET | `/products/{product_id}` | Get product by ID |
| GET | `/products/slug/{slug}` | Get product by slug |
| POST | `/admin/products` | Create product |
| PUT | `/admin/products/{product_id}` | Update product |
| DELETE | `/admin/products/{product_id}` | Delete product |
| GET | `/admin/overview` | Admin overview |

## Deployment Script (`deploy.sh`)

```bash
set -e
cd /home/robot/fb_clone-website
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fastapi
```

## systemd Service (`fastapi.service`)

```ini
[Unit]
Description=Ecommerce FastAPI API
After=network.target

[Service]
User=robot
WorkingDirectory=/home/robot/fb_clone-website
Environment="PATH=/home/robot/fb_clone-website/venv/bin"
ExecStart=/home/robot/fb_clone-website/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Skills Demonstrated

- FastAPI backend development & REST API design
- Linux environment setup and administration (WSL Ubuntu)
- Python dependency management (`venv`, `requirements.txt`)
- systemd service configuration for production-style app hosting
- CI/CD pipeline design with GitHub Actions
- Self-hosted runner installation, registration, and operation
- Shell scripting for deployment automation
- Git/GitHub workflow (branching, rebasing, pushing) across Windows + WSL
- Pipeline debugging (diagnosing and fixing a failed Actions run)

## Future Improvements

- Docker containerization
- Deployment to a managed cloud platform (AWS / Azure / GCP) or Kubernetes
- Automated testing as a CI gate







- Monitoring with Prometheus & Grafana
- Infrastructure as Code with Terraform just change 
- HTTPS via reverse proxy + hardened secrets handling

---
*Full project write-up with annotated screenshots: see `Project_Portfolio_Documentation.docx       `.*





