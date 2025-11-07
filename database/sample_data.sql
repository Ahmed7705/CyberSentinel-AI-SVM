USE cyber_sentinel_db;

DELETE FROM notifications;
DELETE FROM files;
DELETE FROM audit_logs;
DELETE FROM alerts;
DELETE FROM activity_logs;
DELETE FROM users;
INSERT INTO users (username, password_hash, full_name, role, department, is_active, last_login, created_at) VALUES
('admin', '$2b$12$F2hiR0YgJcGaNFqInlYJ7uHNB3cGv0oTPhSfKszYVSyWrtG9WnK8m', 'Aiden Hunt', 'admin', 'Security Operations', 1, '2025-01-08 09:12:00', '2025-11-01 08:00:00'),
('jdoe', '$2b$12$QXG8NwBnUv3YyoNuj66badZPntgd9YdJh7w7V7KHVUFThVj.dGgqe', 'Jordan Doe', 'user', 'Finance', 1, '2025-01-08 07:45:00', '2025-11-02 09:15:00'),
('ssmith', '$2b$12$XrK9PKqbf76TgYPQxO8Z1uexXww8JHcj8apLH8NuNpS3oZuZ0iKQy', 'Sloan Smith', 'user', 'HR', 1, '2025-01-08 06:30:00', '2025-11-05 13:20:00'),
('kwong', '$2b$12$6sdY1uC7lSPhFi6ntP25SeN6e3C6PwLTu5R.thD9dxD2kZl8qrsza', 'Kai Wong', 'user', 'R&D', 1, '2025-01-07 22:10:00', '2025-11-07 11:45:00'),
('mrobbins', '$2b$12$k89QO1C6u5nQd9ty2faS7OWX5lIv3nTA09R4zAmjhQn/BdGcs5RX.', 'Mila Robbins', 'user', 'IT', 1, '2025-01-07 21:03:00', '2025-11-08 10:00:00'),
('dpatel', '$2b$12$UgoVSzj6N8aHJpFy1qFUBOSQLpYMP4f2ZgT19mrcGvXvl0yvkwl7C', 'Dev Patel', 'analyst', 'Security Operations', 1, '2025-01-07 20:15:00', '2025-11-09 09:05:00'),
('rtaylor', '$2b$12$0Q6S9qVjgAA.ziJZVpG7JupLMnCD6tZ9xzHFuS9ex7NmPZK5H8uau', 'Riley Taylor', 'user', 'Marketing', 1, '2025-01-07 19:42:00', '2025-11-10 14:25:00'),
('lgarcia', '$2b$12$sT3xF6le1iCeF2MmpmP5Eevqn/Tgxc0mH6C/6a4wk2azNq0Pp1JRS', 'Lena Garcia', 'user', 'Finance', 1, '2025-01-07 18:05:00', '2025-11-11 08:55:00'),
('bking', '$2b$12$9z8vFm58pL7iKIR6ZcIe..n1/vdvY0pqttkq4VtGeaA0u9m0s5xe2', 'Bailey King', 'user', 'Product', 1, '2025-01-07 17:41:00', '2025-11-12 09:32:00'),
('cibarra', '$2b$12$7W49bi3ojlKxct9bYFRXxO68j9yvIlbJicHkKMfqCE1ytL0MBbfza', 'Carmen Ibarra', 'user', 'Legal', 1, '2025-01-07 16:18:00', '2025-11-12 11:08:00');
INSERT INTO activity_logs (user_id, event_type, source_ip, device, location, bytes_transferred, files_accessed, failed_attempts, session_duration, risk_score, timestamp) VALUES
(2, 'login', '10.0.1.25', 'Windows-Desktop-FIN01', 'NYC HQ', 0, 0, 0, 480, 0.10, '2025-01-08 07:45:00'),
(3, 'login', '10.0.2.18', 'Surface-Pro-HR03', 'LA Office', 0, 0, 0, 300, 0.15, '2025-01-08 06:30:00'),
(4, 'file_download', '10.0.3.44', 'MacBook-Pro-RD07', 'Remote', 5242880, 12, 0, 720, 0.42, '2025-01-07 22:10:00'),
(5, 'privilege_escalation', '10.0.5.12', 'ThinkPad-IT09', 'NYC HQ', 10240, 3, 2, 60, 0.82, '2025-01-07 21:03:00'),
(6, 'threat_detection', '10.0.9.11', 'SOC-VM-01', 'Security Center', 2048, 0, 0, 120, 0.20, '2025-01-07 20:15:00'),
(2, 'file_upload', '10.0.1.25', 'Windows-Desktop-FIN01', 'NYC HQ', 307200, 8, 0, 540, 0.33, '2025-01-07 19:55:00'),
(7, 'login', '10.0.6.32', 'MacBook-Air-MKT02', 'Remote', 0, 0, 1, 420, 0.28, '2025-01-07 19:42:00'),
(8, 'failed_login', '10.0.1.56', 'Dell-Latitude-FIN05', 'NYC HQ', 0, 0, 3, 30, 0.60, '2025-01-07 18:05:00'),
(9, 'mass_copy', '10.0.4.77', 'MacBook-Pro-PD01', 'Remote', 7340032, 85, 0, 180, 0.88, '2025-01-07 17:41:00'),
(10, 'login', '10.0.7.14', 'HP-Elite-LGL01', 'NYC HQ', 0, 0, 0, 600, 0.18, '2025-01-07 16:18:00');
INSERT INTO alerts (user_id, alert_type, description, risk_score, risk_level, status, metadata_json, resolution_note, created_at, resolved_at) VALUES
(5, 'Privilege Escalation', 'Unscheduled admin role granted to Mila Robbins', 0.92, 'critical', 'open', '{"source":"IAM","severity":"critical"}', NULL, '2025-01-07 21:04:00', NULL),
(9, 'Mass Data Copy', 'Bailey King copied 85 files totalling 7MB', 0.88, 'high', 'investigating', '{"files":85}', NULL, '2025-01-07 17:42:00', NULL),
(2, 'Unusual Upload Volume', 'Jordan Doe uploaded 8 files outside business hours', 0.67, 'medium', 'open', '{"time_window":"after_hours"}', NULL, '2025-01-07 20:10:00', NULL),
(3, 'VPN Location Change', 'Sloan Smith connected from Los Angeles after NYC login', 0.58, 'medium', 'resolved', '{"locations":["NYC","LA"]}', 'Validated travel itinerary', '2025-01-06 10:10:00', '2025-01-06 18:05:00'),
(8, 'Repeated Failed Logins', 'Lena Garcia had three consecutive failed attempts', 0.75, 'high', 'open', '{"attempts":3}', NULL, '2025-01-07 18:06:00', NULL),
(4, 'Large Download', 'Kai Wong downloaded 5MB of prototype data', 0.70, 'high', 'open', '{"bytes":5242880}', NULL, '2025-01-07 22:12:00', NULL),
(10, 'After Hours Login', 'Carmen Ibarra logged in at 4AM local time', 0.55, 'medium', 'resolved', '{"hour":4}', 'Confirmed legitimate due to case deadline', '2025-01-05 04:20:00', '2025-01-05 12:30:00'),
(6, 'Anomaly Detected', 'Dev Patel flagged suspicious lateral movement', 0.62, 'medium', 'open', '{"module":"SOC-Agent"}', NULL, '2025-01-07 20:16:00', NULL),
(7, 'IP Reputation Hit', 'Riley Taylor connected from IP flagged by threat intel', 0.81, 'high', 'open', '{"ip":"203.0.113.88"}', NULL, '2025-01-07 19:45:00', NULL),
(3, 'HR File Access Spike', 'Sloan Smith accessed 30 confidential files', 0.84, 'high', 'investigating', '{"files":30}', NULL, '2025-01-06 22:11:00', NULL);

