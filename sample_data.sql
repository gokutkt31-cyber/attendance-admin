-- Sample Data Insertions for Employee Attendance Management System
-- Passwords: admin -> admin123, hr_user -> hr123, emp_user -> emp123 (Bcrypt hashes below)

USE `attendance_db`;

-- 1. Insert System Settings
INSERT INTO `settings` (`key`, `value`, `description`) VALUES
('check_in_start_time', '09:00:00', 'Daily shift start time limit'),
('check_in_grace_period_mins', '15', 'Allowed delay grace minutes'),
('allowed_gps_latitude', '12.9716', 'Default company office latitude location boundary'),
('allowed_gps_longitude', '77.5946', 'Default company office longitude location boundary'),
('allowed_gps_radius_meters', '200.0', 'Maximum boundary distance check limit')
ON DUPLICATE KEY UPDATE `value`=VALUES(`value`);

-- 2. Insert Departments
INSERT INTO `departments` (`id`, `name`, `code`, `description`) VALUES
(1, 'Engineering', 'ENG', 'Product development, software engineering, QA'),
(2, 'Human Resources', 'HR', 'Employee relations, recruitment, benefits'),
(3, 'Sales & Marketing', 'SAL', 'Client relationships, marketing campaigns')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- 3. Insert Users
-- Password hashes generated with Flask-Bcrypt
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `is_active`) VALUES
(1, 'admin', 'admin@ams.com', '$2b$12$t4jG04T3jMizb8x21aO0IumS7y22q/QW9mC81G794aH3z1.Vz8KSm', 'admin', 1), -- pwd: admin123
(2, 'hr_user', 'hr@ams.com', '$2b$12$Z0P620a21sE72k8sQ31jNuoO0a21t8S8dG794aH3z1.Vz8KSmS72a', 'hr', 1),     -- pwd: hr123
(3, 'emp_user', 'employee@ams.com', '$2b$12$K3sQ12a45dF89gH01jK23uuS7y22q/QW9mC81G794aH3z1.Vz8KSm', 'employee', 1) -- pwd: emp123
ON DUPLICATE KEY UPDATE `username`=VALUES(`username`);

-- 4. Insert Employees Profiles
INSERT INTO `employees` (`id`, `user_id`, `employee_id`, `first_name`, `last_name`, `email`, `phone`, `department_id`, `designation`, `date_of_joining`, `location_lat`, `location_lng`) VALUES
(1, 2, 'EMP-2026-0001', 'Sarah', 'Jenkins', 'hr@ams.com', '+1234567890', 2, 'HR Manager', '2026-01-10', 12.9716, 77.5946),
(2, 3, 'EMP-2026-0002', 'John', 'Doe', 'employee@ams.com', '+1987654321', 1, 'Software Engineer', '2026-02-15', 12.9716, 77.5946)
ON DUPLICATE KEY UPDATE `employee_id`=VALUES(`employee_id`);

-- 5. Insert Sample Attendance Logs
INSERT INTO `attendance` (`employee_id`, `date`, `check_in_time`, `check_out_time`, `check_in_lat`, `check_in_lng`, `working_hours`, `overtime`, `status`, `late_entry`) VALUES
(2, DATE_SUB(CURDATE(), INTERVAL 2 DAY), '08:50:00', '17:05:00', 12.9716, 77.5946, 8.25, 0.25, 'Present', 0),
(2, DATE_SUB(CURDATE(), INTERVAL 1 DAY), '09:20:00', '17:00:00', 12.9716, 77.5946, 7.66, 0.00, 'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 1 DAY), '08:55:00', '17:00:00', 12.9716, 77.5946, 8.08, 0.08, 'Present', 0)
ON DUPLICATE KEY UPDATE `employee_id`=VALUES(`employee_id`);
