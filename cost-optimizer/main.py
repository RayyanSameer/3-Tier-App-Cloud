import boto3
from services.ebs import scan_ebs

def main():
    ec2_client = boto3.client('ec2', region_name='ap-south-1')
    orphan_ebs = scan_ebs(ec2_client)
    
    for volume in orphan_ebs:
        print(f"Volume ID: {volume['ID']}, Size: {volume['Size']} GB, Type: {volume['Type']}, Estimated Monthly Cost: ${volume['Cost']}")

if __name__ == "__main__":
    main()

