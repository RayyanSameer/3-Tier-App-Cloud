import boto3
from botocore.exceptions import ClientError

class snapshot_scanner():
    def __init__(self, ec2_client):
        self.client = ec2_client

    def get_orphaned_snapshots(self):
            #Get all snapshots owned by the account
            try:
                response = self.client.describe_snapshots(OwnerIds=['self'])
                snapshots = response['Snapshots']

                orphaned_snapshots = []

                for snapshot in snapshots:
                    #Check if the snapshot is associated with any volume
                    if 'VolumeId' not in snapshot:
                        item = {
                            "ID": snapshot['SnapshotId'],
                            "VolumeID": snapshot.get('VolumeId', 'N/A'),
                            "Cost": 0.05 * (snapshot['VolumeSize'] / 100) # Assuming $0.05 per 100GB-month
                        }
                        orphaned_snapshots.append(item)
                    return orphaned_snapshots
            except ClientError as e:
                print(f"An error occurred: {e}")
                return []


            def scan_snapshots(ec2_client):
                scanner = snapshot_scanner(ec2_client)
                return scanner.get_orphaned_snapshots()    