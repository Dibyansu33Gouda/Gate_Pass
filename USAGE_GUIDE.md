# GatePass: Complete End-to-End User Guide 🛡️
### How to Use Every Feature From Start to Finish

This guide walks you through every single feature of the **GatePass** system step-by-step.

---

## 🚀 Step 0: Starting the Server

1. Open your terminal or PowerShell in `D:\DBMS Project`.
2. Run this command:
   ```powershell
   uvicorn app.main:app --reload
   ```
3. Open your browser and navigate to:
   👉 **`http://127.0.0.1:8000`**

---

## 🔑 Demo Accounts Reference

| Role | Username | Password | Purpose |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Society management, resident/staff CRUD, telemetry & SQL analytics |
| **Security Guard** | `guard_ramesh` | `guard123` | Visitor registration, gate entry/exit control, parcel deliveries |
| **Resident 1** | `resident_aarav` | `resident123` | Flat A-101 portal: approve/reject visitor passes, view gate passes |
| **Resident 2** | `resident_priya` | `resident123` | Flat A-102 portal |

---

## 🛡️ WORKFLOW 1: Security Guard Operations

### Feature 1.1: Register a New Visitor (ACID Transaction)
1. Log in with:
   - **Username:** `guard_ramesh`
   - **Password:** `guard123`
2. You will land on the **Gate Operations** page. In the top right corner, click **`+ Register Visitor`** (or click **+ Register Visitor** in the navigation bar).
3. Fill out the form:
   - **Visitor Full Name:** `Rohan Verma`
   - **Visitor Phone:** `9876543210` (must be 10 digits)
   - **Meeting Resident / Flat:** Select `A-101 — Aarav Sharma`
   - **Purpose of Visit:** `Project Discussion`
4. Click **Submit Visitor Request**.
5. **What happens in the database:**
   - Starts a transaction: `conn.start_transaction()`.
   - Checks if phone `9876543210` already exists in `visitors`. If not, inserts a new row; if yes, reuses the existing `visitor_id`.
   - Inserts a new record into `visits` with status **`Pending`**.
   - Commits the transaction: `conn.commit()`.

---

### Feature 1.2: Gate Entry & Exit Management
1. In the navigation bar, click **Gate Ops (Entry/Exit)** (`/gate`).
2. You will see two sections:
   - **🔵 Approved Visits Awaiting Gate Arrival:** Visitors approved by residents who have not arrived at the gate yet.
   - **🟢 Visitors Currently Inside Society (Live Inside List):** Visitors currently on society premises.
3. Once a resident approves a visitor (see Workflow 2 below), click the green **`➔ Record Entry`** button next to their name.
   - *Database update:* Sets `entry_time = NOW()` for that visit. The visitor moves to the **Inside Society** table.
4. When the visitor is leaving the society, click the red **`Log Exit ➔`** button.
   - *Database update:* Sets `exit_time = NOW()`.
   - The MySQL `CONSTRAINT chk_times CHECK (exit_time >= entry_time)` constraint validates that departure cannot occur before arrival.
   - The visitor departs and is removed from the inside list.

---

### Feature 1.3: Visitor Directory & Search
1. In the navigation bar, click **Visitor Directory** (`/visitors`).
2. **Search:** In the search bar, type a visitor's name (e.g., `Kavita`) or phone number and click **Search**.
   - *Database concept:* Demonstrates indexed query filtering.
3. **Deactivate / Soft Delete:** Click the red **Deactivate** button next to any visitor.
   - *Database concept:* Demonstrates soft deletion via `is_active = FALSE`. The visitor's past visit history remains intact for audit compliance.

---

### Feature 1.4: Courier & Package Deliveries
1. In the navigation bar, click **Deliveries** (`/deliveries`).
2. **Register a Delivery Agent:**
   - On the right panel (**Register Delivery Agent**), enter:
     - **Agent Full Name:** `Deepak Singh`
     - **Phone:** `9711005544`
     - **Courier / Service Provider:** `Zomato`
   - Click **+ Register Agent**.
3. **Log an Incoming Delivery:**
   - On the left panel (**Log Incoming Delivery**):
     - **Recipient Resident:** Select `A-101 — Aarav Sharma`
     - **Delivery Agent:** Select `Zomato — Deepak Singh`
     - **Package Category:** Choose `Food`
   - Click **+ Log Arrival**.
   - *Database update:* Inserts into `deliveries` with `status = 'Arrived'` and current timestamp.
