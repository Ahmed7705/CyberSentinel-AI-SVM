-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 29, 2025 at 03:29 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cyber_sentinel_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `activity_logs`
--

CREATE TABLE `activity_logs` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `event_type` varchar(80) NOT NULL,
  `source_ip` varchar(45) NOT NULL,
  `device` varchar(80) NOT NULL,
  `location` varchar(120) NOT NULL,
  `bytes_transferred` bigint(20) DEFAULT 0,
  `files_accessed` int(11) DEFAULT 0,
  `failed_attempts` int(11) DEFAULT 0,
  `session_duration` int(11) DEFAULT 0,
  `risk_score` decimal(5,2) DEFAULT 0.00,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `activity_logs`
--

INSERT INTO `activity_logs` (`id`, `user_id`, `event_type`, `source_ip`, `device`, `location`, `bytes_transferred`, `files_accessed`, `failed_attempts`, `session_duration`, `risk_score`, `timestamp`) VALUES
(1, 2, 'login', '10.0.1.25', 'Windows-Desktop-FIN01', 'NYC HQ', 0, 0, 0, 480, 0.10, '2025-01-08 07:45:00'),
(2, 3, 'login', '10.0.2.18', 'Surface-Pro-HR03', 'LA Office', 0, 0, 0, 300, 0.15, '2025-01-08 06:30:00'),
(3, 4, 'file_download', '10.0.3.44', 'MacBook-Pro-RD07', 'Remote', 5242880, 12, 0, 720, 0.42, '2025-01-07 22:10:00'),
(4, 5, 'privilege_escalation', '10.0.5.12', 'ThinkPad-IT09', 'NYC HQ', 10240, 3, 2, 60, 0.82, '2025-01-07 21:03:00'),
(5, 6, 'threat_detection', '10.0.9.11', 'SOC-VM-01', 'Security Center', 2048, 0, 0, 120, 0.20, '2025-01-07 20:15:00'),
(6, 2, 'file_upload', '10.0.1.25', 'Windows-Desktop-FIN01', 'NYC HQ', 307200, 8, 0, 540, 0.33, '2025-01-07 19:55:00'),
(7, 7, 'login', '10.0.6.32', 'MacBook-Air-MKT02', 'Remote', 0, 0, 1, 420, 0.28, '2025-01-07 19:42:00'),
(8, 8, 'failed_login', '10.0.1.56', 'Dell-Latitude-FIN05', 'NYC HQ', 0, 0, 3, 30, 0.60, '2025-01-07 18:05:00'),
(9, 9, 'mass_copy', '10.0.4.77', 'MacBook-Pro-PD01', 'Remote', 7340032, 85, 0, 180, 0.88, '2025-01-07 17:41:00'),
(10, 10, 'login', '10.0.7.14', 'HP-Elite-LGL01', 'NYC HQ', 0, 0, 0, 600, 0.18, '2025-01-07 16:18:00');

-- --------------------------------------------------------

--
-- Table structure for table `alerts`
--

CREATE TABLE `alerts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `alert_type` enum('suspicious_login','failed_login','privilege_escalation','data_exfiltration','unauthorized_access','large_file_upload','suspicious_file_type','multiple_failed_attempts','after_hours_activity','geolocation_anomaly','file_upload_alert','security_scan_alert') DEFAULT NULL,
  `description` text NOT NULL,
  `risk_score` decimal(5,2) NOT NULL,
  `risk_level` enum('low','medium','high','critical') NOT NULL,
  `status` enum('open','investigating','resolved') NOT NULL DEFAULT 'open',
  `metadata_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metadata_json`)),
  `resolution_note` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `resolved_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `alerts`
--

