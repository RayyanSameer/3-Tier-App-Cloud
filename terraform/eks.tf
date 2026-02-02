#The EKS file here gets a computer system that runs Kubernetes.

module eks{
    source = "terraform-aws-modules/eks/aws"
    version = "19.15.3"
    cluster_name    = "webapp-eks-cluster"
    cluster_version = "1.31"

    cluster_endpoint_public_access  = true
    cluster_endpoint_private_access = true

    # The Network Configuration
    vpc_id     = module.vpc.vpc_id #Get VPC ID from VPC module
    subnet_ids = module.vpc.private_subnets #Get private subnets from VPC module

    #The security system
    enable_irsa = true

    #The actual worker nodes
    eks_managed_node_groups = {
        webapp_nodes = {
            desired_capacity = 2
            max_capacity     = 3
            min_capacity     = 1

            instance_types = ["t3.medium"]

            disk_size = 20

            tags = {
                Name = "webapp-eks-node"
            }

            capacity_type = "SPOT"

        }
    }

}

#Steps : 1) Import EKS module
#2) Define cluster name and version 
#3) Link VPC and subnets from VPC module
#4) Enable IRSA for better security
#5) Define worker nodes with desired, max and min capacity
#6) Specify instance types and disk size
#7) Add tags for better identification
#8) Use SPOT instances for cost efficiency
