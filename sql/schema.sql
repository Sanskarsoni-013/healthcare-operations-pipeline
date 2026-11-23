-- ========================================================
-- Schema: healthcare_operations
-- Relational model for Chronic Care (CCM) & Remote Monitoring (RPM)
-- ========================================================

CREATE DATABASE IF NOT EXISTS healthcare_operations;
USE healthcare_operations;

-- 1. Care Coordinators Table
CREATE TABLE IF NOT EXISTS care_coordinators (
    coordinator_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    region VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Patients Table
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    primary_condition VARCHAR(100),
    assigned_coordinator_id INT,
    enrollment_date DATE NOT NULL,
    status ENUM('Active', 'Suspended', 'Discharged') DEFAULT 'Active',
    FOREIGN KEY (assigned_coordinator_id) REFERENCES care_coordinators(coordinator_id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_coordinator (assigned_coordinator_id)
);

-- 3. Care Encounter Logs (CCM Time Tracking)
CREATE TABLE IF NOT EXISTS care_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    coordinator_id INT NOT NULL,
    encounter_timestamp DATETIME NOT NULL,
    duration_minutes INT NOT NULL,
    encounter_type ENUM('Phone Call', 'Telehealth Review', 'Care Plan Update', 'Medication Reconciliation') NOT NULL,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (coordinator_id) REFERENCES care_coordinators(coordinator_id),
    INDEX idx_patient_time (patient_id, encounter_timestamp),
    INDEX idx_coordinator_time (coordinator_id, encounter_timestamp)
);

-- 4. Remote Patient Monitoring (RPM) Device Telemetry
CREATE TABLE IF NOT EXISTS rpm_readings (
    reading_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    device_type ENUM('Blood Pressure Monitor', 'Pulse Oximeter', 'Blood Glucose Meter', 'Weight Scale') NOT NULL,
    reading_timestamp DATETIME NOT NULL,
    reading_value_primary DECIMAL(6,2) NOT NULL,
    reading_value_secondary DECIMAL(6,2),
    is_abnormal BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_reading_date (patient_id, reading_timestamp)
);

-- ========================================================
-- Analytical View: Monthly CCM Billing Eligibility
-- ========================================================
CREATE OR REPLACE VIEW v_monthly_ccm_summary AS
SELECT 
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    c.email AS coordinator_email,
    DATE_FORMAT(cl.encounter_timestamp, '%Y-%m') AS report_month,
    SUM(cl.duration_minutes) AS total_minutes_logged,
    COUNT(cl.log_id) AS total_encounters,
    CASE 
        WHEN SUM(cl.duration_minutes) >= 20 THEN 'QUALIFIED (CPT 99490)'
        ELSE 'BELOW_THRESHOLD'
    END AS billing_status
FROM patients p
JOIN care_logs cl ON p.patient_id = cl.patient_id
JOIN care_coordinators c ON cl.coordinator_id = c.coordinator_id
WHERE p.status = 'Active'
GROUP BY p.patient_id, patient_name, c.email, report_month;
