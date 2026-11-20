# MB Solar Hub — Employee Attendance & Daily Work Management System

Production-ready web application for **MB Solar Hub**, built to replace manual office attendance and eliminate separate Excel sheets shared via WhatsApp.

---

## 1. System Architecture & Tech Stack

### Frontend
- **React (Vite)** with modern functional components & hooks
- **Tailwind CSS** with custom Solar Amber & Navy branding palette
- **React Router v6** for nested, role-protected routes
- **Axios** with authenticated JWT interceptors
- **Lucide React** icons
- **Vitest & React Testing Library** for frontend testing

### Backend
- **Python 3.12+ (FastAPI)**
- **SQLAlchemy 2.x** with declarative ORM models
- **Pydantic v2** schemas and validation
- **Alembic** migrations & direct Supabase PostgreSQL DDL migrations
- **openpyxl** for branded employee activity Excel reports (WhatsApp ready)
- **ReportLab** for PDF activity and attendance reports
- **Pytest & TestClient** testing all 14 mandatory business rules

### Database & Authentication
- **Supabase-hosted PostgreSQL 17** (Project `mb-associate`)
- **Supabase Auth & JWT tokens** verified on every request
- **Row-Level Security (RLS)** policies enabled across all tables
- **Server-side role authorization** (Never trusts frontend identity)

---

## 2. Core Business Rules (Asia/Kolkata IST)

1. **Office Shifts**:
   - Standard working hours: **9:00 AM to 6:00 PM IST**.
2. **Check-In Rules**:
   - Check-in window opens: **8:45 AM IST**.
   - Check-in window closes: **10:00 AM IST**.
   - **8:45 AM - 9:00 AM**: On time (`late_minutes = 0`).
   - **9:01 AM - 10:00 AM**: Late arrival (`late_minutes` computed against 9:00 AM).
   - **After 10:00 AM**: Normal check-in locked. Employee submits a **Late Check-In Correction Request** with reasons. *The employee is never automatically marked absent merely because the normal window closed.*
3. **Check-Out Rules**:
   - Opens: **6:00 PM IST**. Closes: **7:00 PM IST**.
   - Before 6:00 PM: Check-out blocked.
   - After 7:00 PM: Check-out locked. Requires checkout correction request. *Checkout times are never fabricated.*
4. **Lunch Tracking (1:00 PM – 2:00 PM)**:
   - Only employees physically stepping outside the office punch **Lunch Out** and **Lunch In**. Employees eating inside the office do not punch lunch.
   - Returning at 2:15 PM records **15 minutes late return**.
   - Invalid transitions (e.g. Lunch In without Lunch Out) are strictly blocked.
5. **Flexible Weekly Offs**:
   - Sunday is **not an assumed universal holiday**. Employees work Sundays if scheduled and take offs on other days (e.g. Wednesday).
   - Working days are computed from actual employee schedules rather than fixed month calculations.
6. **Daily Work Management**:
   - Multiple activities per day per employee.
   - No mandatory Completed/In Progress buttons.
   - Supports solar vendor calls, customer interactions, chatbot programming, etc.
   - Includes draft saving and daily submission with change audit logging.
7. **Reporting & WhatsApp Integration**:
   - Employees can download their weekly Excel report directly and forward it via WhatsApp.
   - Sir (Management) receives automated digest emails with summary and separate employee Excel attachments.
   - Unresolved corrections are highlighted with warning flags.

---

## 3. Directory Structure

```text
mb_attendance/
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/ (Logo, Modal, Navbar, Sidebar, StatCard, StatusBadge)
│   │   │   ├── layout/ (AppLayout)
│   │   │   ├── attendance/ (AttendancePunchWidget, LunchPunchWidget)
│   │   │   └── work/ (WorkEntryForm, WorkEntryList)
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── EmployeeDashboard.jsx
│   │   │   ├── DailyWork.jsx
│   │   │   ├── AttendanceHistory.jsx
│   │   │   ├── WeeklySchedule.jsx
│   │   │   ├── Requests.jsx
│   │   │   └── admin/
│   │   │       ├── AdminDashboard.jsx
│   │   │       ├── Employees.jsx
│   │   │       ├── EmployeeDetails.jsx
│   │   │       ├── AttendanceReview.jsx
│   │   │       ├── WorkReports.jsx
│   │   │       └── Settings.jsx
│   │   ├── contexts/ (AuthContext.jsx)
│   │   ├── services/ (api.js, attendance.js, employees.js, work.js, reports.js, requests.js)
│   │   ├── utils/ (formatters.js)
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env.example
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/ (config.py, security.py)
│   │   ├── api/ (auth.py, employees.py, attendance.py, lunch.py, daily_work.py, schedules.py, requests.py, reports.py)
│   │   ├── models/ (profile.py, schedule.py, attendance.py, daily_work.py, request.py, report.py)
│   │   ├── schemas/ (auth.py, employee.py, attendance.py, daily_work.py, request.py, report.py)
│   │   ├── services/ (attendance_service.py, schedule_service.py, report_service.py, email_service.py)
│   │   └── db/ (database.py, base.py)
│   ├── alembic/
│   ├── tests/ (conftest.py, test_attendance_rules.py)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── supabase/
│   └── migrations/
│       └── 20261120000001_create_mb_solar_hub_schema.sql
├── scripts/
│   ├── run_backend.ps1
│   └── run_frontend.ps1
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 4. Local Development Setup

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Git

### Backend Setup
1. Open a terminal in the project directory:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r backend/requirements.txt email-validator
   ```

