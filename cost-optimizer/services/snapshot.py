import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone

class snapshot_scanner:
    def __init__(self, ec2_client):
        self.client = ec2_client

    def get_orphaned_snapshots(self):
        """
        Identifies snapshots that are truly 'orphaned' (no associated VolumeId ever recorded)
        and snapshots associated with volumes that no longer exist, filtering by a 30-day threshold.
        """
        try:
            # Get all snapshots owned by the account
            response = self.client.describe_snapshots(OwnerIds=['self'])
            snapshots = response['Snapshots']
            
            # Get a list of all currently active volume IDs
            active_volumes_response = self.client.describe_volumes()
            active_vols_ids = {v['VolumeId'] for v in active_volumes_response['Volumes']}

            orphaned_snapshots_list = []
            
            # Define the threshold for old snapshots (e.g., older than 30 days)
            threshold_date = datetime.now(timezone.utc) - timedelta(days=30)
            
            for snapshot in snapshots:
                snapshot_id = snapshot['SnapshotId']
                volume_id = snapshot.get('VolumeId')
                start_time = snapshot['StartTime']

                is_orphaned_no_volume_id = volume_id is None or volume_id == ''
                is_volume_deleted = volume_id not in active_vols_ids
                is_old = start_time < threshold_date

                # An "orphaned" snapshot for cleanup purposes meets two criteria:
                # 1. It is either completely unassociated with a volume OR
                # 2. Its associated volume no longer exists AND the snapshot is older than the threshold.

                if is_orphaned_no_volume_id or (is_volume_deleted and is_old):
                    item = {
                        "ID": snapshot_id,
                        "VolumeID": volume_id if volume_id else 'N/A',
                        "VolumeSizeGB": snapshot['VolumeSize'],
                        
                        "EstimatedMonthlyCost": 0.05 * snapshot['VolumeSize'] 
                    }
                    orphaned_snapshots_list.append(item)
            
            return orphaned_snapshots_list

        except ClientError as e:
            print(f"An error occurred while describing snapshots or volumes: {e}")
            return []

# --- Example Usage ---

def scan_snapshots():
  
    ec2_client = boto3.client('ec2', region_name='ap-south-1') 

    scanner = snapshot_scanner(ec2_client)
    snapshots = scanner.get_orphaned_snapshots()

    if snapshots:
        print(f"Found {len(snapshots)} potentially orphaned snapshots older than 30 days:")
        for snap in snapshots:
            print(f"ID: {snap['ID']}, Volume ID: {snap['VolumeID']}, Size: {snap['VolumeSizeGB']}GB, Est. Monthly Cost: ${snap['EstimatedMonthlyCost']:.2f}")
    else:
        print("No orphaned snapshots found or an error occurred.")

if __name__ == "__main__":
    scan_snapshots()

