CREATE TABLE IF NOT EXISTS incidents (
    incident_id VARCHAR(50) PRIMARY KEY,
    opened_at DATETIME,
    contact_type VARCHAR(100),
    location VARCHAR(255),
    category VARCHAR(255),
    subcategory VARCHAR(255),
    symptom VARCHAR(255),
    impact VARCHAR(50),
    urgency VARCHAR(50),
    priority VARCHAR(50),
    caller_id VARCHAR(255),
    opened_by VARCHAR(255),
    assignment_group VARCHAR(255),
    assigned_to VARCHAR(255),
    resolved_at DATETIME,
    closed_at DATETIME,
    made_sla BOOLEAN,
    resolution_time_hours FLOAT
);

CREATE TABLE IF NOT EXISTS incident_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id VARCHAR(50),
    event_timestamp DATETIME,
    incident_state VARCHAR(100),
    active BOOLEAN,
    reassignment_count INT,
    reopen_count INT,
    sys_mod_count INT,
    assignment_group VARCHAR(255),
    assigned_to VARCHAR(255),
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);

CREATE TABLE IF NOT EXISTS incident_predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id VARCHAR(50) NULL,
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    sla_breach_probability FLOAT,
    sla_risk_level VARCHAR(50),
    estimated_resolution_hours FLOAT,
    prediction_timestamp DATETIME,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);
