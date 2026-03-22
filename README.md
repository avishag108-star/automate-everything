# 🚀 StatusWatch — GitOps Platform

> A production-grade GitOps platform built to demonstrate end-to-end DevOps engineering.
> Every code change automatically flows from **git push → CI/CD → Docker → Kubernetes → Live**.

![CI](https://github.com/YOUR_USERNAME/statuswatch-gitops-platform/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC)
![Kubernetes](https://img.shields.io/badge/orchestration-Kubernetes-326CE5)

---

## 🏗️ Architecture

```
Developer
    │
    │  git push
    ▼
GitHub Actions ──► Lint (flake8) ──► Tests (pytest) ──► Security Scan (Trivy)
    │
    │  docker build + push
    ▼
GitHub Container Registry (GHCR)
    │
    │  update k8s/helm/values.yaml (new image tag)
    ▼
ArgoCD (GitOps) ──► detects change ──► auto-deploys to Kubernetes
    │
    ▼
k3s Kubernetes Cluster (AWS EC2 t2.micro — Free Tier)
    ├── StatusWatch App (2 replicas — High Availability)
    ├── Prometheus (metrics collection)
    └── Grafana (dashboards + alerting)
```

---

## 🛠️ Tech Stack

| Layer | Tool | Why |
|---|---|---|
| **App** | Python FastAPI | Async, fast, auto-docs |
| **Container** | Docker multi-stage | Small image, secure |
| **CI/CD** | GitHub Actions | Free, integrated |
| **Registry** | GHCR | Free, no ECR cost |
| **GitOps** | ArgoCD | Auto-sync Git → K8s |
| **Orchestration** | k3s (Kubernetes) | Lightweight, free tier |
| **IaC** | Terraform | Reproducible infra |
| **Monitoring** | Prometheus + Grafana | Golden Signals |

---

## ✨ Key Features

- **Zero-touch deployment** — `git push` to `main` → live in ~3 minutes
- **GitOps** — cluster state is always in sync with Git (ArgoCD selfHeal)
- **Security** — non-root container, Trivy scanning, no secrets in code
- **Observability** — `/metrics` endpoint + Grafana dashboard
- **Self-healing** — K8s Liveness/Readiness probes restart failed pods
- **Free tier friendly** — runs on a single t2.micro (~$0/month)

---

## 📁 Project Structure

```
.
├── app/                        # FastAPI application
│   ├── main.py
│   ├── requirements.txt
│   └── tests/
├── .github/
│   └── workflows/
│       └── ci.yml              # Full CI/CD pipeline
├── infrastructure/
│   └── terraform/              # AWS IaC (VPC + EC2 + k3s)
├── k8s/
│   └── helm/                   # Helm chart for K8s deployment
├── gitops/
│   └── argocd/
│       └── application.yaml    # ArgoCD App — the GitOps config
├── monitoring/
│   └── values.yaml             # Prometheus + Grafana config
└── Dockerfile                  # Multi-stage build
```

---

## 🚀 Getting Started

### Prerequisites
- AWS account (free tier)
- Terraform >= 1.7
- GitHub account

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/statuswatch-gitops-platform
cd statuswatch-gitops-platform
```

### 2. Deploy Infrastructure
```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars  # fill in your values
terraform init
terraform plan
terraform apply
```

### 3. Bootstrap ArgoCD
```bash
# SSH into EC2
ssh ubuntu@$(terraform output -raw k3s_public_ip)

# Apply ArgoCD Application
kubectl apply -f /path/to/gitops/argocd/application.yaml
```

### 4. Push code — watch it deploy automatically 🎉
```bash
git commit -m "feat: my change"
git push origin main
# GitHub Actions runs → image pushed → ArgoCD syncs → deployed!
```

---

## 📊 Monitoring

Access Grafana at `http://<EC2_IP>:30300` (admin / changeme)

Dashboards include:
- HTTP request rate and error rate
- Pod CPU / Memory utilization
- Response time (p50, p95, p99)

---

## 💰 Cost

| Resource | Cost |
|---|---|
| EC2 t2.micro | **$0** (free tier) |
| GHCR | **$0** (free) |
| GitHub Actions | **$0** (2000 min/month free) |
| **Total** | **~$0/month** |

---

## 🔒 Security Highlights

- Container runs as **non-root user** (UID 1000)
- **No secrets in code** — uses environment variables
- **Trivy** scans for CVEs on every push
- Security Groups restrict access to necessary ports only

---

## 📝 What I Learned

- Setting up a **full GitOps workflow** with ArgoCD
- Writing a production-quality **multi-stage Dockerfile**
- Designing a **CI/CD pipeline** with testing, security scanning, and auto-deploy
- Managing infrastructure as code with **Terraform modules**
- Exposing **Prometheus metrics** from a Python app

---

*Built by [Your Name] — [LinkedIn](https://linkedin.com/in/yourprofile)*
