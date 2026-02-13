import boto3

# Define filters for 'available' (unattached) volumes
Filters = [
    {'Name': 'status', 'Values': ['available']}
]

class ebs_check():
    def __init__(self, client):
        self.client = client

    def get_ebs(self):
       
        raw_volumes = self.client.describe_volumes(Filters=Filters)['Volumes']
        
        clean_list = []
        
        # If raw_volumes is empty, this loop just won't run
        for volume in raw_volumes:
            item = {
                "ID": volume['VolumeId'], 
                "Size": volume['Size'], 
                "Type": volume['VolumeType'], 
                "Cost": volume['Size'] * 0.08
            }
            clean_list.append(item)
            
        return clean_list
def scan_ebs(ec2_client):
    
    ebs_instance = ebs_check(ec2_client)
   
    return ebs_instance.get_ebs()