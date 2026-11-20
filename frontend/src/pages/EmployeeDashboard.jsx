import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getTodayStatus } from '../services/attendance';
import { getWeeklyReport, downloadWeeklyExcel } from '../services/reports';
import AttendancePunchWidget from '../components/attendance/AttendancePunchWidget';
import LunchPunchWidget from '../components/attendance/LunchPunchWidget';
import StatCard from '../components/common/StatCard';
import Modal from '../components/common/Modal';
import { createCorrectionRequest } from '../services/requests';
import {
  Calendar,
  Clock,
  Briefcase,
  Download,
  AlertCircle,
  CheckCircle2,
  Share2
} from 'lucide-react';

export const EmployeeDashboard = () => {
  const { user } = useAuth();
  const [todayStatus, setTodayStatus] = useState(null);
  const [weeklyData, setWeeklyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isCorrectionOpen, setIsCorrectionOpen] = useState(false);
  const [correctionType, setCorrectionType] = useState('check_in');
  const [correctionReason, setCorrectionReason] = useState('');
  const [correctionTime, setCorrectionTime] = useState('');
  const [correctionMsg, setCorrectionMsg] = useState(null);

  const loadData = async () => {
    try {
      const [status, week] = await Promise.all([
        getTodayStatus(),
        getWeeklyReport(),
      ]);
      setTodayStatus(status);
      setWeeklyData(week);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDownloadWeekly = async () => {
    try {
      await downloadWeeklyExcel();
    } catch (err) {
      alert('Failed to download weekly Excel report.');
    }
  };

  const handleCorrectionSubmit = async (e) => {
    e.preventDefault();
    try {
      await createCorrectionRequest({
        request_type: correctionType,
        target_date: todayStatus?.work_date || new Date().toISOString().split('T')[0],
        requested_time: correctionTime ? `${todayStatus?.work_date}T${correctionTime}:00` : null,
        reason: correctionReason,
      });
      setCorrectionMsg('Correction request submitted for management review.');
      setCorrectionReason('');
      setCorrectionTime('');
      setTimeout(() => {
        setIsCorrectionOpen(false);
        setCorrectionMsg(null);
      }, 1500);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit correction request.');
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading your dashboard...</div>;
  }

  const att = todayStatus?.attendance;

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-3xl p-6 sm:p-8 text-white flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 shadow-md">
        <div>
          <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-solar-500/20 text-solar-300 border border-solar-500/30">
            MB Solar Hub Portal
          </span>
          <h1 className="text-2xl font-black mt-2">
            Welcome back, {user?.full_name}!
          </h1>
          <p className="text-xs text-slate-300 mt-1">
            Designation: <span className="font-semibold text-white">{user?.designation}</span> &nbsp;|&nbsp; ID: {user?.employee_id}
          </p>
        </div>

        {/* WhatsApp ready download button */}
        <button
          onClick={handleDownloadWeekly}
          className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 transition-all shrink-0"
        >
          <Download className="h-4 w-4" />
          <span>Download Weekly Excel (WhatsApp)</span>
        </button>
      </div>

      {/* Week Summary Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Scheduled Days"
          value={weeklyData?.scheduled_working_days || 0}
          subtitle="This week"
          icon={Calendar}
          color="slate"
        />
        <StatCard
          title="Present Days"
          value={weeklyData?.present_days || 0}
          subtitle="Completed shifts"
          icon={CheckCircle2}
          color="emerald"
        />
        <StatCard
          title="Late Arrivals"
          value={weeklyData?.late_days || 0}
          subtitle="After 9:00 AM IST"
          icon={Clock}
          color="amber"
        />
        <StatCard
          title="Total Hours"
          value={`${weeklyData?.total_work_hours || '0.00'} hrs`}
          subtitle="Working duration"
          icon={Briefcase}
          color="sky"
        />
      </div>

      {/* Unresolved correction banner */}
      {todayStatus?.has_unresolved_correction && (
        <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-amber-600 shrink-0" />
          <span>
            You have a pending attendance correction request under management review for today.
          </span>
        </div>
      )}

      {/* Punch Widgets Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AttendancePunchWidget
          todayStatus={todayStatus}
          onRefresh={loadData}
          onRequestCorrection={() => setIsCorrectionOpen(true)}
        />
        <LunchPunchWidget
          todayStatus={todayStatus}
          onRefresh={loadData}
          onRequestCorrection={() => setIsCorrectionOpen(true)}
        />
      </div>

      {/* Correction Request Modal */}
      <Modal
        isOpen={isCorrectionOpen}
        onClose={() => setIsCorrectionOpen(false)}
        title="Submit Attendance Correction"
      >
        {correctionMsg ? (
          <div className="p-4 bg-emerald-50 text-emerald-800 text-xs rounded-xl font-bold flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            {correctionMsg}
          </div>
        ) : (
          <form onSubmit={handleCorrectionSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-bold uppercase tracking-wider text-slate-700 mb-1">
                Correction Type
              </label>
              <select
                value={correctionType}
                onChange={(e) => setCorrectionType(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-200"
              >
                <option value="check_in">Late Check-in (after 10:00 AM)</option>
                <option value="check_out">Late Checkout (after 7:00 PM)</option>
                <option value="lunch_out">Lunch Out Correction</option>
                <option value="lunch_in">Lunch In Correction</option>
              </select>
            </div>

            <div>
              <label className="block font-bold uppercase tracking-wider text-slate-700 mb-1">
                Actual Time (IST)
              </label>
              <input
                type="time"
                required
                value={correctionTime}
                onChange={(e) => setCorrectionTime(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-200"
              >
              </input>
            </div>

            <div>
              <label className="block font-bold uppercase tracking-wider text-slate-700 mb-1">
                Reason for Delay / Correction *
              </label>
              <textarea
                required
                rows={3}
                value={correctionReason}
                onChange={(e) => setCorrectionReason(e.target.value)}
                placeholder="Explain the reason (e.g. Vendor site visit, technical connectivity, client meeting)..."
                className="w-full px-3 py-2 rounded-xl border border-slate-200"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setIsCorrectionOpen(false)}
                className="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-solar-500 text-white font-bold"
              >
                Submit Request
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};

export default EmployeeDashboard;
