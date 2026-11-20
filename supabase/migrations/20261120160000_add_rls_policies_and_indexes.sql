-- MB Solar Hub: RLS Policies, Security Hardening & Performance Indexes
-- Applied via Supabase MCP on 2026-11-20

-- ============================================
-- SECURITY: Fix public SECURITY DEFINER functions
-- ============================================
REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM anon, authenticated, PUBLIC;

-- Create is_admin() helper with locked-down search_path
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = auth.uid() AND role = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

REVOKE EXECUTE ON FUNCTION public.is_admin() FROM anon, PUBLIC;
GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated;

-- ============================================
-- RLS POLICIES: profiles
-- ============================================
CREATE POLICY "profiles_select_own_or_admin" ON public.profiles
  FOR SELECT TO authenticated
  USING (id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "profiles_insert_admin" ON public.profiles
  FOR INSERT TO authenticated
  WITH CHECK (public.is_admin());

CREATE POLICY "profiles_update_admin" ON public.profiles
  FOR UPDATE TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

CREATE POLICY "profiles_delete_admin" ON public.profiles
  FOR DELETE TO authenticated
  USING (public.is_admin());

-- ============================================
-- RLS POLICIES: shifts
-- ============================================
ALTER TABLE public.shifts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "shifts_select_authenticated" ON public.shifts
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "shifts_modify_admin" ON public.shifts
  FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ============================================
-- RLS POLICIES: employee_schedules
-- ============================================
CREATE POLICY "schedules_select_own_or_admin" ON public.employee_schedules
  FOR SELECT TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "schedules_modify_admin" ON public.employee_schedules
  FOR INSERT TO authenticated
  WITH CHECK (public.is_admin());

CREATE POLICY "schedules_update_admin" ON public.employee_schedules
  FOR UPDATE TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

CREATE POLICY "schedules_delete_admin" ON public.employee_schedules
  FOR DELETE TO authenticated
  USING (public.is_admin());

-- ============================================
-- RLS POLICIES: schedule_overrides
-- ============================================
CREATE POLICY "overrides_select_own_or_admin" ON public.schedule_overrides
  FOR SELECT TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "overrides_modify_admin" ON public.schedule_overrides
  FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ============================================
-- RLS POLICIES: holidays
-- ============================================
ALTER TABLE public.holidays ENABLE ROW LEVEL SECURITY;

CREATE POLICY "holidays_select_authenticated" ON public.holidays
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "holidays_modify_admin" ON public.holidays
  FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ============================================
-- RLS POLICIES: attendance_records
-- ============================================
CREATE POLICY "attendance_select_own_or_admin" ON public.attendance_records
  FOR SELECT TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "attendance_insert_own_or_admin" ON public.attendance_records
  FOR INSERT TO authenticated
  WITH CHECK (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "attendance_update_own_or_admin" ON public.attendance_records
  FOR UPDATE TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin())
  WITH CHECK (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "attendance_delete_admin" ON public.attendance_records
  FOR DELETE TO authenticated
  USING (public.is_admin());

-- ============================================
-- RLS POLICIES: lunch_records
-- ============================================
CREATE POLICY "lunch_select_own_or_admin" ON public.lunch_records
  FOR SELECT TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "lunch_insert_own_or_admin" ON public.lunch_records
  FOR INSERT TO authenticated
  WITH CHECK (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "lunch_update_own_or_admin" ON public.lunch_records
  FOR UPDATE TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin())
  WITH CHECK (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "lunch_delete_admin" ON public.lunch_records
  FOR DELETE TO authenticated
  USING (public.is_admin());

-- ============================================
-- RLS POLICIES: leave_requests
-- ============================================
CREATE POLICY "leave_select_own_or_admin" ON public.leave_requests
  FOR SELECT TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "leave_insert_own" ON public.leave_requests
  FOR INSERT TO authenticated
  WITH CHECK (employee_id = (select auth.uid()));

CREATE POLICY "leave_update_own_or_admin" ON public.leave_requests
  FOR UPDATE TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin())
  WITH CHECK (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "leave_delete_admin" ON public.leave_requests
  FOR DELETE TO authenticated
  USING (public.is_admin());

-- ============================================
-- RLS POLICIES: correction_requests
-- ============================================
CREATE POLICY "correction_select_own_or_admin" ON public.correction_requests
  FOR SELECT TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "correction_insert_own" ON public.correction_requests
  FOR INSERT TO authenticated
  WITH CHECK (employee_id = (select auth.uid()));

CREATE POLICY "correction_update_own_or_admin" ON public.correction_requests
  FOR UPDATE TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin())
  WITH CHECK (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "correction_delete_admin" ON public.correction_requests
  FOR DELETE TO authenticated
  USING (public.is_admin());

-- ============================================
-- RLS POLICIES: daily_work_entries
-- ============================================
CREATE POLICY "work_select_own_or_admin" ON public.daily_work_entries
  FOR SELECT TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "work_insert_own" ON public.daily_work_entries
  FOR INSERT TO authenticated
  WITH CHECK (employee_id = (select auth.uid()));

CREATE POLICY "work_update_own" ON public.daily_work_entries
  FOR UPDATE TO authenticated
  USING (employee_id = (select auth.uid()))
  WITH CHECK (employee_id = (select auth.uid()));

CREATE POLICY "work_delete_own_or_admin" ON public.daily_work_entries
  FOR DELETE TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin());

-- ============================================
-- RLS POLICIES: report_history
-- ============================================
CREATE POLICY "report_select_own_or_admin" ON public.report_history
  FOR SELECT TO authenticated
  USING (employee_id = (select auth.uid()) OR public.is_admin());

CREATE POLICY "report_modify_admin" ON public.report_history
  FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ============================================
-- RLS POLICIES: report_delivery_logs
-- ============================================
CREATE POLICY "delivery_logs_admin_only" ON public.report_delivery_logs
  FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ============================================
-- RLS POLICIES: audit_logs
-- ============================================
CREATE POLICY "audit_logs_admin_only" ON public.audit_logs
  FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ============================================
-- RLS POLICIES: app_settings
-- ============================================
CREATE POLICY "settings_select_authenticated" ON public.app_settings
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "settings_modify_admin" ON public.app_settings
  FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ============================================
-- PERFORMANCE: Indexes on all foreign keys
-- ============================================
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor ON public.audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_correction_attendance ON public.correction_requests(attendance_id);
CREATE INDEX IF NOT EXISTS idx_correction_employee ON public.correction_requests(employee_id);
CREATE INDEX IF NOT EXISTS idx_correction_reviewed_by ON public.correction_requests(reviewed_by);
CREATE INDEX IF NOT EXISTS idx_daily_work_employee ON public.daily_work_entries(employee_id);
CREATE INDEX IF NOT EXISTS idx_schedules_created_by ON public.employee_schedules(created_by);
CREATE INDEX IF NOT EXISTS idx_schedules_employee ON public.employee_schedules(employee_id);
CREATE INDEX IF NOT EXISTS idx_leave_employee ON public.leave_requests(employee_id);
CREATE INDEX IF NOT EXISTS idx_leave_reviewed_by ON public.leave_requests(reviewed_by);
CREATE INDEX IF NOT EXISTS idx_lunch_attendance ON public.lunch_records(attendance_id);
CREATE INDEX IF NOT EXISTS idx_lunch_employee ON public.lunch_records(employee_id);
CREATE INDEX IF NOT EXISTS idx_delivery_report ON public.report_delivery_logs(report_history_id);
CREATE INDEX IF NOT EXISTS idx_report_employee ON public.report_history(employee_id);
CREATE INDEX IF NOT EXISTS idx_overrides_approved_by ON public.schedule_overrides(approved_by);
CREATE INDEX IF NOT EXISTS idx_overrides_employee ON public.schedule_overrides(employee_id);

-- ============================================
-- SEED DATA: Default shift & app settings
-- ============================================
INSERT INTO public.shifts (id, name, start_time, end_time, check_in_start, check_in_end, check_out_start, check_out_end, lunch_start, lunch_end, is_default)
VALUES (
  '00000000-0000-0000-0000-000000000010',
  'Standard Shift',
  '09:00:00', '18:00:00',
  '08:45:00', '10:00:00',
  '18:00:00', '19:00:00',
  '13:00:00', '14:00:00',
  true
) ON CONFLICT (id) DO NOTHING;

INSERT INTO public.app_settings (key, value, description)
VALUES
  ('management_email', '"management@mbsolarhub.com"', 'Email for management daily digest'),
  ('company_name', '"MB Solar Hub"', 'Company display name'),
  ('timezone', '"Asia/Kolkata"', 'Default timezone for all operations'),
  ('daily_report_time', '"19:15"', 'Time to send daily management report (HH:MM IST)'),
  ('weekly_report_day', '"Monday"', 'Day to send weekly report'),
  ('weekly_report_time', '"09:00"', 'Time to send weekly report (HH:MM IST)'),
  ('monthly_report_day', '1', 'Day of month for monthly report'),
  ('monthly_report_time', '"09:00"', 'Time to send monthly report (HH:MM IST)')
ON CONFLICT (key) DO NOTHING;
