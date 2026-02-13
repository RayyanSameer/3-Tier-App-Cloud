import boto3
import datetime 
import datetime, timedelta

class EC2Scanner:
    def __init__(self, ec2_client, cw_client):
        self.ec2 = ec2_client
        self.cw = cw_client

    def get_ec2_waste(self):
        # 1. Get all instances
        response = self.ec2.describe_instances()
        waste_list = []

        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                
                instance_id = instance['InstanceId']
                state = instance['State']['Name']
                instance_type = instance['InstanceType']
                
                # CASE 1: The "Stopped" Instance
                if state == 'stopped':
                    item = {
                        "ID": instance_id,
                        "Reason": "Stopped (Paying for Storage)",
                        "Cost": 2.00 # Approximate EBS cost 
                    }
                    waste_list.append(item)
                    continue

                # CASE 2: The "Zombie" (Running but Idle)
                if state == 'running':
                    
                    metric = self.cw.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                        StartTime=datetime.utcnow() - timedelta(days=7), # Check last 7 days
                        EndTime=datetime.utcnow(),
                        Period=86400,
                        Statistics=['Average']
                    )
                    
                    # Check the data
                    datapoints = metric.get('Datapoints', [])
                    if datapoints:
                        
                        avg_cpu = datapoints[0]['Average']
                        
                        if avg_cpu < 1.0: 
                            item = {
                                "ID": instance_id,
                                "Reason": f"Low CPU ({avg_cpu:.2f}%) - Zombie",
                                "Cost": 20.00 # 
                            }
                            waste_list.append(item)
        
        return waste_list

def scan_ec2(ec2_client, cw_client):
    scanner = EC2Scanner(ec2_client, cw_client)
    return scanner.get_ec2_waste()
