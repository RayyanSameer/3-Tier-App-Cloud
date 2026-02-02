#Creating a VPC to house the infrastructure

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  #define AZs
  azs = ["ap-south-1a","ap-south-b"]
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.101.0/24","10.0.102.0/24"]
  
  enable_nat_gateway = true
  single_nat_gateway = true

    tags = {
        Terraform   = "true"
        Environment = "dev"
    }


    #Steps : 1) Import vpc module
    #2) Define variables such as name, cidr, azs, subnets
    #3) Enable nat gateway for private subnets to access internet
    #4) Add tags for better identification
}    