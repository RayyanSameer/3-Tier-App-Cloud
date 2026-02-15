import boto3
from datetime import datetime, timedelta 

class nat_scanner:
    def __init__(self, ec2_client, cw_client):
        self.ec2 = ec2_client
        self.cw = cw_client 

    def get_idle_nats(self):
        print("Scanning for NAT Gateways...")
        response = self.ec2.describe_nat_gateways()

        idle = []

        # Use .get() to be safe
        for nat in response.get('NatGateways', []):
            nat_id = nat['NatGatewayId']
            state = nat['State']

            if state != 'available':
                continue

            # --- Logic to find Name Tag ---
            name = "N/A"
            if "Tags" in nat:
                for tag in nat['Tags']:
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
            
            # --- CloudWatch Check ---
            try:
      
                metric_data = self.cw.get_metric_statistics(
                    Namespace='AWS/NATGateway',
                    MetricName='ConnectionEstablishedCount',
                    Dimensions=[{'Name': 'NatGatewayId', 'Value': nat_id}],
                    StartTime=datetime.utcnow() - timedelta(days=1),
                    EndTime=datetime.utcnow(),
                    Period=86400,
                    Statistics=['Sum']
                )

                datapoints = metric_data.get("Datapoints", [])

                # Logic: If no data points OR sum is 0
                if not datapoints or datapoints[0].get('Sum', 0) == 0:
                    item = {
                        "ID": nat_id,
                        "Name": name, 
                        "Cost": 32.40,
                        "Reason": "Idle (0 Connections)"
                    }
                    idle.append(item)
            
            except Exception as e:
                print(f"Error checking NAT {nat_id}: {e}")
                continue

        return idle 

def scan_nat(ec2_client, cw_client): 
    scanner = nat_scanner(ec2_client, cw_client)
    return scanner.get_idle_nats()