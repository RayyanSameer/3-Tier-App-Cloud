#Finds unused NAT gateways 

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

        for nat in response['NatGateways']:
            nat_id = nat['NatGatewayId']
            state =   nat['State']

            if state != 'available':
                continue

            name = "N/A"
            if "Tags" in nat:
                for tag in nat['Tags']:
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
            
            metric_data = self.cw_client.get_metric_statistics(
                Namespace='AWS/NATGateway',
                MetricName='ConnectionEstablishedCount',
                Dimensions=[{'Name': 'NatGatewayId', 'Value': nat_id}],
                StartTime=datetime.utcnow() - timedelta(days=1), # Checking last 24h
                EndTime=datetime.utcnow(),
                Period=86400, # 24 hours
                Statistics=['Sum']
            )

            datapoints =metric_data.get("Datapoints", [])
            total_connections = 0

            if not datapoints or datapoints[0].get('Sum',0) == 0:
                item = {
                    "ID" : nat_id,
                    "Name": nat.get('Tags', [{'Value': 'N/A'}])[0]['Value'],
                    "Cost": 32.40


                }

                idle.append(item)
            return idle

        def scan_nat(ec2_client, cw_client):
            scanner = nat_scanner(ec2_client, cw_client)
            return scanner.get_idle_nats()
          