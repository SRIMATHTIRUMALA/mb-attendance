import React, { useState } from 'react';
import { LogIn, LogOut, AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import { checkIn, checkOut } from '../../services/attendance';
import { formatTime } from '../../utils/formatters';

export const AttendancePunchWidget = ({ todayStatus, onRefresh, onRequestCorrection }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const att = todayStatus?.attendance;
  const isCheckedIn = !!att?.check_in_time;
  const isCheckedOut = !!att?.check_out_time;

  const handleCheckIn = async () => {
    setLoading(true);
    setError(null);
    try {
      await checkIn();
      onRefresh();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record check-in.');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async () => {
    setLoading(true);
    setError(null);
    try {
      await checkOut();
      onRefresh();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record check-out.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 overflow-hidden">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Clock className="h-5 w-5 text-solar-600" />
            Office Attendance Punch
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Shift: 9:00 AM – 6:00 PM IST (Normal office hours)
          </p>
        </div>
        {att?.status && (
          <span
            className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
              att.status === 'present'
                ? 'bg-emerald-100 text-emerald-800'
                : att.status === 'late'
                ? 'bg-amber-100 text-amber-800'
                : 'bg-slate-100 text-slate-700'
            }`}
          >
            {att.status} {att.late_minutes > 0 ? `(${att.late_minutes}m late)` : ''}
          </span>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold">{error}</p>
            {error.includes('Correction Request') && (
              <button
                onClick={onRequestCorrection}
                className="mt-2 inline-flex items-center text-xs font-bold underline hover:text-rose-900"
              >
                Click here to submit an Attendance Correction Request &rarr;
              </button>
            )}
          </div>
        </div>
      )}

      {/* Punch status grid */}
      <div className="grid grid-cols-2 gap-4 my-6">
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Check In</p>
          <p className="text-xl font-black text-slate-900 mt-1">
            {isCheckedIn ? formatTime(att.check_in_time) : '--:--'}
          </p>
          <p className="text-[11px] text-slate-500 mt-1">Window: 8:45 AM – 10:00 AM</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Check Out</p>
          <p className="text-xl font-black text-slate-900 mt-1">
            {isCheckedOut ? formatTime(att.check_out_time) : '--:--'}
          </p>
          <p className="text-[11px] text-slate-500 mt-1">Window: 6:00 PM – 7:00 PM</p>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        {!isCheckedIn ? (
          <button
            onClick={handleCheckIn}
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-solar-500 hover:bg-solar-600 text-white font-bold text-sm shadow-md shadow-amber-500/20 disabled:opacity-50 transition-all"
          >
            <LogIn className="h-4 w-4" />
            {loading ? 'Processing...' : 'Punch Check In'}
          </button>
        ) : !isCheckedOut ? (
          <button
            onClick={handleCheckOut}
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm shadow-md shadow-slate-900/20 disabled:opacity-50 transition-all"
          >
            <LogOut className="h-4 w-4" />
            {loading ? 'Processing...' : 'Punch Check Out'}
          </button>
        ) : (
          <div className="flex-1 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-center text-xs font-bold text-emerald-800 flex items-center justify-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            Attendance completed for today! (Hours: {att.work_hours || '--'})
          </div>
        )}

        <button
          onClick={onRequestCorrection}
          className="px-4 py-3 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold transition-colors"
        >
          Submit Correction
        </button>
      </div>
    </div>
  );
};

export default AttendancePunchWidget;
