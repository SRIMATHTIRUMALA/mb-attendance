import React, { useState, useEffect } from 'react';
import { getAttendanceHistory } from '../services/attendance';
import StatusBadge from '../components/common/StatusBadge';
import { formatDate, formatTime } from '../utils/formatters';
import { Calendar, Filter } from 'lucide-react';

export const AttendanceHistory = () => {
  const [history, setHistory] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(true);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      const data = await getAttendanceHistory(params);
      setHistory(data);
    } catch (err) {
      console.error('Error loading history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-black text-slate-900">Attendance History</h1>
          <p className="text-xs text-slate-500 mt-1">Review your past punches, late minutes, and working hours.</p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 bg-white p-2 rounded-xl border border-slate-200">
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="text-xs px-2 py-1 rounded border border-slate-200 text-slate-700"
          />
          <span className="text-xs text-slate-400">to</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="text-xs px-2 py-1 rounded border border-slate-200 text-slate-700"
          />
          <button
            onClick={loadHistory}
            className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded text-xs font-semibold"
          >
            Filter
          </button>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-100">
              <tr>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">In Time</th>
                <th className="px-6 py-4">Out Time</th>
                <th className="px-6 py-4">Late Arrivals</th>
                <th className="px-6 py-4">Work Hours</th>
                <th className="px-6 py-4">Lunch Punch</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-slate-400">
                    Loading records...
                  </td>
                </tr>
              ) : history.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-slate-400">
                    No attendance records found for this period.
                  </td>
                </tr>
              ) : (
                history.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-50/50">
                    <td className="px-6 py-4 font-bold text-slate-900">
                      {formatDate(row.work_date)}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={row.status} />
                    </td>
                    <td className="px-6 py-4 text-slate-700 font-medium">
                      {formatTime(row.check_in_time)}
                    </td>
                    <td className="px-6 py-4 text-slate-700 font-medium">
                      {formatTime(row.check_out_time)}
                    </td>
                    <td className="px-6 py-4 text-amber-700 font-medium">
                      {row.late_minutes > 0 ? `${row.late_minutes} mins` : '--'}
                    </td>
                    <td className="px-6 py-4 font-bold text-slate-900">
                      {row.work_hours ? `${row.work_hours} hrs` : '--'}
                    </td>
                    <td className="px-6 py-4 text-slate-500">
                      {row.lunch_records && row.lunch_records.length > 0 ? (
                        <span>
                          {formatTime(row.lunch_records[0].lunch_out_time)} - {formatTime(row.lunch_records[0].lunch_in_time)}
                        </span>
                      ) : (
                        '--'
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AttendanceHistory;
