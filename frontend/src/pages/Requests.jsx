import React, { useState, useEffect } from 'react';
import api from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import { formatDate } from '../utils/formatters';
import { FileText, PlusCircle, CheckCircle2 } from 'lucide-react';

export const Requests = () => {
  const [activeTab, setActiveTab] = useState('leaves'); // 'leaves' or 'corrections'
  const [leaves, setLeaves] = useState([]);
  const [corrections, setCorrections] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form states
  const [leaveType, setLeaveType] = useState('casual');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');
  const [submitMsg, setSubmitMsg] = useState(null);

  const loadRequests = async () => {
    setLoading(true);
    try {
      const [lRes, cRes] = await Promise.all([
        api.get('/requests/leave'),
        api.get('/requests/corrections'),
      ]);
      setLeaves(lRes.data);
      setCorrections(cRes.data);
    } catch (err) {
      console.error('Error loading requests:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, []);

  const handleLeaveSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/requests/leave', {
        leave_type: leaveType,
        start_date: startDate,
        end_date: endDate,
        reason,
      });
      setSubmitMsg('Leave request submitted successfully.');
      setReason('');
      setStartDate('');
      setEndDate('');
      loadRequests();
      setTimeout(() => setSubmitMsg(null), 3000);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit leave request');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-black text-slate-900">Requests & Approvals</h1>
        <p className="text-xs text-slate-500 mt-1">Submit leave requests and view punch correction status.</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('leaves')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-colors ${
            activeTab === 'leaves'
              ? 'border-solar-500 text-solar-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Leave Applications ({leaves.length})
        </button>
        <button
          onClick={() => setActiveTab('corrections')}
          className={`py-3 px-5 text-xs font-bold border-b-2 transition-colors ${
            activeTab === 'corrections'
              ? 'border-solar-500 text-solar-700'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Attendance Corrections ({corrections.length})
        </button>
      </div>

      {activeTab === 'leaves' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Leave Application Form */}
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 lg:col-span-1">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
              <PlusCircle className="h-4 w-4 text-solar-600" />
              Apply for Leave
            </h3>

            {submitMsg && (
              <div className="mb-4 p-3 bg-emerald-50 text-emerald-800 text-xs rounded-xl font-semibold flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                {submitMsg}
              </div>
            )}

            <form onSubmit={handleLeaveSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Leave Type
                </label>
                <select
                  value={leaveType}
                  onChange={(e) => setLeaveType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200"
                >
                  <option value="casual">Casual Leave</option>
                  <option value="sick">Sick Leave</option>
                  <option value="earned">Earned Leave</option>
                  <option value="unpaid">Unpaid Leave</option>
                </select>
              </div>

              <div>
                <label className="block font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  required
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200"
                />
              </div>

              <div>
                <label className="block font-bold uppercase tracking-wider text-slate-600 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  required
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200"
                />
              </div>

              <div>
                <label className="block font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Reason *
                </label>
                <textarea
                  required
                  rows={3}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Reason for leave request..."
                  className="w-full px-3 py-2 rounded-xl border border-slate-200"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-solar-500 hover:bg-solar-600 text-white font-bold rounded-xl shadow-md shadow-amber-500/20"
              >
                Submit Application
              </button>
            </form>
          </div>

          {/* Leave History Table */}
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 lg:col-span-2">
            <h3 className="text-sm font-bold text-slate-900 mb-4">My Leave History</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-100">
                  <tr>
                    <th className="px-4 py-3">Dates</th>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">Reason</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {leaves.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="px-4 py-6 text-center text-slate-400">
                        No leave applications submitted yet.
                      </td>
                    </tr>
                  ) : (
                    leaves.map((l) => (
                      <tr key={l.id}>
                        <td className="px-4 py-3 font-semibold text-slate-900">
                          {formatDate(l.start_date)} – {formatDate(l.end_date)}
                        </td>
                        <td className="px-4 py-3 capitalize">{l.leave_type}</td>
                        <td className="px-4 py-3 text-slate-600 max-w-xs truncate">{l.reason}</td>
                        <td className="px-4 py-3">
                          <StatusBadge status={l.status} />
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        /* Corrections Table */
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
          <h3 className="text-sm font-bold text-slate-900 mb-4">Attendance Correction Requests</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-100">
                <tr>
                  <th className="px-4 py-3">Target Date</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Reason</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Admin Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {corrections.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-4 py-6 text-center text-slate-400">
                      No correction requests submitted.
                    </td>
                  </tr>
                ) : (
                  corrections.map((c) => (
                    <tr key={c.id}>
                      <td className="px-4 py-3 font-semibold text-slate-900">
                        {formatDate(c.target_date)}
                      </td>
                      <td className="px-4 py-3 capitalize">{c.request_type.replace('_', ' ')}</td>
                      <td className="px-4 py-3 text-slate-600">{c.reason}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={c.status} />
                      </td>
                      <td className="px-4 py-3 text-slate-500">{c.review_notes || '--'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Requests;
