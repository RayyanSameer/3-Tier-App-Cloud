import streamlit as st
import pandas as pd
import boto3
import time 

# --- IMPORT SCANNERS ---
from services.ebs import scan_ebs
from services.elastic_ip import scan_eip
from services.snapshot import scan_snapshots
from services.rds import scan_rds
from services.nat_gateway import scan_nat
from services.s3 import scan_s3
from services.ec2 import scan_ec2
from services.eks import scan_eks
from services.vpc import scan_vpc

# Handle optional ALB scanner
try:
    from services.alb import scan_alb
except ImportError:
    scan_alb = None  
    print("ALB scanner not found.")

# --- PAGE CONFIG ---
st.set_page_config(page_title="AWS Cost Optimizer", layout="wide")

st.title("💸 AWS Cost Optimizer")
st.markdown("""
**Stop wasting money on unused AWS resources!** This tool scans your AWS account for idle and underutilized resources, providing actionable insights to help you save costs.
""")

# --- SIDEBAR ---
with st.sidebar:
    st.header(" Scan Options")
    region = st.text_input("AWS Region", value="ap-south-1")

    # Use a button to trigger the state
    if st.button(" Start Scan"):
        st.session_state['scan_in_progress'] = True
    
    # Optional: Add a Reset button
    if st.button("Reset"):
        st.session_state['scan_in_progress'] = False

# --- MAIN CONTENT ---

if st.session_state.get('scan_in_progress', False):
    
    with st.spinner(f"Connecting to AWS ({region})..."):
        try:
            # Initialize Clients
            ec2 = boto3.client('ec2', region_name=region)
            elb = boto3.client('elbv2', region_name=region)
            cw = boto3.client('cloudwatch', region_name=region)
            rds = boto3.client('rds', region_name=region)
            s3 = boto3.client('s3', region_name=region)
            eks = boto3.client('eks', region_name=region)

            # Helper function to run scans
            progress_bar = st.progress(0)
            status = st.empty()

            def run_scan(name, func, args, progress):
                status.text(f"Scanning {name}...")
                data = func(*args) # Unpack arguments
                progress_bar.progress(progress)
                return data

            
            scans = [
                ("EBS Volumes", scan_ebs, [ec2]),
                ("Elastic IPs", scan_eip, [ec2]),
                ("Snapshots", scan_snapshots, [ec2]),
                ("RDS Instances", scan_rds, [rds, cw]),
                ("NAT Gateways", scan_nat, [ec2, cw]),
                ("S3 Buckets", scan_s3, [s3]),
                ("EC2 Instances", scan_ec2, [ec2, cw]),
                ("EKS Clusters", scan_eks, [eks]),
                ("VPCs", scan_vpc, [ec2])
            ]

            # Fix: Insert correctly as a single Tuple
            if scan_alb:
                scans.insert(2, ("Load Balancers", scan_alb, [elb, cw]))

            results = {}
            total_savings = 0.0

            step = 100 // len(scans)
            current_progress = 0

            # --- EXECUTION LOOP ---
            for name, func, args in scans:
             
                data = run_scan(name, func, args, current_progress)
                results[name] = data
                
              
                for item in data:
                    total_savings += float(item.get("Cost", 0.0))
                
                current_progress += step
                if current_progress > 100: current_progress = 100

            # Finalize
            progress_bar.progress(100)
            status.success(" Scan Complete!")
            time.sleep(1)
            progress_bar.empty()

            # --- DISPLAY RESULTS ---
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Potential Savings", value=f"${total_savings:.2f}", delta="Monthly Waste")
            with col2:
                st.metric(label="Services Scanned", value=len(scans))
            with col3:
                waste_count = sum(len(v) for v in results.values())
                st.metric(label="Resources Flagged", value=waste_count)

            st.subheader("🕵️ Detailed Findings")
            
            # Prepare Data for Table & Chart
            all_rows = []
            chart_data = []

            for service, items in results.items():
                service_total = 0.0
                for item in items:
                    cost = float(item.get('Cost', 0.0))
                    service_total += cost
                    all_rows.append({
                        "Service": service,
                        "Resource ID": item.get('ID'),
                        "Reason": item.get('Reason'),
                        "Cost ($)": f"${cost:.2f}"
                    })
                
                if service_total > 0:
                    chart_data.append({"Service": service, "Cost": service_total})

            # Display Table
            if all_rows:
                df = pd.DataFrame(all_rows)
                st.dataframe(df, use_container_width=True)

                # Display Chart
                st.subheader(" Cost Breakdown")
                if chart_data:
                    chart_df = pd.DataFrame(chart_data)
                    st.bar_chart(chart_df, x="Service", y="Cost")
            else:
                st.success(" No waste found! Your account is optimized.")

        except Exception as e:
            st.error(f"An error occurred: {e}")



