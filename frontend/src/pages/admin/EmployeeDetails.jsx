import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getEmployee } from '../../services/employees';
import { getWeeklyReport, downloadWeeklyExcel, downloadReportPdf } from '../../services/reports';
import { getAttendanceHistory } from '../../services/attendance';
import { getDailyWork } from '../../services/work';
import StatusBadge from '../../components/common/StatusBadge';
import { formatDate, formatTime, getDayName } from '../../utils/formatters';
import {
  ArrowLeft,
  Download,
  Calendar,
  Clock,
  Briefcase,
  FileText
} from 'lucide-react';

export const EmployeeDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState(null);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [workEntries, setWorkEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [emp, rep, att, work] = await Promise.all([
          getEmployee(id),
          getWeeklyReport({ employee_id: id }),
          getAttendanceHistory({ employee_id: id }),
          getDailyWork({ employee_id: id }),
        ]);
        setEmployee(emp);
        setWeeklyReport(rep);
        setAttendance(att);
        setWorkEntries(work);
      } catch (err) {
        console.error('Error fetching employee details:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading authorized employee records...</div>;
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/admin/employees')}
        className="flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        <span>Back to Employee List</span>
      </button>

      {/* Employee Profile Header */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black text-slate-900">{employee?.full_name}</h1>
            <span className="font-mono text-xs px-2.5 py-0.5 bg-slate-100 text-slate-700 rounded-md font-bold">
              {employee?.employee_id}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Designation: <span className="font-semibold text-slate-800">{employee?.designation}</span> &nbsp;|&nbsp;
            Weekly Off: <span className="font-semibold text-solar-700">{getDayName(employee?.current_weekly_off)}</span> &nbsp;|&nbsp;
            Joined: {formatDate(employee?.joining_date)}
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => downloadWeeklyExcel({ employee_id: id })}
            className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-600/20 transition-all"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Download Excel</span>
          </button>
          <button
            onClick={() => downloadReportPdf({ employee_id: id })}
            className="flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-all"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Download PDF</span>
          </button>
        </div>
      </div>

      {/* Recent Work Activities */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
        <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Briefcase className="h-4 w-4 text-solar-600" />
          Recent Daily Work Entries
        </h3>
        {workEntries.length === 0 ? (
          <p className="text-xs text-slate-400">No work entries logged by this employee yet.</p>
        ) : (
          <div className="space-y-3">
            {workEntries.map((w) => (
              <div key={w.id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 text-xs">
                <div className="flex justify-between items-start">
                  <p className="font-bold text-slate-900">{w.work_description}</p>
                  <span className="text-slate-400 font-medium">{formatDate(w.work_date)}</span>
                </div>
                {w.work_details && (
                  <p className="text-slate-600 mt-1 whitespace-pre-line bg-white/70 p-2 rounded border border-slate-200/60">
                    {w.work_details}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Attendance History */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
        <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Clock className="h-4 w-4 text-solar-600" />
          Attendance Records
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-100">
              <tr>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Check In</th>
                <th className="px-4 py-3">Check Out</th>
                <th className="px-4 py-3">Late Mins</th>
                <th className="px-4 py-3">Hours</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {attendance.map((a) => (
                <tr key={a.id}>
                  <td className="px-4 py-3 font-semibold">{formatDate(a.work_date)}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={a.status} />
                  </td>
                  <td className="px-4 py-3">{formatTime(a.check_in_time)}</td>
                  <td className="px-4 py-3">{formatTime(a.check_out_time)}</td>
                  <td className="px-4 py-3 text-amber-700">{a.late_minutes > 0 ? `${a.late_minutes}m` : '--'}</td>
                  <td className="px-4 py-3 font-bold">{a.work_hours || '--'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default EmployeeDetails;
