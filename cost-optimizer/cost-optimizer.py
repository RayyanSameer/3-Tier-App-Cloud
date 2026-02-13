import boto3
def get_orphan_volumes():
    ec2 = boto3.client('ec2', region_name='ap-south-1')