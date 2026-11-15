-- GatePass Database Schema
-- DBMS Project: Smart Visitor & Delivery Management System
-- Target: MySQL 8.0.16+ (enforces CHECK constraints)

CREATE DATABASE IF NOT EXISTS gatepass_db CHARACTER SET utf8mb4;
USE gatepass_db;

-- 1. Residents Table
CREATE TABLE IF NOT EXISTS residents (
    resident_id INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    flat_no     VARCHAR(10)  NOT NULL,
    phone       VARCHAR(15)  NOT NULL UNIQUE,
    email       VARCHAR(120) UNIQUE,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_residents_flat (flat_no)
);

-- 2. Visitors Table
CREATE TABLE IF NOT EXISTS visitors (
    visitor_id   INT AUTO_INCREMENT PRIMARY KEY,
    visitor_name VARCHAR(100) NOT NULL,
    phone        VARCHAR(15)  NOT NULL UNIQUE,
    is_active    BOOLEAN NOT NULL DEFAULT TRUE
);

-- 3. Security Staff Table
CREATE TABLE IF NOT EXISTS security_staff (
    staff_id   INT AUTO_INCREMENT PRIMARY KEY,
    staff_name VARCHAR(100) NOT NULL,
    phone      VARCHAR(15)  NOT NULL UNIQUE,
    shift      ENUM('Morning','Evening','Night') NOT NULL DEFAULT 'Morning',
    is_active  BOOLEAN NOT NULL DEFAULT TRUE
);

-- 4. Delivery Agents Table
CREATE TABLE IF NOT EXISTS delivery_agents (
    agent_id        INT AUTO_INCREMENT PRIMARY KEY,
    agent_name      VARCHAR(100) NOT NULL,
    phone           VARCHAR(15)  NOT NULL UNIQUE,
    courier_company VARCHAR(80)  NOT NULL
);

-- 5. Users Table (Authentication & RBAC)
CREATE TABLE IF NOT EXISTS users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('admin','security','resident') NOT NULL,
    staff_id      INT NULL,
    resident_id   INT NULL,
    FOREIGN KEY (staff_id)    REFERENCES security_staff(staff_id) ON DELETE SET NULL,
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id) ON DELETE SET NULL
);

-- 6. Visits Table
CREATE TABLE IF NOT EXISTS visits (
    visit_id        INT AUTO_INCREMENT PRIMARY KEY,
    visitor_id      INT NOT NULL,
    resident_id     INT NOT NULL,
    staff_id        INT NOT NULL,
    purpose         VARCHAR(150) NOT NULL,
    visit_date      DATE NOT NULL DEFAULT (CURRENT_DATE),
    approval_status ENUM('Pending','Approved','Rejected','Cancelled') NOT NULL DEFAULT 'Pending',
    gate_pass_no    VARCHAR(25) UNIQUE,
    entry_time      DATETIME NULL,
    exit_time       DATETIME NULL,
    FOREIGN KEY (visitor_id)  REFERENCES visitors(visitor_id),
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id),
    FOREIGN KEY (staff_id)    REFERENCES security_staff(staff_id),
    CONSTRAINT chk_times CHECK (
        exit_time IS NULL OR (entry_time IS NOT NULL AND exit_time >= entry_time)
    ),
    INDEX idx_visits_date   (visit_date),
    INDEX idx_visits_status (approval_status)
);

-- 7. Deliveries Table
CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id   INT AUTO_INCREMENT PRIMARY KEY,
    resident_id   INT NOT NULL,
    staff_id      INT NOT NULL,
    agent_id      INT NOT NULL,
    delivery_type ENUM('Courier','Food','Other') NOT NULL,
    status        ENUM('Arrived','Received','Returned') NOT NULL DEFAULT 'Arrived',
    arrived_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    received_at   DATETIME NULL,
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id),
    FOREIGN KEY (staff_id)    REFERENCES security_staff(staff_id),
    FOREIGN KEY (agent_id)    REFERENCES delivery_agents(agent_id),
    INDEX idx_deliveries_status (status)
);

-- 8. View: Reusable History Report (Concept 7 in Section 7)
CREATE OR REPLACE VIEW v_visit_history AS
SELECT v.visit_id, v.visit_date, vi.visitor_name, vi.phone AS visitor_phone,
       v.purpose, r.name AS resident_name, r.flat_no,
       s.staff_name AS guard, v.approval_status, v.gate_pass_no,
       v.entry_time, v.exit_time
FROM visits v
JOIN visitors vi       ON v.visitor_id  = vi.visitor_id
JOIN residents r       ON v.resident_id = r.resident_id
JOIN security_staff s  ON v.staff_id    = s.staff_id;
