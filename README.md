# GatePass 🛡️
### Smart Visitor & Delivery Management System
**Academic DBMS Project** &bull; Built with **Python (FastAPI)**, **Jinja2 Templates**, and **MySQL 8.0**

---

## 1. Project Overview

GatePass is a role-based residential society security and delivery management web application. It automates gate control, visitor verification, and delivery logging while rigorously demonstrating foundational **Database Management System (DBMS)** concepts.

### Key Workflows:
1. **Visitor Registration (ACID Transaction):** A security guard registers an incoming visitor. The database checks for returning visitors by unique phone number, reusing the visitor row or creating a new one, and creates a pending visit record in a single atomic transaction.
2. **Resident Approval & Gate Pass Generation:** The resident logs in to their private portal, views pending visitor requests for their flat, and approves or rejects them. Approval atomically issues an alphanumeric gate pass number (`GP-YYYYMMDD-XXXX`).
3. **Gate Entry & Exit Tracking:** The guard verifies the approved pass, records entry timestamp, tracks all visitors currently on premises, and records their exit timestamp with SQL `CHECK` constraint validation.
4. **Deliveries Management:** Guards log courier and food deliveries against residents. Deliveries can be marked as received or returned.
5. **Admin Telemetry & SQL Reports:** Live stats on today's visitors, active residents, pending requests, and database analytics demonstrating Joins, Aggregations, Group By, Subqueries, and Views.

---

## 2. DBMS Concepts & Where They Are Used

| DBMS Concept | Implementation in GatePass | Where to Check in Code |
|---|---|---|
| **Primary Keys & Foreign Keys** | Auto-increment primary keys on all 7 tables; referential integrity with `ON DELETE SET NULL` and `FOREIGN KEY` references. | `database/schema.sql` |
| **CHECK Constraints** | Enforces that exit time cannot occur before entry time: `CONSTRAINT chk_times CHECK (exit_time IS NULL OR (entry_time IS NOT NULL AND exit_time >= entry_time))` | `database/schema.sql` (Line 60) |
| **UNIQUE Constraints** | Prevents duplicate phone numbers in `visitors`, `residents`, `security_staff`, `delivery_agents`, and unique `gate_pass_no`. | `database/schema.sql` |
| **Indexes** | B-Tree indexes: `idx_residents_flat` on `flat_no`, `idx_visits_date` on `visit_date`, `idx_visits_status` on `approval_status`, `idx_deliveries_status`. | `database/schema.sql`, `database/queries.sql` |
| **Database Transactions (ACID)** | Multi-statement transaction with `conn.start_transaction()`, `conn.commit()`, and `conn.rollback()` when registering visitors. | `app/routers/visitors.py` |
| **Database Views** | `v_visit_history` encapsulates a 4-table join into an abstract reusable relation for history auditing. | `database/schema.sql`, `app/routers/history.py` |
| **INNER JOIN (3 & 4 Tables)** | Joins visits, visitors, residents, and staff to reconstruct visitor movement and guard accountability. | `database/queries.sql` (Queries 1 & 2) |
| **LEFT OUTER JOIN** | Shows all residents and their deliveries, including residents with 0 deliveries (e.g. Vikram Malhotra). | `database/queries.sql` (Query 3), `/reports` |
| **GROUP BY & Aggregates** | Computes visit frequencies per resident, daily visitor counts, and delivery status distributions using `COUNT`, `AVG`, `ROUND`. | `database/queries.sql` (Queries 4 & 5) |
| **Correlated Subquery with HAVING** | Selects residents whose hosted visit count is strictly greater than the society-wide average visits per resident. | `database/queries.sql` (Query 6), `/reports` |
| **SQL Injection Prevention** | 100% of queries use parameterized placeholders (`%s`). Zero string formatting or concatenation. | Across all routers in `app/routers/` |

---

## 3. Database Normalization (Viva Explanation)

- **1NF (First Normal Form):** Every table attribute is atomic (single-valued); no repeating groups or comma-separated lists.
- **2NF (Second Normal Form):** All tables have single-column primary keys (`resident_id`, `visitor_id`, etc.), so partial functional dependencies cannot exist.
- **3NF (Third Normal Form):** No transitive dependencies. Visitor details are kept in `visitors`, delivery agent company is in `delivery_agents`, and visit purpose is stored in `visits` (since purpose belongs to a specific visit, not the visitor entity).

---

## 4. Project Structure

