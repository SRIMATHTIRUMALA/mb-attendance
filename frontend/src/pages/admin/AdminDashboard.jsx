import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDashboardSummary, triggerManagementDigest } from '../../services/reports';
import StatCard from '../../components/common/StatCard';
import {
  Users,
  CheckCircle2,
  Clock,
  Calendar,
  AlertTriangle,
  FileCheck,
  Send,
  Coffee,
  HelpCircle,
  Briefcase
} from 'lucide-react';

export const AdminDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [digestMsg, setDigestMsg] = useState(null);
  const navigate = useNavigate();

  const loadSummary = async () => {
    try {
      const data = await getDashboardSummary();
      setSummary(data);
    } catch (err) {
      console.error('Error loading dashboard summary:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  const handleSendDigest = async (type = 'daily') => {
    if (window.confirm(`Send ${type} management summary report email to Sir?`)) {
      setTriggering(true);
      try {
        const res = await triggerManagementDigest(type);
        setDigestMsg(`Digest successfully generated and sent to ${res.recipient}.`);
        setTimeout(() => setDigestMsg(null), 4000);
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to dispatch report digest');
      } finally {
        setTriggering(false);
      }
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading admin operations dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-950 via-slate-900 to-amber-950 rounded-3xl p-6 sm:p-8 text-white flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shadow-xl">
        <div>
          <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-solar-500 text-white shadow-md shadow-amber-500/20">
            Management Control Center
          </span>
          <h1 className="text-2xl font-black mt-2">
            MB Solar Hub — Operations & Attendance Overview
          </h1>
          <p className="text-xs text-slate-300 mt-1">
            Real-time office presence, flexible weekly offs, and employee daily work activities.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handleSendDigest('daily')}
            disabled={triggering}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-solar-500 hover:bg-solar-600 text-white font-bold text-xs shadow-md shadow-amber-500/20 disabled:opacity-50 transition-all"
          >
            <Send className="h-3.5 w-3.5" />
            <span>{triggering ? 'Sending...' : 'Send Daily Report to Sir'}</span>
          </button>
        </div>
      </div>

      {digestMsg && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          <span>{digestMsg}</span>
        </div>
      )}

      {/* 10 Operational Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <StatCard
          title="Total Staff"
          value={summary?.total_employees || 0}
          subtitle="Active employees"
          icon={Users}
          color="slate"
        />
        <StatCard
          title="Present Today"
          value={summary?.present_count || 0}
          subtitle="Checked in"
          icon={CheckCircle2}
          color="emerald"
        />
        <StatCard
          title="Late Arrivals"
          value={summary?.late_count || 0}
          subtitle="After 9:00 AM"
          icon={Clock}
          color="amber"
        />
        <StatCard
          title="Weekly Offs"
          value={summary?.weekly_off_count || 0}
          subtitle="Scheduled off today"
          icon={Calendar}
          color="sky"
        />
        <StatCard
          title="Approved Leaves"
          value={summary?.on_leave_count || 0}
          subtitle="On leave"
          icon={FileCheck}
          color="purple"
        />
        <StatCard
          title="Absent"
          value={summary?.absent_count || 0}
          subtitle="Unscheduled absence"
          icon={AlertTriangle}
          color="rose"
        />
        <StatCard
          title="Lunch Delays"
          value={summary?.lunch_delays_count || 0}
          subtitle="Returned after 2 PM"
          icon={Coffee}
          color="amber"
        />
        <StatCard
          title="Missing Punches"
          value={summary?.missing_punches_count || 0}
          subtitle="Open lunch punches"
          icon={HelpCircle}
          color="rose"
        />
        <StatCard
          title="Work Submitted"
          value={summary?.work_submitted_count || 0}
          subtitle="Daily activity logs"
          icon={Briefcase}
          color="emerald"
        />
        <StatCard
          title="Pending Approvals"
          value={summary?.pending_approvals_total || 0}
          subtitle="Corrections & leaves"
          icon={AlertTriangle}
          color="purple"
        />
      </div>

      {/* Quick Action Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div
          onClick={() => navigate('/admin/attendance')}
          className="cursor-pointer bg-white p-6 rounded-2xl border border-slate-200/90 hover:border-solar-400 hover:shadow-md transition-all"
        >
          <div className="flex items-center gap-3 mb-2">
            <Clock className="h-5 w-5 text-solar-600" />
            <h3 className="font-bold text-sm text-slate-900">Attendance & Corrections</h3>
          </div>
          <p className="text-xs text-slate-500">
            Review live check-in and checkout times, approve punch corrections, and inspect lunch duration.
          </p>
        </div>

        <div
          onClick={() => navigate('/admin/reports')}
          className="cursor-pointer bg-white p-6 rounded-2xl border border-slate-200/90 hover:border-solar-400 hover:shadow-md transition-all"
        >
          <div className="flex items-center gap-3 mb-2">
            <Briefcase className="h-5 w-5 text-solar-600" />
            <h3 className="font-bold text-sm text-slate-900">Employee Work Reports</h3>
          </div>
          <p className="text-xs text-slate-500">
            Inspect individual daily work logs, vendor calls, website development notes, and export Excel reports.
          </p>
        </div>

        <div
          onClick={() => navigate('/admin/employees')}
          className="cursor-pointer bg-white p-6 rounded-2xl border border-slate-200/90 hover:border-solar-400 hover:shadow-md transition-all"
        >
          <div className="flex items-center gap-3 mb-2">
            <Users className="h-5 w-5 text-solar-600" />
            <h3 className="font-bold text-sm text-slate-900">Employee Accounts & Shifts</h3>
          </div>
          <p className="text-xs text-slate-500">
            Add team members, configure designations without restrictive departments, and assign weekly offs.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
