import React, { useState } from 'react';
import { Trash2, Edit3, Send, CheckCircle2, Clock } from 'lucide-react';
import { updateDailyWork, deleteDailyWork } from '../../services/work';
import { formatTime } from '../../utils/formatters';

export const WorkEntryList = ({ entries, onRefresh }) => {
  const [editingId, setEditingId] = useState(null);
  const [editDesc, setEditDesc] = useState('');
  const [editDetails, setEditDetails] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const startEdit = (entry) => {
    setEditingId(entry.id);
    setEditDesc(entry.work_description);
    setEditDetails(entry.work_details || '');
  };

  const saveEdit = async (id) => {
    try {
      await updateDailyWork(id, {
        work_description: editDesc,
        work_details: editDetails,
      });
      setEditingId(null);
      onRefresh();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update entry');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this activity entry?')) {
      try {
        await deleteDailyWork(id);
        onRefresh();
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to delete entry');
      }
    }
  };

  const handleSubmitAll = async () => {
    setSubmitting(true);
    try {
      // Mark all unsubmitted entries as submitted
      for (const entry of entries) {
        if (!entry.is_submitted) {
          await updateDailyWork(entry.id, { is_submitted: true });
        }
      }
      onRefresh();
    } catch (err) {
      alert('Failed to submit daily work');
    } finally {
      setSubmitting(false);
    }
  };

  if (!entries || entries.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200/80 p-8 text-center text-slate-400">
        <p className="text-sm font-medium">No work activities recorded for this date yet.</p>
        <p className="text-xs text-slate-400 mt-1">Use the form above to add your daily tasks, calls, or development activities.</p>
      </div>
    );
  }

  const allSubmitted = entries.every((e) => e.is_submitted);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Today's Logged Activities</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            {entries.length} {entries.length === 1 ? 'entry' : 'entries'} recorded
          </p>
        </div>

        {!allSubmitted ? (
          <button
            onClick={handleSubmitAll}
            disabled={submitting}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md shadow-emerald-600/20 disabled:opacity-50 transition-all"
          >
            <Send className="h-3.5 w-3.5" />
            {submitting ? 'Submitting...' : "Submit Day's Activities"}
          </button>
        ) : (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-800 text-xs font-bold rounded-full border border-emerald-200">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
            Submitted for Management Review
          </span>
        )}
      </div>

      <div className="space-y-3">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition-colors"
          >
            {editingId === entry.id ? (
              <div className="space-y-3">
                <input
                  type="text"
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm"
                />
                <textarea
                  rows={2}
                  value={editDetails}
                  onChange={(e) => setEditDetails(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm"
                />
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => setEditingId(null)}
                    className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-200 rounded-lg"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => saveEdit(entry.id)}
                    className="px-3 py-1.5 text-xs bg-solar-500 text-white font-bold rounded-lg"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-slate-900">{entry.work_description}</p>
                  {entry.work_details && (
                    <p className="text-xs text-slate-600 mt-1.5 whitespace-pre-line bg-white/80 p-2.5 rounded-lg border border-slate-200/50">
                      {entry.work_details}
                    </p>
                  )}
                  {(entry.start_time || entry.end_time) && (
                    <div className="flex items-center gap-1 text-[11px] font-medium text-slate-400 mt-2">
                      <Clock className="h-3 w-3" />
                      <span>
                        {entry.start_time || '--'} - {entry.end_time || '--'}
                      </span>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => startEdit(entry)}
                    title="Edit Activity"
                    className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-lg transition-colors"
                  >
                    <Edit3 className="h-3.5 w-3.5" />
                  </button>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    title="Delete Activity"
                    className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkEntryList;
