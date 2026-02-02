Cloud-Native 3-Tier Application (AWS EKS)

A distributed, containerized 3-Tier Web Application deployed on AWS Elastic Kubernetes Service (EKS).

The Purpose: This project serves as the "Traffic Generator" (or "Victim App") for a larger FinOps initiative. It is architected to utilize real-world cloud resources (Load Balancers, NAT Gateways, PVCs) to generate meaningful billing data, which will later be analyzed by a Cloud Cost Observer tool.
🏗 Architecture

The application follows a modern microservices-style architecture:

    Frontend: React.js (Serving the UI).

    Backend: Python Flask (REST API).

    Database: PostgreSQL (Persistent Storage).

    Cache: Redis (High-speed caching & counter).

    Infrastructure: AWS VPC (Public/Private Subnets) + EKS Cluster.

📂 Project Structure
Bash

.
├── backend/                # Flask API & Requirements
├── frontend/               # React App & Assets
├── terraform/              # Infrastructure as Code (AWS EKS/VPC)
├── docker-compose.yml      # Local Development Orchestration
├── .gitignore              # Git exclusions
└── README.md               # Documentation

🚀 Getting Started
Prerequisites

    Docker & Docker Compose

    Terraform (v1.5+)

    AWS CLI (configured with aws configure)

    kubectl

1. Local Development (Docker)

To run the full stack locally on your machine (simulating the cloud environment):
Bash

# Clone the repository
git clone <your-repo-url>
cd 3-tier-devops-capstone

# Create environment variables
echo "DB_USER=admin\nDB_PASSWORD=secretpassword" > .env

# Spin up the containers
docker-compose up --build

    Frontend: http://localhost:3000

    Backend API: http://localhost:5000

☁️ Infrastructure Deployment (Terraform)

We use Terraform to provision a production-ready VPC and EKS Cluster.
Step 1: Initialize
Bash

cd terraform
terraform init

Step 2: Plan & Apply

Review the resources to be created (VPC, Subnets, NAT Gateways, EKS Control Plane, Worker Nodes).
Bash

terraform plan
terraform apply --auto-approve

⏳ Estimated Time: 15-20 minutes.
Step 3: Connect to Cluster

Once the infrastructure is ready, update your local kubectl context:
Bash

aws eks update-kubeconfig --region ap-south-1 --name todo-app-cluster

Step 4: Verify

Check if the Worker Nodes are online:
Bash

kubectl get nodes

🛠 Roadmap

    [x] Phase 1: Containerization (Dockerize Frontend/Backend/DB).

    [x] Phase 2: Infrastructure (VPC & EKS provisioning via Terraform).

    [ ] Phase 3: CI/CD Pipeline (GitHub Actions -> AWS ECR -> EKS).

    [ ] Phase 4: Monitoring (Prometheus/Grafana for metrics).

    [ ] Phase 5: Cost Analysis (Integration with Cost Observer tool).

💰 Cost Warning (FinOps)

Running this infrastructure incurs costs.

    EKS Control Plane: ~$0.10/hr

    NAT Gateway: ~$0.05/hr + Data processing

    EC2 Instances: Depends on t3.medium usage.

⚠️ Always destroy resources when not in use:
Bash

cd terraform
terraform destroy --auto-approve