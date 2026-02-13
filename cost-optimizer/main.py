import boto3
from services.ebs import scan_ebs
from services.elastic_ip import scan_eip
from services.alb import scan_alb
from services.snapshot import scan_snapshots
from services.rds import scan_rds
from services.nat import scan_nat



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

    # 3. ALB SCAN
    elb_client = boto3.client('elbv2', region_name='ap-south-1')
    cw_client = boto3.client('cloudwatch', region_name='ap-south-1')

    orphan_albs = scan_alb(elb_client, cw_client)
    for alb in orphan_albs:
        print(f"[ALB] ID: {alb['ID']} | Name: {alb['Name']} | Cost: ${alb['Cost']:.2f}")
        total_savings += alb['Cost']   

    # 4. SNAPSHOT SCAN
    snapshot_list = []
    try:
        response = ec2_client.describe_snapshots(OwnerIds=['self'])
        for snapshot in response['Snapshots']:
            if snapshot['State'] == 'completed':
                snapshot_list.append({
                    "ID": snapshot['SnapshotId'],
                    "Size": snapshot['VolumeSize'],
                    "Cost": 0.0  
                })
    except Exception as e:
        print(f"Error scanning snapshots: {e}")

        for snapshot in snapshot_list:
            print(f"[SNAPSHOT] ID: {snapshot['ID']} | Size: {snapshot['Size']}GB | Cost: ${snapshot['Cost']:.2f}")

    #5 RDS SCAN
    rds_client = boto3.client('rds', region_name='ap-south-1')
    rds_list = scan_rds(rds_client)
    for rds in rds_list:
        print(f"[RDS] ID: {rds['ID']} | Engine: {rds['Engine']} | Cost: ${rds['Cost']:.2f}")
        total_savings += rds['Cost']

    #NAT GATEWAY 

    for nat in scan_nat(ec2_client, cw_client):
        print(f"[NAT] {nat['ID']} - ${nat['Cost']}")
    total_savings += nat['Cost']

        



       

    

      

    print("-" * 30)
    if total_savings == 0:
        print(" SUCCESS: Your cloud is clean!")
    else:
        print(f" TOTAL POTENTIAL SAVINGS: ${total_savings:.2f} / month")
    print("-" * 30)


    

    

    
        

if __name__ == "__main__":
    main()