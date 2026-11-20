import React, { useState } from 'react';
import { Utensils, AlertTriangle, Coffee } from 'lucide-react';
import { lunchOut, lunchIn } from '../../services/attendance';
import { formatTime } from '../../utils/formatters';

export const LunchPunchWidget = ({ todayStatus, onRefresh, onRequestCorrection }) => {
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState('');
  const [error, setError] = useState(null);

  const att = todayStatus?.attendance;
  const isCheckedIn = !!att?.check_in_time;
  const isCheckedOut = !!att?.check_out_time;

  const lunchRecords = att?.lunch_records || [];
  const latestLunch = lunchRecords.length > 0 ? lunchRecords[lunchRecords.length - 1] : null;
  const isOnLunch = latestLunch && !latestLunch.lunch_in_time;

  const handleLunchOut = async () => {
    setLoading(true);
    setError(null);
    try {
      await lunchOut(notes || null);
      setNotes('');
      onRefresh();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record lunch exit.');
    } finally {
      setLoading(false);
    }
  };

  const handleLunchIn = async () => {
    setLoading(true);
    setError(null);
    try {
      await lunchIn();
      onRefresh();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record lunch return.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 overflow-hidden">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Utensils className="h-5 w-5 text-amber-600" />
            Lunch Break Tracking
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Only required if leaving office physically (1:00 PM – 2:00 PM IST)
          </p>
        </div>
        {isOnLunch && (
          <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-100 text-amber-800 animate-pulse">
            Out for Lunch
          </span>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
          {error}
        </div>
      )}

      <div className="my-5 p-4 rounded-xl bg-slate-50/70 border border-slate-100 text-xs space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-slate-500">Scheduled Lunch Window:</span>
          <span className="font-semibold text-slate-700">1:00 PM to 2:00 PM</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-500">Office Lunch Rule:</span>
          <span className="font-semibold text-slate-700">Employees eating inside do not punch</span>
        </div>
        {latestLunch && (
          <div className="pt-2 border-t border-slate-200/60 flex justify-between items-center">
            <span className="text-slate-500">Today's Punch:</span>
            <span className="font-bold text-slate-800">
              Out: {formatTime(latestLunch.lunch_out_time)} | In: {formatTime(latestLunch.lunch_in_time)}
            </span>
          </div>
        )}
        {latestLunch?.late_minutes > 0 && (
          <div className="flex items-center gap-1.5 text-amber-700 font-bold">
            <AlertTriangle className="h-4 w-4" />
            <span>Late return by {latestLunch.late_minutes} minutes (Returned after 2:00 PM)</span>
          </div>
        )}
      </div>

      {!isCheckedIn ? (
        <p className="text-xs text-slate-400 italic text-center py-2">
          Check in first before recording lunch break.
        </p>
      ) : isCheckedOut ? (
        <p className="text-xs text-slate-400 italic text-center py-2">
          Work day completed. Lunch tracking closed.
        </p>
      ) : (
        <div className="flex flex-col sm:flex-row gap-3">
          {!isOnLunch ? (
            <button
              onClick={handleLunchOut}
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-300 font-bold text-xs transition-colors"
            >
              <Utensils className="h-4 w-4" />
              {loading ? 'Processing...' : 'Step Out for Lunch (Lunch Out)'}
            </button>
          ) : (
            <button
              onClick={handleLunchIn}
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md shadow-emerald-600/20 transition-all"
            >
              <Coffee className="h-4 w-4" />
              {loading ? 'Processing...' : 'Return from Lunch (Lunch In)'}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default LunchPunchWidget;