INSERT INTO `alerts` (`id`, `user_id`, `alert_type`, `description`, `risk_score`, `risk_level`, `status`, `metadata_json`, `resolution_note`, `created_at`, `resolved_at`) VALUES
(1, 5, '', 'Unscheduled admin role granted to Mila Robbins', 0.92, 'critical', 'open', '{\"source\":\"IAM\",\"severity\":\"critical\"}', NULL, '2025-01-07 21:04:00', NULL),
(2, 9, '', 'Bailey King copied 85 files totalling 7MB', 0.88, 'high', 'investigating', '{\"files\":85}', NULL, '2025-01-07 17:42:00', NULL),
(3, 2, '', 'Jordan Doe uploaded 8 files outside business hours', 0.67, 'medium', 'open', '{\"time_window\":\"after_hours\"}', NULL, '2025-01-07 20:10:00', NULL),
(4, 3, '', 'Sloan Smith connected from Los Angeles after NYC login', 0.58, 'medium', 'resolved', '{\"locations\":[\"NYC\",\"LA\"]}', 'Validated travel itinerary', '2025-01-06 10:10:00', '2025-01-06 18:05:00'),
(5, 8, '', 'Lena Garcia had three consecutive failed attempts', 0.75, 'high', 'open', '{\"attempts\":3}', NULL, '2025-01-07 18:06:00', NULL),
(6, 4, '', 'Kai Wong downloaded 5MB of prototype data', 0.70, 'high', 'open', '{\"bytes\":5242880}', NULL, '2025-01-07 22:12:00', NULL),
(7, 10, '', 'Carmen Ibarra logged in at 4AM local time', 0.55, 'medium', 'resolved', '{\"hour\":4}', 'Confirmed legitimate due to case deadline', '2025-01-05 04:20:00', '2025-01-05 12:30:00'),
(8, 6, '', 'Dev Patel flagged suspicious lateral movement', 0.62, 'medium', 'open', '{\"module\":\"SOC-Agent\"}', NULL, '2025-01-07 20:16:00', NULL),
(9, 7, '', 'Riley Taylor connected from IP flagged by threat intel', 0.81, 'high', 'open', '{\"ip\":\"203.0.113.88\"}', NULL, '2025-01-07 19:45:00', NULL),
(10, 3, '', 'Sloan Smith accessed 30 confidential files', 0.84, 'high', 'investigating', '{\"files\":30}', NULL, '2025-01-06 22:11:00', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `audit_logs`
--

CREATE TABLE `audit_logs` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `event_type` varchar(120) NOT NULL,
  `message` text NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `audit_logs`
--

INSERT INTO `audit_logs` (`id`, `user_id`, `event_type`, `message`, `created_at`) VALUES
(1, 1, 'login_success', 'Admin console accessed by Aiden Hunt', '2025-01-08 09:12:00'),
(2, 2, 'login_success', 'Jordan Doe authenticated via SSO', '2025-01-08 07:45:05'),
(3, 3, 'password_reset', 'Password reset requested for Sloan Smith', '2025-01-07 21:00:00'),
(4, 4, 'file_download', 'Prototype schematics downloaded by Kai Wong', '2025-01-07 22:10:30'),
(5, 5, 'privilege_change', 'Temporary admin role granted to Mila Robbins', '2025-01-07 21:04:30'),
(6, 6, 'alert_triage', 'Analyst Dev Patel triaged alert #42', '2025-01-07 20:20:00'),
(7, 7, 'login_failed', 'Failed login attempt for Riley Taylor', '2025-01-07 19:41:00'),
(8, 8, '', 'Global configuration export generated', '2025-01-07 18:06:30'),
(9, 9, 'policy_ack', 'Bailey King acknowledged updated data policy', '2025-01-06 09:30:00'),
(10, 10, 'login_success', 'Legal portal accessed by Carmen Ibarra', '2025-01-05 04:20:05'),
(11, NULL, 'login_failed', 'Failed login attempt for username admin', '2025-10-27 01:00:19'),
(12, NULL, 'login_failed', 'Failed login attempt for username admin', '2025-10-27 01:11:08'),
(13, NULL, 'login_failed', 'Failed login attempt for username admin', '2025-10-27 01:11:21'),
(14, NULL, 'login_failed', 'Failed login attempt for username admin', '2025-10-27 01:12:29'),
(15, NULL, 'login_failed', 'Failed login attempt for username admin', '2025-10-27 01:12:45'),
(16, NULL, 'login_failed', 'Failed login attempt for username admin', '2025-10-27 01:12:58'),
(17, NULL, 'login_failed', 'Failed login attempt for username admin', '2025-10-27 01:13:01'),
(18, 1, 'login_success', 'User admin logged in successfully', '2025-10-27 01:19:59'),
(19, NULL, 'login_failed', 'Failed login attempt for username admin', '2025-10-27 02:01:00'),
(20, 1, 'login_success', 'User admin logged in successfully', '2025-10-27 02:01:05'),
(21, 1, 'login_success', 'User admin logged in successfully', '2025-10-28 00:48:34'),
(22, 1, 'login_success', 'User admin logged in successfully', '2025-10-28 01:17:23'),
(23, 1, 'login_success', 'User admin logged in successfully', '2025-10-28 04:58:59'),
(24, 6, 'login_success', 'User dpatel logged in successfully', '2025-10-28 05:22:45'),
(25, 1, 'login_success', 'User admin logged in successfully', '2025-10-28 05:58:29'),
(26, 1, 'login_success', 'User admin logged in successfully', '2025-10-28 07:12:27'),
(27, 2, 'login_success', 'User Noura logged in successfully', '2025-10-28 07:26:26'),
(28, 1, 'login_success', 'User admin logged in successfully', '2025-10-28 07:48:42'),
(29, NULL, 'login_failed', 'Failed login attempt for username Norah', '2025-10-28 07:49:20'),
(30, 2, 'login_success', 'User noura logged in successfully', '2025-10-28 07:49:34'),
(31, 1, 'login_success', 'User admin logged in successfully', '2025-10-28 23:15:31'),
(32, NULL, 'login_failed', 'Failed login attempt for username dpatel', '2025-10-28 23:46:25'),
(33, NULL, 'login_failed', 'Failed login attempt for username dpatel', '2025-10-28 23:46:31'),
(34, NULL, 'login_failed', 'Failed login attempt for username NOHA', '2025-10-28 23:46:46'),
(35, 2, 'login_success', 'User nOURA logged in successfully', '2025-10-28 23:47:05'),
(36, 1, 'login_success', 'User admin logged in successfully', '2025-10-29 01:42:23'),
(37, NULL, 'login_failed', 'Failed login attempt for username admin4', '2025-10-29 02:06:53'),
(38, 1, 'login_success', 'User admin logged in successfully', '2025-10-29 02:07:15'),
(39, 2, 'login_success', 'User Noura logged in successfully', '2025-10-29 02:12:17');

-- --------------------------------------------------------

--
-- Table structure for table `files`
--

CREATE TABLE `files` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `action` enum('upload','download','delete','share') NOT NULL,
  `checksum` varchar(128) DEFAULT NULL,
  `size_kb` int(11) DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `files`
--

INSERT INTO `files` (`id`, `user_id`, `file_name`, `action`, `checksum`, `size_kb`, `created_at`) VALUES
(1, 4, 'prototype-drawings.pdf', 'download', 'ab4e5d8901234cd56ef7890ab1234567', 5024, '2025-01-07 22:11:00'),
(2, 2, 'q4-financials.xlsx', 'upload', 'bc5f6a9012345de67fa8901bc2345678', 812, '2025-01-07 19:55:00'),
(3, 3, 'employee-roster.csv', 'download', 'cd6g7b0123456ef78ab9012cd3456789', 245, '2025-01-07 18:45:00'),
(4, 5, 'network-map.vsdx', 'share', 'de7h8c1234567fg89bc0123de4567890', 1420, '2025-01-07 21:05:00'),
(5, 6, 'threat-intel-report.pdf', 'upload', 'ef8i9d2345678gh90cd1234ef5678901', 960, '2025-01-07 20:17:00'),
(6, 7, 'campaign-plan.docx', 'download', 'f09j0e3456789hi01de2345f06789012', 512, '2025-01-07 19:43:00'),
(7, 8, 'ledger-export.csv', 'upload', '012k1f4567890ij12ef3456017890123', 389, '2025-01-07 18:07:00'),
(8, 9, 'design-assets.zip', 'download', '123l2g5678901jk23fg4567128901234', 7320, '2025-01-07 17:43:00'),
(9, 10, 'merger-contract.docx', 'share', '234m3h6789012kl34gh5678239012345', 1024, '2025-01-07 16:20:00'),
(10, 2, 'tax-documents.zip', 'delete', '345n4i7890123lm45hi6789340123456', 2048, '2025-01-06 08:55:00');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(120) NOT NULL,
  `message` text NOT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `title`, `message`, `is_read`, `created_at`) VALUES