```
DBMS Project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, static mounting, SessionMiddleware, routers
│   ├── config.py            # Reads configuration from .env
│   ├── db.py                # MySQL connection pool & context managers
│   ├── auth.py              # Argon2 password hashing (pwdlib) & require_role RBAC
│   ├── schemas.py           # Pydantic form validation (10-digit phone, clean strings)
│   ├── routers/
│   │   ├── auth.py          # /login, /logout
│   │   ├── dashboard.py     # /dashboard (Admin overview & telemetry)
│   │   ├── visitors.py      # /visitors/new (ACID transaction), /visitors directory
│   │   ├── residents.py     # /residents (CRUD, flat search, soft delete)
│   │   ├── staff.py         # /staff (CRUD, shift assignment)
│   │   ├── approvals.py     # /approvals (Resident portal, atomic approve/reject)
│   │   ├── gate.py          # /gate (Security entry/exit timestamps, inside list)
│   │   ├── deliveries.py    # /deliveries (Log delivery, agent registration)
│   │   ├── history.py       # /history (Audit log via v_visit_history view)
│   │   └── reports.py       # /reports (Subquery, Group By, Left Join reports)
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html        # Main layout, responsive navbar, role badges
│   │   ├── login.html       # Login form with evaluation credentials cheat-sheet
│   │   ├── dashboard.html   # Admin metric cards and recent tables
│   │   ├── visitors_new.html# Visitor registration transaction form
│   │   ├── visitors_list.html# Visitor directory & search
│   │   ├── residents.html   # Residents management table
│   │   ├── staff.html       # Security staff & shift roster
│   │   ├── approvals.html   # Resident pending approvals & gate pass viewer
│   │   ├── gate.html        # Main gate entry/exit control & inside list
│   │   ├── deliveries.html  # Deliveries log & courier agent enrollment
│   │   ├── history.html     # Historical visit filter & view viewer
│   │   ├── reports.html     # DBMS query demonstration showcase
│   │   └── error.html       # Friendly 403 & 404 error page
│   └── static/
│       └── css/
│           └── style.css    # Clean, modern, responsive CSS styling
├── database/
│   ├── schema.sql           # 7 tables, constraints, indexes & view
│   ├── seed.sql             # 8 residents, 3 guards, 5 agents, 25 visits, 10 deliveries
│   └── queries.sql          # 8 annotated SQL demonstration queries for viva
├── scripts/
│   └── generate_seeds.py    # Generates seed.sql with real Argon2 password hashes
├── setup_db.py              # Automatic database creation and population script
├── requirements.txt         # Project dependencies
├── .env                     # Local database credentials & session secret
└── README.md
```

---

## 5. Setup & Installation

### Step 1: Clone or Navigate to the Project
Open terminal or command prompt in `d:\DBMS Project`.

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Database Credentials
Edit the `.env` file with your MySQL server credentials:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=gatepass_db
SECRET_KEY=gatepass_super_secret_session_key_academic_project_2026
```

### Step 4: Initialize the Database
You can initialize the database either via Python or MySQL Workbench:

**Option A (Automatic via Python Script):**
```bash
python setup_db.py
```

**Option B (Via MySQL Workbench):**
1. Open MySQL Workbench and connect to your local MySQL instance.
2. Open and execute `database/schema.sql` (creates `gatepass_db`, tables, and view).
3. Open and execute `database/seed.sql` (loads demo data and hashed passwords).

### Step 5: Start the Web Server
```bash
uvicorn app.main:app --reload
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

FastAPI interactive API documentation is also available at: **`http://127.0.0.1:8000/docs`**

---

## 6. Demo Accounts (For Viva Evaluation)

| Role | Username | Password | Linked Profile / Flat |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Full administrative access |
| **Security Guard** | `guard_ramesh` | `guard123` | Guard on Morning shift |
| **Security Guard** | `guard_suresh` | `guard123` | Guard on Evening shift |
| **Security Guard** | `guard_mahesh` | `guard123` | Guard on Night shift |
| **Resident 1** | `resident_aarav` | `resident123` | Aarav Sharma (Flat A-101) |
| **Resident 2** | `resident_priya` | `resident123` | Priya Verma (Flat A-102) |

---

## 7. Step-by-Step Viva Demo Script

1. **Guard Logs a Visitor:**
   - Log in as `guard_ramesh` / `guard123`.
   - Click **+ Register Visitor**, enter visitor name (e.g. `Kunal Verma`), phone `9876543210`, select Resident **A-101 (Aarav Sharma)**, purpose `Project Discussion`.
   - Submit the form. Notice the status is set to **Pending**.
2. **Resident Approves and Issues Gate Pass:**
   - In a private/incognito window (or after logging out), log in as `resident_aarav` / `resident123`.
   - Go to **My Approvals & Gate Passes**.
   - See Kunal Verma's request under **Pending Visitor Requests**.
   - Click **Approve (Issue Pass)**. Notice the generated gate pass code: `GP-YYYYMMDD-XXXX`.
3. **Guard Records Entry:**
   - Back as `guard_ramesh`, open **Gate Ops (Entry/Exit)**.
   - Kunal Verma now appears in **Approved Visits Awaiting Gate Arrival**.
   - Click **Record Entry**. The visitor moves to **Visitors Currently Inside Society**.
4. **Guard Records Exit:**
   - Click **Log Exit**. The visitor departs and is no longer inside.
5. **Demonstrate DBMS Concept 6 (Subquery):**
   - Log in as `admin` / `admin123`.
   - Click **SQL Reports**. Show Report 1: Residents with visits strictly above the society average.
6. **Demonstrate DBMS Concept 3 (LEFT JOIN):**
   - On **SQL Reports**, show Report 4: Notice **Vikram Malhotra (Flat C-301)** has `NULL` delivery attributes, confirming outer join behavior.
7. **Demonstrate Database View:**
   - Click **History View** in the navbar. Explain that this queries `v_visit_history`.
