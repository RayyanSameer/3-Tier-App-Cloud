import boto3

class S3Scanner:
    def __init__(self, client):
        # 1. Store the tool in the robot's belt
        self.client = client

    def scan_regions(self):
        # 2. Use the stored tool
        response = self.client.list_buckets()
        
        print(f"Found {len(response['Buckets'])} buckets. Checking regions...")

        for bucket in response['Buckets']:
            name = bucket['Name']
            
            loc_response = self.client.get_bucket_location(Bucket=name)
            region = loc_response['LocationConstraint']
            try:
                public_access_status = self.client.get_public_access_block(Bucket = name)
            except ClientError as e:
                if e.response['Erreor']["Code"]  == 'NoSuchPublicAccessBlockConfiguration':
                    print(f" DANGER: {name} has NO Public Access Block! (Public?)")
                else:
                    print(f" Error checking {name}: {e}") 

            else:
                print("SECURE")        



            # The "us-east-1" Fix
            if region is None:
                region = "us-east-1"

            print(f"   > Bucket: {name} | Region: {region}")

# --- Execution ---
if __name__ == "__main__":
    s3 = boto3.client('s3')
    scanner = S3Scanner(s3)
    scanner.scan_regions()