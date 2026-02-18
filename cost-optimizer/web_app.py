import streamlit as st
import pandas as pd
import boto3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# --- PAGE CONFIG ---
st.set_page_config(page_title="AWS Cost Optimizer", layout="wide", page_icon="")

st.title(" AWS Cost Optimizer")
st.markdown("""
**Stop wasting money.** This tool scans your AWS account in parallel to find idle resources instantly.
""")

# --- SIDEBAR ---
with st.sidebar:
    st.header(" Configuration")
    region = st.text_input("AWS Region", value="ap-south-1")
    
    # Debug mode toggle
    debug_mode = st.checkbox(" Debug Mode", value=True)
    
    if st.button(" Run Fast Scan"):
        st.session_state['scan_in_progress'] = True
        st.session_state['scan_completed'] = False
    
    # Reset button
    if st.button(" Reset"):
        st.session_state['scan_in_progress'] = False
        st.session_state['scan_completed'] = False
        st.rerun()

# --- MAIN LOGIC ---
if st.session_state.get('scan_in_progress', False) and not st.session_state.get('scan_completed', False):
    
    # 1. INITIALIZE CLIENTS (Fast)
    with st.spinner(f" Connecting to AWS ({region})..."):
        try:
            session = boto3.Session(region_name=region)
            
            # Verify credentials
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            st.sidebar.success(f"✅ Connected as: {identity['Arn'].split('/')[-1]}")
            
            ec2 = session.client('ec2')
            elb = session.client('elbv2')
            cw = session.client('cloudwatch')
            rds = session.client('rds')
            s3 = session.client('s3')
            eks = session.client('eks')
            
        except Exception as e:
            st.error(f" AWS Connection Error: {e}")
            st.info(" Make sure AWS credentials are configured (`aws configure`)")
            st.session_state['scan_in_progress'] = False
            st.stop()

    # 2. DEFINE SCANS
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

    if scan_alb:
        scans.insert(2, ("Load Balancers", scan_alb, [elb, cw]))

    # 3. RUN PARALLEL SCANS
    results = {}
    total_savings = 0.0
    scan_errors = {}
    
    # UI Elements for Progress (OUTSIDE spinner to make them visible)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # The ThreadPool Engine
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks to the pool
        future_to_name = {
            executor.submit(func, *args): name 
            for name, func, args in scans
        }
        
        completed_count = 0
        total_scans = len(scans)
        
        # Process as they finish (First Come, First Served)
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                data = future.result()
                
                # CRITICAL: Validate data structure
                if data is None:
                    if debug_mode:
                        st.warning(f" {name} returned None (missing return statement?)")
                    data = []
                
                if not isinstance(data, list):
                    if debug_mode:
                        st.warning(f" {name} returned {type(data).__name__} instead of list")
                    data = []
                
                # Validate each item has required keys
                validated_data = []
                for i, item in enumerate(data):
                    if not isinstance(item, dict):
                        if debug_mode:
                            st.warning(f" {name} item {i} is not a dict: {type(item).__name__}")
                        continue
                    
                    # Try to extract data with flexible key names
                    resource_id = (item.get('ID') or item.get('id') or 
                                 item.get('ResourceId') or item.get('resource_id') or 
                                 'N/A')
                    
                    reason = (item.get('Reason') or item.get('reason') or 
                            item.get('Description') or item.get('description') or 
                            'No reason provided')
                    
                    cost = item.get('Cost') or item.get('cost') or 0.0
                    
                    # Try to convert cost to float
                    try:
                        cost = float(cost)
                    except (ValueError, TypeError):
                        if debug_mode:
                            st.warning(f" {name}: Invalid cost value '{cost}' for {resource_id}")
                        cost = 0.0
                    
                    validated_data.append({
                        'ID': resource_id,
                        'Reason': reason,
                        'Cost': cost
                    })
                
                results[name] = validated_data
                
                # Calculate savings immediately
                for item in validated_data:
                    total_savings += item['Cost']
                    
            except Exception as e:
                results[name] = []
                scan_errors[name] = str(e)
                st.toast(f" Error scanning {name}: {e}", icon="")
            
            # Update Progress
            completed_count += 1
            progress = completed_count / total_scans
            progress_bar.progress(progress)
            status_text.text(f" Finished: {name} ({completed_count}/{total_scans})")

    time.sleep(0.3)
    progress_bar.empty()
    status_text.empty()
    
    # Mark scan as completed
    st.session_state['scan_completed'] = True
    st.session_state['results'] = results
    st.session_state['total_savings'] = total_savings
    st.session_state['scan_errors'] = scan_errors

# 4. DISPLAY RESULTS (separate from scanning)
if st.session_state.get('scan_completed', False):
    results = st.session_state.get('results', {})
    total_savings = st.session_state.get('total_savings', 0.0)
    scan_errors = st.session_state.get('scan_errors', {})
    
    st.divider()
    
    # Show errors if any
    if scan_errors and debug_mode:
        with st.expander(" Scan Errors", expanded=False):
            for service, error in scan_errors.items():
                st.error(f"**{service}:** {error}")
    
    # Top Metrics
    c1, c2, c3 = st.columns(3)
    total_items = sum(len(v) for v in results.values())
    c1.metric(" Total Monthly Waste", f"${total_savings:.2f}", delta="Potential Savings")
    c2.metric(" Services Scanned", len(results))
    c3.metric(" Resources Flagged", total_items)
    
    # Debug: Show raw results structure
    if debug_mode:
        with st.expander("🔍 Debug: Raw Scan Results", expanded=False):
            for service, items in results.items():
                st.write(f"**{service}:** {len(items)} items")
                if items:
                    st.json(items[:2])  # Show first 2 items
    
    # Detailed Table
    st.subheader(" Detailed Findings")
    
    all_rows = []
    chart_data = []

    for service, items in results.items():
        service_total = 0.0
        for item in items:
            cost = item['Cost']
            service_total += cost
            all_rows.append({
                "Service": service,
                "Resource ID": item['ID'],
                "Reason": item['Reason'],
                "Cost": cost  # Keep as number for sorting
            })
        
        if service_total > 0:
            chart_data.append({"Service": service, "Cost": service_total})

    if all_rows:
        df = pd.DataFrame(all_rows)
        # Format Cost column for display
        df['Cost ($)'] = df['Cost'].apply(lambda x: f"${x:.2f}")
        
        # Sort by most expensive
        df = df.sort_values(by="Cost", ascending=False)
        
        st.dataframe(
            df[["Service", "Resource ID", "Reason", "Cost ($)"]], 
            use_container_width=True,
            hide_index=True
        )

        # Bar Chart
        st.subheader("Waste by Service")
        if chart_data:
            chart_df = pd.DataFrame(chart_data).set_index("Service")
            st.bar_chart(chart_df)
            
        # Download button
        csv = df[["Service", "Resource ID", "Reason", "Cost ($)"]].to_csv(index=False)
        st.download_button(
            label="📥 Download CSV Report",
            data=csv,
            file_name=f"aws_waste_report_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.balloons()
        st.success(" Your AWS account is squeaky clean! No waste found.")
        st.info("**Services checked:** " + ", ".join(results.keys()))
        
        # Show what was checked even if empty
        if debug_mode:
            with st.expander("Show Empty Scan Results"):
                for service in results.keys():
                    st.write(f"✅ {service}: 0 idle resources")