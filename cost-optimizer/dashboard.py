import boto3
from dashboard import generate_dashboard

# Import your scanners
from services.ebs import scan_ebs
from services.elastic_ip import scan_eip
from services.alb import scan_alb
from services.nat import scan_nat
from services.snapshots import scan_snapshots
from services.rds import scan_rds
from services.s3 import scan_s3
from services.ec2 import scan_ec2

def main():
    region = 'ap-south-1'
    
    # 1. Initialize Clients 
    ec2 = boto3.client('ec2', region_name=region)
    elb = boto3.client('elbv2', region_name=region)
    cw = boto3.client('cloudwatch', region_name=region)
    rds = boto3.client('rds', region_name=region)
    s3 = boto3.client('s3', region_name=region)

    print(f"\n🚀 Connecting to AWS ({region})... scanning resources...")

    # 2. Run Scanners & Aggregate Data
  
    cloud_data = {
        'EBS Volumes': scan_ebs(ec2),
        'Elastic IPs': scan_eip(ec2),
        'Load Balancers': scan_alb(elb, cw),
        'NAT Gateways': scan_nat(ec2, cw),
        'Snapshots': scan_snapshots(ec2),
        'RDS Instances': scan_rds(rds),
        'S3 Buckets': scan_s3(s3),
        'EC2 Instances': scan_ec2(ec2, cw)
    }

    # 3. Generate the Report
    generate_dashboard(cloud_data)

if __name__ == "__main__":
    main()