INSERT INTO audit_logs (user_id, event_type, message, created_at) VALUES
(1, 'login_success', 'Admin console accessed by Aiden Hunt', '2025-01-08 09:12:00'),
(2, 'login_success', 'Jordan Doe authenticated via SSO', '2025-01-08 07:45:05'),
(3, 'password_reset', 'Password reset requested for Sloan Smith', '2025-01-07 21:00:00'),
(4, 'file_download', 'Prototype schematics downloaded by Kai Wong', '2025-01-07 22:10:30'),
(5, 'privilege_change', 'Temporary admin role granted to Mila Robbins', '2025-01-07 21:04:30'),
(6, 'alert_triage', 'Analyst Dev Patel triaged alert #42', '2025-01-07 20:20:00'),
(7, 'login_failed', 'Failed login attempt for Riley Taylor', '2025-01-07 19:41:00'),
(8, NULL, 'Global configuration export generated', '2025-01-07 18:06:30'),
(9, 'policy_ack', 'Bailey King acknowledged updated data policy', '2025-01-06 09:30:00'),
(10, 'login_success', 'Legal portal accessed by Carmen Ibarra', '2025-01-05 04:20:05');

INSERT INTO files (user_id, file_name, action, checksum, size_kb, created_at) VALUES
(4, 'prototype-drawings.pdf', 'download', 'ab4e5d8901234cd56ef7890ab1234567', 5024, '2025-01-07 22:11:00'),
(2, 'q4-financials.xlsx', 'upload', 'bc5f6a9012345de67fa8901bc2345678', 812, '2025-01-07 19:55:00'),
(3, 'employee-roster.csv', 'download', 'cd6g7b0123456ef78ab9012cd3456789', 245, '2025-01-07 18:45:00'),
(5, 'network-map.vsdx', 'share', 'de7h8c1234567fg89bc0123de4567890', 1420, '2025-01-07 21:05:00'),
(6, 'threat-intel-report.pdf', 'upload', 'ef8i9d2345678gh90cd1234ef5678901', 960, '2025-01-07 20:17:00'),
(7, 'campaign-plan.docx', 'download', 'f09j0e3456789hi01de2345f06789012', 512, '2025-01-07 19:43:00'),
(8, 'ledger-export.csv', 'upload', '012k1f4567890ij12ef3456017890123', 389, '2025-01-07 18:07:00'),
(9, 'design-assets.zip', 'download', '123l2g5678901jk23fg4567128901234', 7320, '2025-01-07 17:43:00'),
(10, 'merger-contract.docx', 'share', '234m3h6789012kl34gh5678239012345', 1024, '2025-01-07 16:20:00'),
(2, 'tax-documents.zip', 'delete', '345n4i7890123lm45hi6789340123456', 2048, '2025-01-06 08:55:00');