(1, 1, 'New Alert Assigned', 'Critical privilege escalation alert requires review.', 0, '2025-01-07 21:05:00'),
(2, 2, 'File Upload Complete', 'Your upload of q4-financials.xlsx finished successfully.', 1, '2025-01-07 19:56:00'),
(3, 3, 'Password Reset', 'Your password reset was processed.', 1, '2025-01-07 21:01:00'),
(4, 4, 'Security Notice', 'Large prototype download flagged for review.', 0, '2025-01-07 22:12:00'),
(5, 5, 'Role Change', 'You temporarily hold elevated privileges.', 0, '2025-01-07 21:06:00'),
(6, 6, 'Alert Queue Update', 'Two new alerts waiting in the escalation queue.', 0, '2025-01-07 20:18:00'),
(7, 7, 'Failed Login Attempt', 'We noticed a failed login on your account.', 1, '2025-01-07 19:44:00'),
(8, 8, 'Finance Policy Update', 'Review the new quarterly compliance checklist.', 0, '2025-01-07 18:08:00'),
(9, 9, 'Design Delivery Reminder', 'Prototype assets shared with vendor partners.', 1, '2025-01-07 17:44:00'),
(10, 10, 'Legal Deadline', 'Upcoming contract delivery due tomorrow morning.', 0, '2025-01-07 16:21:00');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(120) NOT NULL,
  `role` enum('admin','user','analyst') NOT NULL DEFAULT 'user',
  `department` varchar(80) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `last_login` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password_hash`, `full_name`, `role`, `department`, `is_active`, `last_login`, `created_at`) VALUES
(1, 'admin', '$2b$12$/ayeFZA1EaobCKDfHC/c0OY/QO8l.MedSeHxHpwxV63Jseq7lqnj6', 'admin', 'admin', 'Security Operations', 1, '2025-10-29 02:07:15', '2024-11-01 08:00:00'),
(2, 'Noura', '$2b$12$/ayeFZA1EaobCKDfHC/c0OY/QO8l.MedSeHxHpwxV63Jseq7lqnj6', 'Noura Abdullah', 'user', 'Finance', 1, '2025-10-29 02:12:17', '2024-11-02 09:15:00'),
(3, 'Milaf', '$2b$12$/ayeFZA1EaobCKDfHC/c0OY/QO8l.MedSeHxHpwxV63Jseq7lqnj6', 'Milaf Bandar', 'user', 'HR', 1, '2025-01-08 06:30:00', '2024-11-05 13:20:00'),
(4, 'alqahtani', '$2b$12$/ayeFZA1EaobCKDfHC/c0OY/QO8l.MedSeHxHpwxV63Jseq7lqnj6', 'alqahtani', 'user', 'R&D', 1, '2025-01-07 22:10:00', '2024-11-07 11:45:00'),
(5, 'fahad', '$2b$12$/ayeFZA1EaobCKDfHC/c0OY/QO8l.MedSeHxHpwxV63Jseq7lqnj6', 'Fahad Alharbi', 'user', 'Information Technology', 1, '2025-01-07 21:03:00', '2024-11-08 10:00:00'),
(6, 'saad', '$2b$12$/ayeFZA1EaobCKDfHC/c0OY/QO8l.MedSeHxHpwxV63Jseq7lqnj6', 'Saad Almutairi', 'analyst', 'Security Operations', 1, '2025-10-28 05:22:45', '2024-11-09 09:05:00'),
(7, 'reem', '$2b$12$/ayeFZA1EaobCKDfHC/c0OY/QO8l.MedSeHxHpwxV63Jseq7lqnj6', 'Reem Alotaibi', 'user', 'Marketing', 1, '2025-01-07 19:42:00', '2024-11-10 14:25:00'),
(8, 'huda', '$2b$12$/ayeFZA1EaobCKDfHC/c0OY/QO8l.MedSeHxHpwxV63Jseq7lqnj6', 'Huda Alzahrani', 'user', 'Finance', 1, '2025-01-07 18:05:00', '2024-11-11 08:55:00'),
(9, 'nasser', '$2b$12$/ayeFZA1EaobCKDfHC/c0OY/QO8l.MedSeHxHpwxV63Jseq7lqnj6', 'Nasser Alshammari', 'user', 'Product Management', 1, '2025-01-07 17:41:00', '2024-11-12 09:32:00'),
(10, 'maha', '$2b$12$/ayeFZA1EaobCKDfHC/c0OY/QO8l.MedSeHxHpwxV63Jseq7lqnj6', 'Maha Alshehri', 'user', 'Legal Affairs', 1, '2025-01-07 16:18:00', '2024-11-12 11:08:00');

-- --------------------------------------------------------

--
-- Table structure for table `user_files`
--

CREATE TABLE `user_files` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_size` bigint(20) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `risk_level` enum('low','medium','high','critical') DEFAULT 'low',
  `uploaded_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `scanned_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `activity_logs`
--
ALTER TABLE `activity_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `alerts`
--
ALTER TABLE `alerts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `files`
--
ALTER TABLE `files`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `user_files`
--
ALTER TABLE `user_files`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_uploaded_at` (`uploaded_at`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `activity_logs`
--
ALTER TABLE `activity_logs`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `alerts`
--
ALTER TABLE `alerts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `audit_logs`
--
ALTER TABLE `audit_logs`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT for table `files`
--
ALTER TABLE `files`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `user_files`
--
ALTER TABLE `user_files`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `activity_logs`
--
ALTER TABLE `activity_logs`
  ADD CONSTRAINT `activity_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `alerts`
--
ALTER TABLE `alerts`
  ADD CONSTRAINT `alerts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `files`
--
ALTER TABLE `files`
  ADD CONSTRAINT `files_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_files`
--
ALTER TABLE `user_files`
  ADD CONSTRAINT `user_files_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
