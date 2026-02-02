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