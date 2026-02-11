import boto3
from services.ebs import scan_ebs
from services.elastic_ip import scan_eip

def main():
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    total_savings = 0.0
    
    print("-" * 30)
    print(" CLOUD COST SCANNER")
    print("-" * 30)

    # 1. EBS SCAN
    orphan_ebs = scan_ebs(ec2_client)
    for volume in orphan_ebs:
        print(f"[EBS] ID: {volume['ID']} | Size: {volume['Size']}GB | Cost: ${volume['Cost']:.2f}")
        total_savings += volume['Cost']

    # 2. EIP SCAN
    orphan_elastic_ips = scan_eip(ec2_client)
    for eip in orphan_elastic_ips:
   
        print(f"[EIP] ID: {eip['ID']} | IP: {eip['PublicIP']} | Cost: ${eip['Cost']:.2f}")
        total_savings += eip['Cost']

    print("-" * 30)
    if total_savings == 0:
        print(" SUCCESS: Your cloud is clean!")
    else:
        print(f" TOTAL POTENTIAL SAVINGS: ${total_savings:.2f} / month")
    print("-" * 30)

if __name__ == "__main__":
    main()