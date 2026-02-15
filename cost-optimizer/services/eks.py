import boto3
class eks_scanner:
    def __init__(self ,eks_client):
        self.eks = eks_client

    def get_clusters(self):
        try:
            clusters = self.eks.list_clusters()[clusters]
            waste_clusters = []

            for cluster in clusters:
                waste_clusters.append({
                    "ID": cluster,
                    "Reason": "Control Plane is bill able",
                    "Cost" : 72.00 #Monthly flat
                })    

            return waste_clusters
        except Exception as e:
            print(f"An error has occured scanning EKS: {e}")    
            return[]
        
def scan_eks(eks_client):
    scanner = eks_scanner(eks_client)
    return scanner.get_clusters()        