import React, { useState, useEffect } from 'react';
import { getEmployees } from '../../services/employees';
import { getDailyWork } from '../../services/work';
import { downloadWeeklyExcel, downloadReportPdf } from '../../services/reports';
import { formatDate } from '../../utils/formatters';
import { Briefcase, Download, Calendar, Filter } from 'lucide-react';

export const WorkReports = () => {
  const [employees, setEmployees] = useState([]);
  const [selectedEmp, setSelectedEmp] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [workEntries, setWorkEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStaff = async () => {
      try {
        const staff = await getEmployees();
        setEmployees(staff);
        if (staff.length > 0) {
          setSelectedEmp(staff[0].id);
        }
      } catch (err) {
        console.error('Error fetching staff list:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStaff();
  }, []);

  const loadWork = async () => {
    if (!selectedEmp) return;
    setLoading(true);
    try {
      const params = { employee_id: selectedEmp };
      if (selectedDate) params.work_date = selectedDate;
      const data = await getDailyWork(params);
      setWorkEntries(data);
    } catch (err) {
      console.error('Error fetching work logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWork();
  }, [selectedEmp, selectedDate]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-black text-slate-900">Work & Activity Reports</h1>
          <p className="text-xs text-slate-500 mt-1">
            Review vendor calls, customer interactions, chatbot updates, and download individual Excel files.
          </p>
        </div>

        {selectedEmp && (
          <div className="flex gap-2">
            <button
              onClick={() => downloadWeeklyExcel({ employee_id: selectedEmp })}
              className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-600/20"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Download Excel</span>
            </button>
            <button
              onClick={() => downloadReportPdf({ employee_id: selectedEmp })}
              className="flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Download PDF</span>
            </button>
          </div>
        )}
      </div>

      {/* Select Employee and Date */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-sm flex flex-wrap gap-4 items-center">
        <div>
          <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">
            Select Employee:
          </label>
          <select
            value={selectedEmp}
            onChange={(e) => setSelectedEmp(e.target.value)}
            className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-800"
          >
            {employees.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.full_name} ({emp.employee_id} - {emp.designation})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">
            Filter by Date (Optional):
          </label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs text-slate-800"
          />
        </div>
      </div>

      {/* Activity Entries Feed */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
        <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Briefcase className="h-4 w-4 text-solar-600" />
          Logged Activities for Selected Employee
        </h3>

        {workEntries.length === 0 ? (
          <p className="text-xs text-slate-400 py-4">No daily work activities logged for this selection.</p>
        ) : (
          <div className="space-y-3">
            {workEntries.map((w) => (
              <div key={w.id} className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-xs">
                <div className="flex justify-between items-start">
                  <p className="font-bold text-slate-900">{w.work_description}</p>
                  <span className="text-slate-400 font-medium">{formatDate(w.work_date)}</span>
                </div>
                {w.work_details && (
                  <p className="text-slate-600 mt-2 whitespace-pre-line bg-white p-3 rounded-lg border border-slate-200/70">
                    {w.work_details}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkReports;
