-- MB Solar Hub Attendance & Daily Work Management System
-- Schema Migration: 20261120000001_create_mb_solar_hub_schema.sql

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles (Mapped to Supabase auth.users or internal UUIDs)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    designation VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'employee',
    joining_date DATE NOT NULL DEFAULT CURRENT_DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    phone VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Shifts
CREATE TABLE IF NOT EXISTS public.shifts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL DEFAULT 'Standard Shift',
    start_time TIME NOT NULL DEFAULT '09:00:00',
    end_time TIME NOT NULL DEFAULT '18:00:00',
    check_in_start TIME NOT NULL DEFAULT '08:45:00',
    check_in_end TIME NOT NULL DEFAULT '10:00:00',
    check_out_start TIME NOT NULL DEFAULT '18:00:00',
    check_out_end TIME NOT NULL DEFAULT '19:00:00',
    lunch_start TIME NOT NULL DEFAULT '13:00:00',
    lunch_end TIME NOT NULL DEFAULT '14:00:00',
    is_default BOOLEAN NOT NULL DEFAULT TRUE
);

-- 3. Employee Schedules (Flexible Recurring Weekly Off)
CREATE TABLE IF NOT EXISTS public.employee_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    weekly_off_day INT NOT NULL DEFAULT 6, -- 0=Mon, 6=Sun
    effective_from DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_to DATE,
    created_by UUID REFERENCES public.profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Schedule Overrides (Specific date off / swap / working override)
CREATE TABLE IF NOT EXISTS public.schedule_overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    override_date DATE NOT NULL,
    is_working_day BOOLEAN NOT NULL,
    reason TEXT,
    approved_by UUID REFERENCES public.profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_emp_override_date UNIQUE(employee_id, override_date)
);

-- 5. Holidays
CREATE TABLE IF NOT EXISTS public.holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    holiday_date DATE UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6. Attendance Records
CREATE TABLE IF NOT EXISTS public.attendance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    work_date DATE NOT NULL,
    check_in_time TIMESTAMPTZ,
    check_out_time TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'present',
    late_minutes INT NOT NULL DEFAULT 0,
    work_hours NUMERIC(5, 2),
    check_in_mode VARCHAR(50) NOT NULL DEFAULT 'normal',
    check_out_mode VARCHAR(50) DEFAULT 'normal',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_emp_work_date UNIQUE(employee_id, work_date)
);

-- 7. Lunch Records
CREATE TABLE IF NOT EXISTS public.lunch_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attendance_id UUID NOT NULL REFERENCES public.attendance_records(id) ON DELETE CASCADE,
    employee_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    work_date DATE NOT NULL,
    lunch_out_time TIMESTAMPTZ NOT NULL,
    lunch_in_time TIMESTAMPTZ,
    duration_minutes INT,
    late_minutes INT NOT NULL DEFAULT 0,
    missing_lunch_in BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 8. Leave Requests
CREATE TABLE IF NOT EXISTS public.leave_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    leave_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    reviewed_by UUID REFERENCES public.profiles(id),
    review_notes TEXT,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 9. Correction Requests
CREATE TABLE IF NOT EXISTS public.correction_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    attendance_id UUID REFERENCES public.attendance_records(id) ON DELETE SET NULL,
    request_type VARCHAR(50) NOT NULL,
    target_date DATE NOT NULL,
    requested_time TIMESTAMPTZ,
    requested_off_day INT,
    reason TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    reviewed_by UUID REFERENCES public.profiles(id),
    review_notes TEXT,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 10. Daily Work Entries (Multiple entries per day per employee)
CREATE TABLE IF NOT EXISTS public.daily_work_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    work_date DATE NOT NULL,
    work_description TEXT NOT NULL,
    work_details TEXT,
    start_time TIME,
    end_time TIME,
    is_submitted BOOLEAN NOT NULL DEFAULT FALSE,
    submitted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 11. Report History
CREATE TABLE IF NOT EXISTS public.report_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    employee_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    file_format VARCHAR(10) NOT NULL,
    file_path TEXT,
    file_size_bytes INT,
    status VARCHAR(50) NOT NULL DEFAULT 'generated',
    has_unresolved_corrections BOOLEAN NOT NULL DEFAULT FALSE,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 12. Report Delivery Logs
CREATE TABLE IF NOT EXISTS public.report_delivery_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_history_id UUID NOT NULL REFERENCES public.report_history(id) ON DELETE CASCADE,
    recipient_email VARCHAR(255) NOT NULL,
    recipient_name VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    attempts INT NOT NULL DEFAULT 0,
    last_error TEXT,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 13. Audit Logs
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    target_entity VARCHAR(100) NOT NULL,
    target_id VARCHAR(100),
    changes JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 14. App Settings
CREATE TABLE IF NOT EXISTS public.app_settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for high-performance querying
CREATE INDEX IF NOT EXISTS idx_attendance_emp_date ON public.attendance_records(employee_id, work_date);
CREATE INDEX IF NOT EXISTS idx_lunch_att_id ON public.lunch_records(attendance_id);
CREATE INDEX IF NOT EXISTS idx_daily_work_emp_date ON public.daily_work_entries(employee_id, work_date);
CREATE INDEX IF NOT EXISTS idx_schedules_emp ON public.employee_schedules(employee_id, effective_from);
CREATE INDEX IF NOT EXISTS idx_correction_status ON public.correction_requests(status, target_date);

-- Enable Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.attendance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.lunch_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_work_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leave_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.correction_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employee_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.schedule_overrides ENABLE ROW LEVEL SECURITY;

-- Helper RLS function to check if current Supabase auth user is admin
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = auth.uid() AND role = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RLS Policies: Profiles
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (id = auth.uid() OR public.is_admin());

CREATE POLICY "Admins can update profiles" ON public.profiles
    FOR ALL USING (public.is_admin());

-- RLS Policies: Attendance
CREATE POLICY "Employees can view own attendance" ON public.attendance_records
    FOR SELECT USING (employee_id = auth.uid() OR public.is_admin());

CREATE POLICY "Employees can manage own attendance" ON public.attendance_records
    FOR ALL USING (employee_id = auth.uid() OR public.is_admin());

-- RLS Policies: Daily Work
CREATE POLICY "Employees can manage own daily work" ON public.daily_work_entries
    FOR ALL USING (employee_id = auth.uid() OR public.is_admin());