INSERT INTO user_files (user_id, filename, file_path, file_size, file_type, risk_level, uploaded_at) VALUES
(2, 'q4-financials.xlsx', 'uploads/user_files/2/q4-financials.xlsx', 831488, 'xlsx', 'medium', '2025-01-07 19:55:10'),
(3, 'employee-roster.csv', 'uploads/user_files/3/employee-roster.csv', 251904, 'csv', 'low', '2025-01-07 18:45:15'),
(4, 'prototype-drawings.pdf', 'uploads/user_files/4/prototype-drawings.pdf', 5144576, 'pdf', 'high', '2025-01-07 22:11:30'),
(8, 'ledger-export.csv', 'uploads/user_files/8/ledger-export.csv', 398336, 'csv', 'medium', '2025-01-07 18:07:25'),
(6, 'threat-intel-report.pdf', 'uploads/user_files/6/threat-intel-report.pdf', 983040, 'pdf', 'medium', '2025-01-07 20:17:45');

INSERT INTO notifications (user_id, title, message, is_read, created_at) VALUES
(1, 'New Alert Assigned', 'Critical privilege escalation alert requires review.', 0, '2025-01-07 21:05:00'),
(2, 'File Upload Complete', 'Your upload of q4-financials.xlsx finished successfully.', 1, '2025-01-07 19:56:00'),
(3, 'Password Reset', 'Your password reset was processed.', 1, '2025-01-07 21:01:00'),
(4, 'Security Notice', 'Large prototype download flagged for review.', 0, '2025-01-07 22:12:00'),
(5, 'Role Change', 'You temporarily hold elevated privileges.', 0, '2025-01-07 21:06:00'),
(6, 'Alert Queue Update', 'Two new alerts waiting in the escalation queue.', 0, '2025-01-07 20:18:00'),
(7, 'Failed Login Attempt', 'We noticed a failed login on your account.', 1, '2025-01-07 19:44:00'),
(8, 'Finance Policy Update', 'Review the new quarterly compliance checklist.', 0, '2025-01-07 18:08:00'),
(9, 'Design Delivery Reminder', 'Prototype assets shared with vendor partners.', 1, '2025-01-07 17:44:00'),
(10, 'Legal Deadline', 'Upcoming contract delivery due tomorrow morning.', 0, '2025-01-07 16:21:00');
