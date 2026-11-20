import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import StatusBadge from '../../components/common/StatusBadge';
import { formatDate, formatTime } from '../../utils/formatters';
import { Clock, Check, X, AlertTriangle } from 'lucide-react';

export const AttendanceReview = () => {
  const [corrections, setCorrections] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [corrRes, attRes] = await Promise.all([
        api.get('/requests/corrections?status_filter=pending'),
        api.get('/attendance/history'),
      ]);
      setCorrections(corrRes.data);
      setAttendance(attRes.data);
    } catch (err) {
      console.error('Error loading attendance review data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleReview = async (id, status) => {
    const notes = prompt(`Optional management note for ${status}:`);
    setActionLoading(id);
    try {
      await api.patch(`/requests/corrections/${id}/review`, {
        status,
        review_notes: notes || null,
      });
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to review request');
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-black text-slate-900">Attendance & Corrections Review</h1>
        <p className="text-xs text-slate-500 mt-1">
          Review employee attendance punches and approve late check-in or checkout correction requests.
        </p>
      </div>

      {/* Pending Correction Approvals */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
        <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-600" />
          Pending Punch Correction Requests ({corrections.length})
        </h3>

        {corrections.length === 0 ? (
          <p className="text-xs text-slate-400 py-3">All punch corrections have been reviewed.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-100">
                <tr>
                  <th className="px-4 py-3">Employee</th>
                  <th className="px-4 py-3">Target Date</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Reason</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {corrections.map((c) => (
                  <tr key={c.id}>
                    <td className="px-4 py-3 font-bold text-slate-900">
                      {c.employee_name || 'Staff Member'}
                    </td>
                    <td className="px-4 py-3">{formatDate(c.target_date)}</td>
                    <td className="px-4 py-3 capitalize">{c.request_type.replace('_', ' ')}</td>
                    <td className="px-4 py-3 text-slate-600 max-w-xs">{c.reason}</td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <button
                        onClick={() => handleReview(c.id, 'approved')}
                        disabled={actionLoading === c.id}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs"
                      >
                        <Check className="h-3.5 w-3.5" />
                        <span>Approve</span>
                      </button>
                      <button
                        onClick={() => handleReview(c.id, 'rejected')}
                        disabled={actionLoading === c.id}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs"
                      >
                        <X className="h-3.5 w-3.5" />
                        <span>Reject</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent Attendance Feed */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
        <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Clock className="h-4 w-4 text-solar-600" />
          Recent Office Attendance Records
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-100">
              <tr>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Check In</th>
                <th className="px-4 py-3">Check Out</th>
                <th className="px-4 py-3">Late Delay</th>
                <th className="px-4 py-3">Mode</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {attendance.slice(0, 15).map((a) => (
                <tr key={a.id}>
                  <td className="px-4 py-3 font-semibold text-slate-900">{formatDate(a.work_date)}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={a.status} />
                  </td>
                  <td className="px-4 py-3">{formatTime(a.check_in_time)}</td>
                  <td className="px-4 py-3">{formatTime(a.check_out_time)}</td>
                  <td className="px-4 py-3 text-amber-700">{a.late_minutes > 0 ? `${a.late_minutes}m` : '--'}</td>
                  <td className="px-4 py-3 font-mono text-[11px] text-slate-500">{a.check_in_mode}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AttendanceReview;
