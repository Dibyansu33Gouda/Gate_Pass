-- GatePass DBMS Project - Required SQL Demonstrations (Section 7)
USE gatepass_db;

-- 1. INNER JOIN (visits + visitors + residents)
-- Concept: Combines rows where foreign keys match across 3 tables.
SELECT v.visit_id, vi.visitor_name, vi.phone AS visitor_phone,
       r.name AS resident_name, r.flat_no, v.purpose, v.approval_status
FROM visits v
INNER JOIN visitors vi ON v.visitor_id = vi.visitor_id
INNER JOIN residents r ON v.resident_id = r.resident_id
ORDER BY v.visit_id DESC;

-- 2. INNER JOIN (visits + visitors + security_staff)
-- Concept: Tracks accountability by linking visit entries to security guards.
SELECT v.visit_id, vi.visitor_name, s.staff_name AS registered_by_guard,
       s.shift AS guard_shift, v.visit_date, v.approval_status, v.gate_pass_no
FROM visits v
INNER JOIN visitors vi ON v.visitor_id = vi.visitor_id
INNER JOIN security_staff s ON v.staff_id = s.staff_id
ORDER BY v.visit_date DESC, v.visit_id DESC;

-- 3. LEFT JOIN (residents + deliveries)
-- Concept: Returns ALL residents, including those with zero deliveries (NULL demonstration).
SELECT r.resident_id, r.name AS resident_name, r.flat_no,
       d.delivery_id, d.delivery_type, d.status AS delivery_status, d.arrived_at
FROM residents r
LEFT JOIN deliveries d ON r.resident_id = d.resident_id
ORDER BY r.resident_id, d.arrived_at DESC;

-- 4. GROUP BY with COUNT
-- Concept: Groups visits by resident entity and aggregates frequency.
SELECT r.resident_id, r.name AS resident_name, r.flat_no, COUNT(v.visit_id) AS total_visits
FROM residents r
LEFT JOIN visits v ON r.resident_id = v.resident_id
GROUP BY r.resident_id, r.name, r.flat_no
ORDER BY total_visits DESC;

-- 5. Aggregate Functions (COUNT, AVG, Distribution)
-- 5a. Daily visitor volume
SELECT visit_date, COUNT(*) AS total_visitors_today
FROM visits GROUP BY visit_date ORDER BY visit_date DESC;

-- 5b. Average visits per resident
SELECT ROUND(AVG(visit_count), 2) AS avg_visits_per_resident
FROM (SELECT resident_id, COUNT(*) AS visit_count FROM visits GROUP BY resident_id) AS stats;

-- 5c. Deliveries breakdown by status
SELECT status, COUNT(*) AS total_deliveries FROM deliveries GROUP BY status;

-- 6. Correlated/Nested Subquery with HAVING
-- Concept: Finds residents whose total visit count strictly exceeds society-wide average.
SELECT r.name, r.flat_no, COUNT(*) AS total_visits
FROM residents r
JOIN visits v ON v.resident_id = r.resident_id
GROUP BY r.resident_id, r.name, r.flat_no
HAVING COUNT(*) > (
    SELECT AVG(cnt) FROM (
        SELECT COUNT(*) AS cnt FROM visits GROUP BY resident_id
    ) AS per_resident
);

-- 7. View Demonstration
-- Concept: Encapsulates 4-table join into an abstract relation.
SELECT * FROM v_visit_history WHERE approval_status = 'Approved' ORDER BY visit_date DESC;

-- 8. Index Demonstration (EXPLAIN query optimization proof)
-- 8a. Uses UNIQUE index on phone
EXPLAIN SELECT * FROM visitors WHERE phone = '9876543210';
-- 8b. Uses idx_visits_date index on visit_date
EXPLAIN SELECT * FROM visits WHERE visit_date = CURRENT_DATE;
-- 8c. Uses idx_residents_flat index on flat_no
EXPLAIN SELECT * FROM residents WHERE flat_no = 'A-101';