4. **Mark Delivery Received:**
   - Under the Delivery Registry table, find the delivery and click **`✓ Received`**.
   - *Database update:* Executes:
     `UPDATE deliveries SET status = 'Received', received_at = NOW() WHERE delivery_id = %s;`

---

### Feature 1.5: Historical Audit Log (`v_visit_history`)
1. Click **Visit History** (`/history`).
2. This page queries the MySQL database **VIEW** `v_visit_history`.
3. Filter by **Date**, **Resident**, or **Approval Status**, and click **Apply Filter**.

---

## 🏡 WORKFLOW 2: Resident Portal

### Feature 2.1: View Pending Visitor Requests
1. Open an incognito browser window (or log out).
2. Log in with:
   - **Username:** `resident_aarav`
   - **Password:** `resident123`
3. You will automatically land on the **Resident Portal** (`/approvals`).
4. Notice your profile information at the top: **Flat A-101 — Aarav Sharma**.
   - *Security Note:* Resident routes always scope queries to the logged-in session `resident_id` to block unauthorized ID tampering.

---

### Feature 2.2: Approve a Visitor and Issue a Gate Pass
1. Under **⚠️ Pending Visitor Requests**, look for the visitor registered in Feature 1.1 (`Rohan Verma`).
2. Click the green button: **`✓ Approve (Issue Pass)`**.
3. **What happens in the database:**
   - Executes atomic SQL update with status guard:
     ```sql
     UPDATE visits
     SET approval_status = 'Approved',
         gate_pass_no = CONCAT('GP-', DATE_FORMAT(NOW(), '%Y%m%d'), '-', LPAD(visit_id, 4, '0'))
     WHERE visit_id = %s AND resident_id = %s AND approval_status = 'Pending';
     ```
   - Generates a unique Gate Pass code (e.g., `GP-20261113-0026`).
4. The visit moves into **My Recent Visit History & Gate Passes** with status badge `Approved`.

---

### Feature 2.3: Reject a Visitor
1. For any unwanted visitor request, click the red **`✕ Reject`** button.
2. The visit status is updated to `Rejected`, barring the gate guard from recording an entry.

---

## 👑 WORKFLOW 3: Admin Operations & DBMS Reports

Log in with:
- **Username:** `admin`
- **Password:** `admin123`

---

### Feature 3.1: Admin Dashboard (`/dashboard`)
- View real-time counters:
  - **Active Residents:** Total flats enrolled.
  - **Today's Visitors:** Count of visits scheduled for `CURRENT_DATE`.
  - **Visitors Inside Society:** Live count of visitors with entry logged but exit `NULL`.
  - **Pending Approvals:** Global count of requests awaiting resident decisions.
  - **Deliveries:** Arrived vs Received statistics.
- Previews of the latest 5 visits and deliveries.

---

### Feature 3.2: Manage Residents (`/residents`)
1. In the navigation bar, click **Residents**.
2. **Add New Resident:**
   - Enter Full Name, Flat Number (e.g. `D-401`), 10-digit Phone, and Email.
   - Click **+ Add Resident**.
3. **Search Residents:** Filter residents by name or flat number.
4. **Soft Delete:** Click **Deactivate** to toggle `is_active` to `FALSE`.

---

### Feature 3.3: Manage Security Staff & Shifts (`/staff`)
1. Click **Staff**.
2. **Enroll Security Guard:** Enter Name, Phone, and assign initial shift (`Morning`, `Evening`, `Night`).
3. **Shift Reallocation:** Change a guard's shift directly using the dropdown selector in the table and click **Update**.
4. **Soft Delete:** Toggle guard active status.

---

### Feature 3.4: SQL Demonstrations & Reports (`/reports`)
Click **SQL Reports** in the navbar to review the core DBMS concepts:
1. **Nested Subquery with HAVING (Report 1):**
   - Shows residents whose total visits strictly exceed the society-wide average visits per resident.
2. **GROUP BY + COUNT (Report 2):**
   - Aggregates and ranks residents by total visitors hosted.
3. **Aggregate Functions (Report 3):**
   - Shows daily visitor traffic counts and delivery status distribution.
4. **LEFT JOIN Demonstration (Report 4):**
   - Displays all residents joined with deliveries.
   - Notice **Vikram Malhotra (Flat C-301)** has `NULL` delivery attributes, confirming outer join behavior.

---

### Feature 3.5: Interactive Backend API Docs (`/docs`)
1. In your browser URL bar, go to:
   👉 **`http://127.0.0.1:8000/docs`**
2. Interactive Swagger UI where you can inspect every route, request parameter, and response model.
