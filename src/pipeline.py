"""
Healthcare Operations & Patient Analytics Pipeline
End-to-End Orchestrator:
1. Simulates/Loads Patient Care logs (CCM & RPM)
2. Executes Automated Data Cleansing and Anomaly Detection
3. Computes Operational KPIs (Minutes logged, Billing Eligibility, Coordinator Load)
4. Exports an Executive, Multi-Tab MS Excel Report
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_mock_datasets(num_patients=250, num_logs=3000):
    """Generates synthetic patient logs reflecting chronic care management (CCM)."""
    random.seed(42)
    np.random.seed(42)
    
    coordinators = [
        {"id": 101, "name": "Dr. Sarah Adams", "email": "s.adams@careorg.com"},
        {"id": 102, "name": "Marcus Chen, RN", "email": "m.chen@careorg.com"},
        {"id": 103, "name": "Priya Sharma, BSN", "email": "p.sharma@careorg.com"},
        {"id": 104, "name": "Elena Rostova, NP", "email": "e.rostova@careorg.com"}
    ]
    
    conditions = ["Hypertension", "Type 2 Diabetes", "COPD", "Congestive Heart Failure", "Chronic Kidney Disease"]
    encounter_types = ["Phone Call", "Telehealth Review", "Care Plan Update", "Medication Reconciliation"]
    
    # Generate Patient Master
    patients = []
    for i in range(1, num_patients + 1):
        pid = f"PAT-{i:04d}"
        coord = random.choice(coordinators)
        patients.append({
            "patient_id": pid,
            "patient_name": f"Patient_{i}",
            "primary_condition": random.choice(conditions),
            "coordinator_id": coord["id"],
            "coordinator_name": coord["name"],
            "coordinator_email": coord["email"],
            "enrollment_status": random.choices(["Active", "Suspended"], weights=[0.92, 0.08])[0]
        })
    df_patients = pd.DataFrame(patients)
    
    # Generate Encounter Logs with intentional real-world anomalies (dupes, missing vals)
    base_date = datetime(2026, 10, 1)
    logs = []
    for log_id in range(1, num_logs + 1):
        pat = random.choice(patients)
        days_offset = random.randint(0, 30)
        minutes_offset = random.randint(8 * 60, 18 * 60)
        timestamp = base_date + timedelta(days=days_offset, minutes=minutes_offset)
        
        # Duration: typical 5 to 25 mins
        duration = random.choice([5, 8, 10, 12, 15, 20, 25, 30])
        
        logs.append({
            "log_id": log_id,
            "patient_id": pat["patient_id"],
            "coordinator_id": pat["coordinator_id"],
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "encounter_type": random.choice(encounter_types),
            "duration_minutes": duration,
            "clinical_notes": f"Routine check-in regarding {pat['primary_condition']} management."
        })
    
    # Inject intentional duplicates and anomalies
    for _ in range(35):
        dupe = random.choice(logs).copy()
        dupe["log_id"] = len(logs) + 1
        logs.append(dupe)
        
    df_logs = pd.DataFrame(logs)
    return df_patients, df_logs

def clean_and_validate_data(df_patients, df_logs):
    """Applies validation rules, cleans schema, and strips duplicates."""
    print("-> Cleaning raw encounters and auditing integrity...")
    initial_log_count = len(df_logs)
    
    # 1. Deduplication on patient + timestamp window
    df_logs = df_logs.drop_duplicates(subset=["patient_id", "timestamp", "duration_minutes"])
    deduped_count = len(df_logs)
    
    # 2. Date parsing
    df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"])
    
    # 3. Join with patient master
    merged_df = pd.merge(df_logs, df_patients, on="patient_id", how="inner")
    
    # Filter active patients
    active_df = merged_df[merged_df["enrollment_status"] == "Active"].copy()
    
    print(f"   [Cleaned] Dropped {initial_log_count - deduped_count} duplicate logs. Processed {len(active_df)} active encounters.")
    return active_df

def compute_operational_kpis(df):
    """Calculates healthcare operational KPIs and billing eligibility."""
    print("-> Computing care management metrics & CMS thresholds...")
    
    # Group by patient to determine monthly minutes
    patient_summary = df.groupby(["patient_id", "patient_name", "primary_condition", "coordinator_name"]).agg(
        total_care_minutes=("duration_minutes", "sum"),
        total_encounters=("log_id", "count"),
        avg_encounter_duration=("duration_minutes", "mean")
    ).reset_index()
    
    # CMS Chronic Care Management (CCM) requires 20+ minutes of clinical staff time per month
    patient_summary["ccm_billing_eligible"] = patient_summary["total_care_minutes"].apply(
        lambda mins: "QUALIFIED (CPT 99490)" if mins >= 20 else "BELOW THRESHOLD"
    )
    
    # Coordinator Capacity Breakdown
    coordinator_summary = df.groupby("coordinator_name").agg(
        assigned_patients=("patient_id", "nunique"),
        total_minutes_delivered=("duration_minutes", "sum"),
        total_touchpoints=("log_id", "count")
    ).reset_index()
    coordinator_summary["avg_minutes_per_patient"] = (
        coordinator_summary["total_minutes_delivered"] / coordinator_summary["assigned_patients"]
    ).round(1)
    
    return patient_summary, coordinator_summary

def export_executive_excel(patient_summary, coordinator_summary, output_path="output/Monthly_Healthcare_Operations_Report.xlsx"):
    """Generates a structured, formatted multi-tab Excel workbook."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"-> Generating executive Excel report at {output_path}...")
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Tab 1: Executive KPI Summary
        total_patients = len(patient_summary)
        qualified = len(patient_summary[patient_summary["ccm_billing_eligible"].str.contains("QUALIFIED")])
        qual_rate = (qualified / total_patients) * 100 if total_patients else 0
        total_mins = patient_summary["total_care_minutes"].sum()
        
        exec_metrics = pd.DataFrame([
            {"Key Metric": "Total Monitored Patients", "Value": total_patients},
            {"Key Metric": "CCM Reimbursement Qualified (>=20 mins)", "Value": qualified},
            {"Key Metric": "Qualification Compliance Rate", "Value": f"{qual_rate:.1f}%"},
            {"Key Metric": "Total Clinical Care Minutes Delivered", "Value": f"{total_mins:,} mins"},
            {"Key Metric": "Avg Care Time Per Patient", "Value": f"{total_mins/total_patients:.1f} mins"}
        ])
        exec_metrics.to_excel(writer, sheet_name="Executive_Summary", index=False)
        
        # Tab 2: Patient Billing Roster
        patient_summary.to_excel(writer, sheet_name="Patient_Eligibility_Roster", index=False)
        
        # Tab 3: Coordinator Performance
        coordinator_summary.to_excel(writer, sheet_name="Coordinator_Breakdown", index=False)

    print(f"-> Successfully created: {output_path}")

def main():
    print("=" * 65)
    print("Circle Health - Automated Healthcare Operations Pipeline")
    print("=" * 65)
    df_patients, df_logs = generate_mock_datasets()
    cleaned_df = clean_and_validate_data(df_patients, df_logs)
    patient_summary, coord_summary = compute_operational_kpis(cleaned_df)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "..", "output", "Monthly_Healthcare_Operations_Report.xlsx")
    export_executive_excel(patient_summary, coord_summary, output_file)
    print("=" * 65)
    print("Pipeline Execution Completed Successfully.")

if __name__ == "__main__":
    main()
