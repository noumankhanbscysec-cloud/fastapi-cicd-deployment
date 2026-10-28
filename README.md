<div align="center">

# 🚀 FastAPI CI/CD Deployment on AWS EC2

### Automated Backend Deployment with GitHub Actions

![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white)

I built this project to learn how **real-world DevOps deployment** works. A FastAPI backend runs on **AWS EC2**, and a **GitHub Actions self-hosted runner** automates application updates.

[🌐 Live API](http://3.25.244.145:8000/) · [📘 Swagger Docs](http://3.25.244.145:8000/docs) · [💻 Repository](https://github.com/noumankhanbscysec-cloud/fastapi-cicd-deployment)

</div>

---

## 📑 Table of Contents

- [🔗 Live Application](#-live-application)
- [🏗️ Architecture](#️-architecture)
- [🧰 Tech Stack](#-tech-stack)
- [✨ Features](#-features)
- [📜 Deployment Script](#-deployment-script)
- [🛠️ Challenges & Solutions](#️-challenges--solutions)
- [🎓 What I Learned](#-what-i-learned)
- [🔮 Future Improvements](#-future-improvements)
- [📌 Project Outcome](#-project-outcome)

---

## 🔗 Live Application

| Resource | Link |
|----------|------|
| 🌐 **Live API** | http://3.25.244.145:8000/ |
| 📘 **Swagger Documentation** | http://3.25.244.145:8000/docs |
| 💻 **GitHub Repository** | https://github.com/noumankhanbscysec-cloud/fastapi-cicd-deployment |

---

## 🏗️ Architecture

```mermaid
flowchart LR
    A[👨‍💻 Developer<br/>pushes code] --> B[🐙 GitHub]
    B --> C[⚙️ GitHub Actions<br/>workflow triggered]
    C --> D[🏃 Self-hosted runner<br/>on AWS EC2]
    D --> E[📜 deploy.sh]
    E --> F[🚀 FastAPI + Uvicorn<br/>port 8000]
```

**How it works:**

1. 👨‍💻 Developer pushes code to GitHub.
2. ⚙️ GitHub Actions triggers the deployment workflow.
3. 🏃 The self-hosted runner executes on AWS EC2.
4. 📜 The deployment script pulls the latest code, installs dependencies, restarts FastAPI, and checks the API response.
5. 🚀 The application runs using Uvicorn on port `8000`.

---

## 🧰 Tech Stack

| Category | Technologies |
|----------|--------------|
| ☁️ **Cloud** | AWS EC2, Amazon Linux 2023 |
| 🐍 **Backend** | Python, FastAPI, Uvicorn |
| 🔄 **CI/CD** | GitHub Actions, Self-hosted runner |
| 🔧 **Tools** | Git, GitHub, Bash scripting |
| 🐧 **System** | Linux, systemd |

---

## ✨ Features

- ☁️ Deployed a FastAPI backend on AWS EC2
- 📘 Published interactive API documentation using Swagger UI
- 🏃 Configured a self-hosted GitHub Actions runner
- 📜 Created a Bash deployment script
- 🔁 Automated dependency installation and service restart
- ✅ Added an API readiness check after deployment
- 🛒 Implemented product APIs for searching products and managing stock

---

## 📜 Deployment Script

The `deploy.sh` script automates these steps:

1. 📂 Navigate to the application directory
2. ⬇️ Pull the latest code from GitHub
3. 🐍 Activate the Python virtual environment
4. 📦 Install dependencies from `requirements.txt`
5. 🔄 Restart the FastAPI systemd service
6. 🩺 Check whether the API responds
7. 📣 Report deployment success or failure

**Run it manually:**

```bash
cd ~/fastapi-cicd-deployment
chmod +x deploy.sh
./deploy.sh
```

---

## 🛠️ Challenges & Solutions

### 1️⃣ Git Branch Divergence

> ❌ **Problem:** Git reported that my local and remote branches had diverged when pulling the latest code.

**🔍 Investigation:**

```bash
git status
git fetch origin
git log --oneline --graph --decorate -8
git log --oneline HEAD..origin/main
git log --oneline origin/main..HEAD
```

**✅ Solution:** After confirming the EC2 checkout should match GitHub, I synchronized it:

```bash
git fetch origin main
git reset --hard origin/main
git status
```

> 💡 **Learned:** How to compare local and remote Git histories and synchronize a deployment server safely.
> ⚠️ A hard reset discards local tracked changes, so only use it when those changes are safe to discard.

---

### 2️⃣ GitHub Actions Runner Session Conflict

> ❌ **Problem:** The runner stopped with the error: `A session for this runner already exists.`

**✅ Solution:** I stopped the runner service, checked for leftover processes, and started it again.

```bash
sudo systemctl stop actions.runner.noumankhanbscysec-cloud-fastapi-cicd-deployment.ip-172-31-41-226.service

pgrep -af 'Runner.Listener|runsvc.sh|RunnerService.js'

sudo systemctl start actions.runner.noumankhanbscysec-cloud-fastapi-cicd-deployment.ip-172-31-41-226.service

sudo systemctl status actions.runner.noumankhanbscysec-cloud-fastapi-cicd-deployment.ip-172-31-41-226.service --no-pager
```

The runner reconnected to GitHub and began listening for jobs. 🎉

> 💡 **Learned:** How to manage Linux services, inspect running processes, and troubleshoot self-hosted runners.

---

### 3️⃣ Deployment Job Failure

> ❌ **Problem:** The runner connected successfully, but a deployment job failed.

**🔍 Investigation:**

```bash
sudo journalctl -u actions.runner.noumankhanbscysec-cloud-fastapi-cicd-deployment.ip-172-31-41-226.service -n 50 --no-pager

sudo systemctl status fastapi --no-pager

sudo journalctl -u fastapi -n 50 --no-pager
```

**➡️ Next step:** Inspect the failed step in GitHub Actions to identify the exact cause.

> 💡 **Learned:** A runner being online does not guarantee a successful deployment. Workflow logs and application health checks are essential.

---

## 🎓 What I Learned

- ☁️ Deploying a Python backend on AWS EC2
- ⚡ Running FastAPI with Uvicorn
- 🐧 Managing Linux services with systemd
- 🌿 Using Git to manage and synchronize application code
- 🏃 Configuring a GitHub Actions self-hosted runner
- 📜 Automating deployment with Bash
- 🔍 Investigating CI/CD failures through logs
- 🩺 Verifying application health after deployment

---

## 🔮 Future Improvements

- [ ] 🔒 Configure HTTPS with a domain name
- [ ] 🧪 Add automated API tests before deployment
- [ ] 🛡️ Tighten security group and SSH access restrictions
- [ ] 🔑 Secure application credentials
- [ ] 💾 Implement database backups and deployment rollback
- [ ] 📊 Improve health checks and monitoring

---

## 📌 Project Outcome

I deployed a FastAPI backend on AWS EC2, configured GitHub Actions with a self-hosted runner, and created a script to automate application updates and service restarts.

This project gave me practical experience with **cloud infrastructure, Linux administration, Git, CI/CD, and real deployment troubleshooting**.

> 📍 **Current status:** The API is deployed and the runner has been restored. A successful end-to-end automated deployment still needs to be verified.

---

<div align="center">

⭐ If you found this project useful, consider giving it a star!

</div>
