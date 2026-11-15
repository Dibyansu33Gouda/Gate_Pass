-- GatePass Seed Data
-- Generated with Argon2 hashes via pwdlib
USE gatepass_db;

-- Clear tables in reverse dependency order (safe re-seeding)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE deliveries;
TRUNCATE TABLE visits;
TRUNCATE TABLE users;
TRUNCATE TABLE delivery_agents;
TRUNCATE TABLE security_staff;
TRUNCATE TABLE visitors;
TRUNCATE TABLE residents;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Residents (8 residents across 5 flats: Flat A-101, A-102, B-201, B-202, C-301)
-- Resident 8 (Vikram Malhotra) intentionally has ZERO deliveries for LEFT JOIN demo.
INSERT INTO residents (resident_id, name, flat_no, phone, email, is_active) VALUES
(1, 'Aarav Sharma',     'A-101', '9811001101', 'aarav.sharma@example.com',     TRUE),
(2, 'Priya Verma',      'A-102', '9811001102', 'priya.verma@example.com',      TRUE),
(3, 'Rohan Gupta',      'B-201', '9811001103', 'rohan.gupta@example.com',      TRUE),
(4, 'Sneha Patel',      'B-202', '9811001104', 'sneha.patel@example.com',      TRUE),
(5, 'Amitabh Joshi',    'C-301', '9811001105', 'amitabh.joshi@example.com',    TRUE),
(6, 'Deepika Rao',      'A-101', '9811001106', 'deepika.rao@example.com',      TRUE),
(7, 'Karan Kapoor',     'B-201', '9811001107', 'karan.kapoor@example.com',     TRUE),
(8, 'Vikram Malhotra',  'C-301', '9811001108', 'vikram.malhotra@example.com',  TRUE);

-- 2. Security Staff (3 staff members, one per shift)
INSERT INTO security_staff (staff_id, staff_name, phone, shift, is_active) VALUES
(1, 'Ramesh Kumar',  '9911002201', 'Morning', TRUE),
(2, 'Suresh Yadav',  '9911002202', 'Evening', TRUE),
(3, 'Mahesh Singh',  '9911002203', 'Night',   TRUE);

-- 3. Delivery Agents (5 agents from different courier companies)
INSERT INTO delivery_agents (agent_id, agent_name, phone, courier_company) VALUES
(1, 'Rajesh Das',     '9711003301', 'Amazon Logistics'),
(2, 'Sunil Khan',     '9711003302', 'Flipkart Quick'),
(3, 'Manish Tiwari',  '9711003303', 'Zomato'),
(4, 'Imran Ali',      '9711003304', 'Swiggy Instamart'),
(5, 'Pankaj Mishra',  '9711003305', 'BlueDart');

-- 4. Users (1 admin, 3 guards, 2 residents linked to residents 1 & 2)
INSERT INTO users (user_id, username, password_hash, role, staff_id, resident_id) VALUES
(1, 'admin',        '$argon2id$v=19$m=65536,t=3,p=4$kAsZqnjOpBhUrwJDaMZTEA$rSQmxGUeq71Ggm3Kp3hcwLyW7ECGjSbyCshJsU4YpM4',  'admin',    NULL, NULL),
(2, 'guard_ramesh', '$argon2id$v=19$m=65536,t=3,p=4$q+/qiSYcbXd3sM4EQkvvxw$FNedOfkwxyADttrheUTtE9I1O+2wZ2KGx4I0Bq+bZV0', 'security', 1,    NULL),
(3, 'guard_suresh', '$argon2id$v=19$m=65536,t=3,p=4$dOp4R0Gn3kJZLiZ5k0dhtg$Vxveg9p+FLY9mp/lwUXHOqcyfa8JqSpycijMF5RH1L8', 'security', 2,    NULL),
(4, 'guard_mahesh', '$argon2id$v=19$m=65536,t=3,p=4$vPvrnRSzcoEwm6GT5mb5Yg$Y4dU9m5oQY3iA8eg1tZZqANj6PXEwc+m1Lc0+B3jZ1U', 'security', 3,    NULL),
(5, 'resident_aarav','$argon2id$v=19$m=65536,t=3,p=4$DOgM6evOgHXQ048TfiDhJw$ucSndqIQBZplN/3CXACxyEIeATstafE400NJp0byPqU',  'resident', NULL, 1),
(6, 'resident_priya','$argon2id$v=19$m=65536,t=3,p=4$KMzrs3nerp9U/jI69YqIDA$6BFPWyNuBhIgkdsq7u+hCPieK5J1+pUTy5OJnT0rndw',  'resident', NULL, 2);

