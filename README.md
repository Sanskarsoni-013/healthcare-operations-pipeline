# Healthcare Operations & Patient Analytics Pipeline

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458.svg)](https://pandas.pydata.org/)
[![Excel](https://img.shields.io/badge/MS_Excel-Reporting-217346.svg)](https://microsoft.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, automated data pipeline designed to ingest, cleanse, analyze, and generate executive reporting workbooks for healthcare care coordination programs (**Chronic Care Management - CCM**, **Remote Patient Monitoring - RPM**, and **Behavioral Health Integration - BHI**).

---

## 🎯 Background & Problem Statement
In value-based healthcare, clinical organizations manage thousands of chronically ill patients across distributed care teams. Operational reporting frequently suffers from:
- **Disparate Data Sources**: Fragmented logs across electronic health records (EHR), telemetry device syncs, and manual call logs.
- **Manual Overhead**: Care managers spend hundreds of hours manually auditing monthly engagement thresholds (e.g., qualifying minutes for CMS reimbursement codes like 99490/99457).
- **Data Quality Issues**: Duplicate touchpoint logs, inconsistent phone formatting, and unverified patient status records.

This pipeline automates ingestion, enforces data integrity rules, calculates program compliance KPIs, and outputs a formatted, multi-tab **MS Excel Executive Dashboard** alongside queryable SQL schemas.

---

## 🏗️ Architecture & Workflow

```text
[ Raw CSV/JSON Exports ]
       │
       ▼
[ Data Validation & Cleaning (Pandas/Regex) ]
  ├── Schema conformance & null handling
  ├── Deduplication & phone standardization
  └── Timestamp validation
       │
       ▼
[ Metrics & Analytics Engine ]
  ├── Monthly Care Minutes Aggregation (CCM 20+ min threshold)
  ├── RPM Telemetry Device Compliance (16+ days threshold)
  └── Coordinator Performance & Capacity Ratios
       │
       ├─────────────────────────┐
       ▼                         ▼
[ Polished Excel Workbook ]  [ MySQL Relational Storage ]
  • Executive Summary Tab      • Normalized Patient & Call Logs
  • Coordinator KPI Breakdown  • Queryable Analytical Views
  • Audit Exception Log        • Indexed for sub-second retrieval
```

---

## 🚀 Key Features

1. **Automated Data Cleaning**:
   - Strips anomalies, invalid timestamps, and non-standard patient IDs.
   - Cleans and standardizes patient phone records with regex parsing.
   - Resolves duplicate touchpoint entries within a 15-minute sliding window.

2. **Healthcare Operations Analytics**:
   - **CCM Eligibility Tracking**: Identifies patients meeting the CMS 20-minute monthly clinical care requirement.
   - **RPM Device Compliance**: Tracks device transmission frequencies (e.g. blood pressure, glucometers) against monthly compliance targets.
   - **Care Manager Caseload Efficiency**: Summarizes hours logged, patient touchpoint frequency, and turnaround time per coordinator.

3. **Multi-Tab Excel Generation (`OpenPyXL`)**:
   - Auto-formats headers with corporate styling.
   - Dynamically calculates summary KPIs (Total Patients, Qualifying Rate %, Total Engagement Minutes).
   - Generates tabular views ready for instant Pivot Table and Slicer interactions.

4. **Production-Ready Relational SQL**:
   - 3NF-compliant schema (`patients`, `care_coordinators`, `care_logs`, `rpm_readings`).
   - Window functions and Common Table Expressions (CTEs) for advanced cohort analysis.

---

## 📁 Repository Structure

```text
healthcare-operations-pipeline/
│
├── data/                       # Raw and processed sample data
│   ├── raw_patient_logs.csv
│   └── mock_rpm_readings.csv
│
├── sql/                        # Relational database schemas & views
│   ├── schema.sql
│   └── analytics_queries.sql
│
├── src/                        # Core application code
│   ├── generate_mock_data.py   # Synthesizes realistic 20,000+ patient records
│   ├── cleaner.py              # Data hygiene and validation routines
│   ├── analytics.py            # Healthcare KPI aggregation engine
│   └── pipeline.py             # Orchestrates ingestion -> cleaning -> Excel export
│
├── output/                     # Auto-generated Excel reports
│   └── Monthly_Healthcare_Operations_Report.xlsx
│
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/sanskar-soni/healthcare-operations-pipeline.git
cd healthcare-operations-pipeline
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate mock EHR data & run pipeline
```bash
python src/pipeline.py
```
*The pipeline will automatically synthesize realistic patient care logs, validate data, compute KPIs, and generate `output/Monthly_Healthcare_Operations_Report.xlsx`.*

---

## 📊 Sample Metrics & Output Preview

| Metric | Raw Ingested | Post-Cleansing | Qualified for Reimbursement |
| :--- | :---: | :---: | :---: |
| **Total Patient Encounters** | 12,450 | 11,890 (560 dupes purged) | 8,920 (75.0%) |
| **Total Care Minutes Logged**| 248,300 | 242,100 | - |
| **RPM Active Transmissions** | 1,200 devices | 1,180 active | 940 (≥ 16 days reading) |

---

## 👤 Author
- **Sanskar Soni** - [LinkedIn](https://linkedin.com/in/sanskar-soni-669382311) • [GitHub](https://github.com/sanskar-soni)
