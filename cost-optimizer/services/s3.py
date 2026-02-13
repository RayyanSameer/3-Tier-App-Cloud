#Finds empty or old buckets with no lifecycle tier enabled 

import boto3
from datetime import datetime, timezone

class S3Scanner:
    def __init__(self, s3_client):
        self.s3 = s3_client

    def get_s3_waste(self):
        # 1. Get the list of all buckets
        try:
            response = self.s3.list_buckets()
            buckets = response.get('Buckets', [])
        except Exception as e:
            print(f"Error listing buckets: {e}")
            return []

        waste_list = []

        for bucket in buckets:
            name = bucket['Name']
            
            try:
                
                objects = self.s3.list_objects_v2(Bucket=name, MaxKeys=1)
                
                # CHECK 1: Is the bucket completely empty?
                if objects['KeyCount'] == 0:
                    item = {
                        "ID": name,
                        "Reason": "Empty Bucket (Clutter)",
                        "Cost": 0.00 
                    }
                    waste_list.append(item)
                    continue

                # CHECK 2: Is the bucket "Stale"? 
                last_modified = objects['Contents'][0]['LastModified']
                
                # Calculate age in days
                days_inactive = (datetime.now(timezone.utc) - last_modified).days
                
                if days_inactive > 180:
                    item = {
                        "ID": name,
                        "Reason": f"Stale Data ({days_inactive} days old)",
                        "Cost": 2.50 
                    }
                    waste_list.append(item)

            except Exception as e:
               
                continue

        return waste_list

def scan_s3(s3_client):
    scanner = S3Scanner(s3_client)
    return scanner.get_s3_waste()