`-- 5. Visitors (12 visitors with unique phone numbers)
INSERT INTO visitors (visitor_id, visitor_name, phone, is_active) VALUES
(1,  'Kavita Nair',      '9611004401', TRUE),
(2,  'Gaurav Mehta',     '9611004402', TRUE),
(3,  'Neha Saxena',      '9611004403', TRUE),
(4,  'Harish Choudhary', '9611004404', TRUE),
(5,  'Pooja Bhatia',     '9611004405', TRUE),
(6,  'Arjun Sen',        '9611004406', TRUE),
(7,  'Simran Kaur',      '9611004407', TRUE),
(8,  'Varun Aggarwal',   '9611004408', TRUE),
(9,  'Meera Menon',      '9611004409', TRUE),
(10, 'Nitin Deshmukh',   '9611004410', TRUE),
(11, 'Ananya Sengupta',  '9611004411', TRUE),
(12, 'Devendra Shukla',  '9611004412', TRUE);

-- 6. Visits (25 visits spread across past 7 days up to today)
-- Demonstrating: Pending, Approved (some entered, 3 currently inside, some exited), Rejected, Cancelled.
INSERT INTO visits (visit_id, visitor_id, resident_id, staff_id, purpose, visit_date, approval_status, gate_pass_no, entry_time, exit_time) VALUES
-- Past Completed Visits (Approved -> Entered -> Exited)
(1,  1,  1, 1, 'Family Visit',       DATE_SUB(CURRENT_DATE, INTERVAL 6 DAY), 'Approved',  'GP-20261107-0001', DATE_SUB(NOW(), INTERVAL 140 HOUR), DATE_SUB(NOW(), INTERVAL 137 HOUR)),
(2,  2,  2, 2, 'Plumbing Repair',    DATE_SUB(CURRENT_DATE, INTERVAL 6 DAY), 'Approved',  'GP-20261107-0002', DATE_SUB(NOW(), INTERVAL 139 HOUR), DATE_SUB(NOW(), INTERVAL 136 HOUR)),
(3,  3,  3, 3, 'Friend Meetup',      DATE_SUB(CURRENT_DATE, INTERVAL 5 DAY), 'Approved',  'GP-20261108-0003', DATE_SUB(NOW(), INTERVAL 115 HOUR), DATE_SUB(NOW(), INTERVAL 112 HOUR)),
(4,  4,  4, 1, 'Carpentry Work',     DATE_SUB(CURRENT_DATE, INTERVAL 5 DAY), 'Approved',  'GP-20261108-0004', DATE_SUB(NOW(), INTERVAL 114 HOUR), DATE_SUB(NOW(), INTERVAL 110 HOUR)),
(5,  5,  5, 2, 'Document Signing',   DATE_SUB(CURRENT_DATE, INTERVAL 4 DAY), 'Approved',  'GP-20261109-0005', DATE_SUB(NOW(), INTERVAL 90 HOUR),  DATE_SUB(NOW(), INTERVAL 88 HOUR)),
(6,  6,  6, 3, 'Tutor Classes',      DATE_SUB(CURRENT_DATE, INTERVAL 4 DAY), 'Approved',  'GP-20261109-0006', DATE_SUB(NOW(), INTERVAL 89 HOUR),  DATE_SUB(NOW(), INTERVAL 87 HOUR)),
(7,  7,  7, 1, 'Interior Inspection',DATE_SUB(CURRENT_DATE, INTERVAL 3 DAY), 'Approved',  'GP-20261110-0007', DATE_SUB(NOW(), INTERVAL 66 HOUR),  DATE_SUB(NOW(), INTERVAL 64 HOUR)),
(8,  8,  1, 2, 'Guest Visit',        DATE_SUB(CURRENT_DATE, INTERVAL 3 DAY), 'Approved',  'GP-20261110-0008', DATE_SUB(NOW(), INTERVAL 65 HOUR),  DATE_SUB(NOW(), INTERVAL 62 HOUR)),
(9,  9,  2, 3, 'Birthday Invitation',DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), 'Approved',  'GP-20261111-0009', DATE_SUB(NOW(), INTERVAL 42 HOUR),  DATE_SUB(NOW(), INTERVAL 40 HOUR)),
(10, 10, 3, 1, 'AC Servicing',       DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), 'Approved',  'GP-20261111-0010', DATE_SUB(NOW(), INTERVAL 41 HOUR),  DATE_SUB(NOW(), INTERVAL 39 HOUR)),

-- Rejected and Cancelled visits
(11, 11, 4, 2, 'Unsolicited Sales',  DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), 'Rejected',   NULL,               NULL, NULL),
(12, 12, 5, 3, 'Unknown Person',     DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), 'Rejected',   NULL,               NULL, NULL),
(13, 1,  2, 1, 'Cancelled by Guest', DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), 'Cancelled',  NULL,               NULL, NULL),

-- Recent Approved Visits
(14, 2,  3, 2, 'Electrical Check',   DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), 'Approved',  'GP-20261112-0014', DATE_SUB(NOW(), INTERVAL 18 HOUR),  DATE_SUB(NOW(), INTERVAL 16 HOUR)),
(15, 3,  1, 3, 'Personal Visit',     DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), 'Approved',  'GP-20261112-0015', DATE_SUB(NOW(), INTERVAL 17 HOUR),  DATE_SUB(NOW(), INTERVAL 15 HOUR)),

-- 3 Visits CURRENTLY INSIDE (entry_time set, exit_time IS NULL)
(16, 4,  1, 1, 'Painting Consultation',CURRENT_DATE,                         'Approved',  'GP-20261113-0016', DATE_SUB(NOW(), INTERVAL 2 HOUR),   NULL),
(17, 5,  2, 1, 'Study Group',          CURRENT_DATE,                         'Approved',  'GP-20261113-0017', DATE_SUB(NOW(), INTERVAL 1 HOUR),   NULL),
(18, 6,  3, 2, 'Appliance Repair',     CURRENT_DATE,                         'Approved',  'GP-20261113-0018', DATE_SUB(NOW(), INTERVAL 30 MINUTE),NULL),

-- Approved Visits Waiting at Gate (entry_time NULL)
(19, 7,  1, 1, 'Friend Visit',         CURRENT_DATE,                         'Approved',  'GP-20261113-0019', NULL, NULL),
(20, 8,  2, 2, 'Courier Delivery Check',CURRENT_DATE,                        'Approved',  'GP-20261113-0020', NULL, NULL),

-- Pending Approval Visits (Ready for resident approval demo)
(21, 9,  1, 1, 'Client Discussion',    CURRENT_DATE,                         'Pending',   NULL,               NULL, NULL),
(22, 10, 2, 2, 'Housemaid Interview',  CURRENT_DATE,                         'Pending',   NULL,               NULL, NULL),
(23, 11, 3, 3, 'Package Verification', CURRENT_DATE,                         'Pending',   NULL,               NULL, NULL),
(24, 12, 4, 1, 'Internet Installation',CURRENT_DATE,                         'Pending',   NULL,               NULL, NULL),
(25, 1,  5, 2, 'Casual Meet',          CURRENT_DATE,                         'Pending',   NULL,               NULL, NULL);

-- 7. Deliveries (10 deliveries across Arrived, Received, Returned)
-- Resident 8 has 0 deliveries on purpose for LEFT JOIN demonstration
INSERT INTO deliveries (delivery_id, resident_id, staff_id, agent_id, delivery_type, status, arrived_at, received_at) VALUES
(1,  1, 1, 1, 'Courier', 'Received', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY) + INTERVAL 2 HOUR),
(2,  1, 2, 3, 'Food',    'Received', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY) + INTERVAL 30 MINUTE),
(3,  2, 3, 2, 'Courier', 'Received', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY) + INTERVAL 4 HOUR),
(4,  3, 1, 4, 'Food',    'Received', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY) + INTERVAL 45 MINUTE),
(5,  4, 2, 5, 'Courier', 'Received', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY) + INTERVAL 3 HOUR),
(6,  5, 3, 1, 'Other',   'Returned', DATE_SUB(NOW(), INTERVAL 1 DAY), NULL),
(7,  6, 1, 3, 'Food',    'Returned', DATE_SUB(NOW(), INTERVAL 1 DAY), NULL),
(8,  1, 2, 4, 'Food',    'Arrived',  DATE_SUB(NOW(), INTERVAL 2 HOUR), NULL),
(9,  2, 1, 2, 'Courier', 'Arrived',  DATE_SUB(NOW(), INTERVAL 1 HOUR), NULL),
(10, 7, 3, 5, 'Courier', 'Arrived',  DATE_SUB(NOW(), INTERVAL 15 MINUTE), NULL);
