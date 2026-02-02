output "cluster_endpoint" {
    description = "Endpoint for EKS control plane"
    value       = module.eks.cluster_endpoint
  
}
output "cluster_security_group_id" {
    description = "Security group ID for EKS cluster"
    value       = module.eks.cluster_security_group_id

  
}

output "region" {
    description = "AWS Region"
    value = "ap-south-1"

  
}

output "cluster_name" {
    description = "Kubernetes cluster name : "
    value = module.eks.cluster_name
  
}

output "ecr_frontend_url" {
  value = aws_ecr_repository.todo-frontend-repo.repository_url
}

output "ecr_backend_url" {
  value = aws_ecr_repository.todo-backend-repo.repository_url
}