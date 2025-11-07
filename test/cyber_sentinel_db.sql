-- Create and select the database
CREATE DATABASE IF NOT EXISTS cyber_sentinel_db;
USE cyber_sentinel_db;

-- ===============================
-- USERS TABLE
-- ===============================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50),
    position VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ===============================
-- ACTIVITY LOGS TABLE
-- ===============================
DROP TABLE IF EXISTS activity_logs;
CREATE TABLE activity_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    activity_type ENUM('login', 'logout', 'file_access', 'data_copy', 'file_modify', 'data_download') NOT NULL,
    timestamp DATETIME NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSON,
    risk_score FLOAT DEFAULT 0,
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_anomaly (is_anomaly)
);

-- ===============================
-- ALERTS TABLE
-- ===============================
DROP TABLE IF EXISTS alerts;
CREATE TABLE alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    risk_level ENUM('low', 'medium', 'high') NOT NULL,
    description TEXT NOT NULL,
    risk_score FLOAT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME,
    resolved_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_risk_level (risk_level),
    INDEX idx_timestamp (timestamp),
    INDEX idx_resolved (is_resolved)
);

-- ===============================
-- SAMPLE DATA
-- ===============================

-- Password hash placeholder (use same dummy hash for simplicity)
SET @hash = '$2b$12$LQv3c1yqBWVHxkd0g8f7O.FfT5L5BfPv5n8Yb6Vc5c5c5c5c5c5c5c5c';

-- USERS
INSERT INTO users (username, password_hash, role, full_name, email, department, position) VALUES
('admin', @hash, 'admin', 'System Administrator', 'admin@cybersentinel.ai', 'IT', 'System Admin'),
('mohammed.hakami', @hash, 'user', 'Mohammed Al-Hakami', 'mohammed@cybersentinel.ai', 'Cybersecurity', 'AI Analyst'),
('janan.rayyani', @hash, 'user', 'Janan Yacoub Rayyani', 'janan@cybersentinel.ai', 'Finance', 'Financial Controller'),
('layan.mohammed', @hash, 'user', 'Layan Mohammed', 'layan@cybersentinel.ai', 'HR', 'HR Specialist'),
('nasser.almshqab', @hash, 'user', 'Nasser Al-Mshqab', 'nasser@cybersentinel.ai', 'IT', 'System Engineer'),
('rahaf.abkar', @hash, 'user', 'Rahaf Abkar', 'rahaf@cybersentinel.ai', 'Legal', 'Compliance Officer'),
('manar.allami', @hash, 'user', 'Manar Ibrahim Allami', 'manar@cybersentinel.ai', 'Operations', 'Data Analyst'),
('arjwan.asuni', @hash, 'user', 'Arjwan Asuni', 'arjwan@cybersentinel.ai', 'Marketing', 'Digital Strategist'),
('ruba.atiah', @hash, 'user', 'Ruba Ali Atiah', 'ruba@cybersentinel.ai', 'Sales', 'Account Manager'),
('yosef.hassan', @hash, 'user', 'Yosef Hassan', 'yosef@cybersentinel.ai', 'Support', 'Helpdesk Agent');

-- ===============================
-- ACTIVITY LOGS
-- (dates between Oct 13–27, 2025 and one in future: Nov 3, 2025)
-- ===============================

INSERT INTO activity_logs (user_id, activity_type, timestamp, ip_address, details, risk_score, is_anomaly, anomaly_reason) VALUES
(2, 'login',       '2025-10-13 08:42:00', '192.168.10.14', '{"browser":"Chrome","os":"Windows 11"}', 0.10, FALSE, NULL),
(2, 'file_access', '2025-10-14 09:05:00', '192.168.10.14', '{"file":"incident_report.pdf","action":"view"}', 0.25, FALSE, NULL),
(3, 'login',       '2025-10-15 23:55:00', '192.168.10.21', '{"browser":"Firefox","os":"macOS"}', 0.80, TRUE, 'Late-night login after hours'),
(4, 'data_copy',   '2025-10-16 02:40:00', '192.168.10.30', '{"files":120,"total_size":"1.8GB"}', 0.90, TRUE, 'Large data transfer detected'),
(5, 'file_modify', '2025-10-17 09:35:00', '192.168.10.40', '{"file":"system_config.json"}', 0.30, FALSE, NULL),
(6, 'login',       '2025-10-18 07:50:00', '192.168.10.45', '{"browser":"Edge","os":"Windows 10"}', 0.15, FALSE, NULL),
(7, 'data_download','2025-10-19 22:15:00','192.168.10.55', '{"file":"raw_logs.zip","size":"2.2GB"}', 0.75, TRUE, 'Large data download after working hours'),
(8, 'logout',      '2025-10-20 16:30:00', '192.168.10.60', '{"session_duration":"6h"}', 0.05, FALSE, NULL),
(9, 'login',       '2025-10-21 09:00:00', '192.168.10.75', '{"browser":"Safari","os":"macOS"}', 0.10, FALSE, NULL),
(10,'file_access', '2025-11-03 11:10:00', '192.168.10.80', '{"file":"support_tickets.csv","action":"download"}', 0.50, TRUE, 'Unusual file download from remote location');

-- ===============================
-- ALERTS
-- ===============================

INSERT INTO alerts (user_id, alert_type, timestamp, risk_level, description, risk_score, is_resolved) VALUES
(3, 'Late Night Login',   '2025-10-15 23:55:00', 'high',   'User Janan logged in after midnight — potential insider activity.', 0.80, FALSE),
(4, 'Mass Data Copy',     '2025-10-16 02:40:00', 'high',   'Layan copied over 1.8GB of data outside working hours.', 0.90, FALSE),
(7, 'Large Data Download','2025-10-19 22:15:00', 'medium', 'Manar downloaded 2.2GB of system logs at 10:15 PM.', 0.75, TRUE),
(2, 'Multiple Login Attempts','2025-10-13 08:42:00','medium','Mohammed attempted 3 logins within 5 minutes.', 0.65, TRUE),
(5, 'Config File Change', '2025-10-17 09:35:00', 'low',    'Nasser modified a configuration file.', 0.35, TRUE),
(6, 'Unusual Login IP',   '2025-10-18 07:50:00', 'medium', 'Rahaf logged in from unrecognized IP 192.168.10.45.', 0.55, FALSE),
(9, 'Suspicious Login Location','2025-10-21 09:00:00','medium','Ruba logged in from new city (Jeddah).',0.60,FALSE),
(10,'Remote Download',    '2025-11-03 11:10:00', 'high',   'Yosef downloaded sensitive support data from external IP.', 0.82, FALSE),
(8, 'Session Timeout',    '2025-10-20 16:30:00', 'low',    'Arjwan remained logged in for over 6 hours.', 0.30, TRUE),
(3, 'Email Attachment Anomaly','2025-10-24 14:10:00','medium','Janan sent 5 large attachments (500MB) to external contact.',0.70,FALSE);