2. Copy the environment configuration:
   ```powershell
   cp backend/.env.example backend/.env
   ```

3. Run the backend server:
   ```powershell
   .\scripts\run_backend.ps1
   ```
   FastAPI server will be live at `http://localhost:8000` (Docs at `http://localhost:8000/docs`).

### Frontend Setup
1. Open another terminal and install dependencies:
   ```powershell
   cd frontend
   npm install
   ```

2. Start the Vite dev server:
   ```powershell
   npm run dev
   ```
   Frontend will run at `http://localhost:5173`.

---

## 5. Seed Accounts & Credentials

The system comes pre-seeded on the connected Supabase instance:

| Role | Email | Password | Details |
|------|-------|----------|---------|
| **Admin (Sir)** | `management@mbsolarhub.com` | `MBSolar@2026` | Full management access, approvals, reports |
| **Employee 1** | `rajesh@mbsolarhub.com` | `MBSolar@2026` | Rajesh Sharma (Business Analyst, Sunday off) |
| **Employee 2** | `priya@mbsolarhub.com` | `MBSolar@2026` | Priya Patel (Software Engineer, Wednesday off, works Sunday) |

---

## 6. Running Automated Tests

### Backend Pytest Suite (All 14 Business Rules)
```powershell
$env:PYTHONPATH="backend"
.\.venv\Scripts\python.exe -m pytest backend/tests -v
```
**Test Results:**
- `test_rule_1_check_in_on_time`: PASSED (8:50 AM on time)
- `test_rule_2_check_in_late`: PASSED (9:30 AM 30 mins late)
- `test_rule_3_check_in_after_window_requires_request`: PASSED (10:15 AM check-in locked)
- `test_rule_4_checkout_before_6pm_blocked`: PASSED (5:45 PM checkout blocked)
- `test_rule_5_checkout_accepted`: PASSED (6:30 PM checkout accepted)
- `test_rule_6_checkout_after_7pm_requires_request`: PASSED (7:15 PM checkout locked)
- `test_rule_7_lunch_return_late`: PASSED (2:15 PM return = 15m late)
- `test_rule_8_sunday_work_valid_if_scheduled`: PASSED (Sunday scheduled work)
- `test_rule_9_wednesday_off_not_absent`: PASSED (Wednesday scheduled off)
- `test_rule_10_unauthorized_cross_access_denied`: PASSED (Strict employee isolation)
- `test_rule_11_multiple_daily_work_entries`: PASSED (Multiple activities saved)
- `test_rule_12_weekly_report_segregation`: PASSED (Employee report segregation)
- `test_rule_13_report_delivery_tracking`: PASSED (Delivery log recording)
- `test_rule_14_no_duplicate_attendance_punches`: PASSED (Duplicate punches rejected)

### Frontend Tests & Production Build
```powershell
cd frontend
npm run test    # Runs Vitest
npm run build   # Validates production bundle
```

---

## 7. Deployment Instructions

### Frontend on Vercel
1. Push this repository to GitHub or GitLab.
2. In Vercel, import the repository and set **Root Directory** to `frontend`.
3. Framework Preset: **Vite**.
4. Set Environment Variables:
   - `VITE_API_URL`: Your deployed FastAPI backend URL (e.g. `https://api.mbsolarhub.com/api`).
   - `VITE_SUPABASE_URL`: `https://hpfqqbuaozdgpsdvylrh.supabase.co`.
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key.
5. Deploy. Vercel's rewrite configuration in `frontend/vercel.json` ensures client-side routing works smoothly.

### Backend on Render / Railway / Fly.io / Docker
1. The backend includes a production-ready `backend/Dockerfile` configured with `TZ=Asia/Kolkata`.
2. Configure Environment Variables on your hosting provider:
   - `DATABASE_URL`: Your Supabase Transaction Pooler connection string (`postgresql+psycopg://...`).
   - `SUPABASE_URL`: `https://hpfqqbuaozdgpsdvylrh.supabase.co`.
   - `SUPABASE_JWT_SECRET`: Your Supabase JWT secret.
   - `TIMEZONE`: `Asia/Kolkata`.
   - `CORS_ORIGINS`: Your Vercel frontend URL (e.g. `https://mb-solar-hub.vercel.app`).
   - `SIR_EMAIL`: `management@mbsolarhub.com`.
3. Startup command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Database on Supabase
- The complete normalized schema with RLS policies is available in `supabase/migrations/20261120000001_create_mb_solar_hub_schema.sql`.
- Applied and active on Supabase project `hpfqqbuaozdgpsdvylrh`.

---

## 8. Backup & Recovery Guidance

1. **Supabase Automated Backups**: Supabase includes daily automated backups with Point-in-Time Recovery (PITR) on Pro plans.
2. **Manual Schema and Data Dump**:
   ```bash
   pg_dump --host=db.hpfqqbuaozdgpsdvylrh.supabase.co --username=postgres --dbname=postgres > mb_solar_hub_backup.sql
   ```
3. **Restoring Data**:
   ```bash
   psql --host=YOUR_HOST --username=postgres --dbname=postgres < mb_solar_hub_backup.sql
   ```
