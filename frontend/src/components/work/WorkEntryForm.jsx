import React, { useState } from 'react';
import { PlusCircle, Save, Check } from 'lucide-react';
import { createDailyWork } from '../../services/work';

export const WorkEntryForm = ({ onEntryAdded, defaultDate }) => {
  const [description, setDescription] = useState('');
  const [details, setDetails] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) {
      setError('Please provide a work activity description.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await createDailyWork({
        work_date: defaultDate || new Date().toISOString().split('T')[0],
        work_description: description.trim(),
        work_details: details.trim() || null,
        start_time: startTime || null,
        end_time: endTime || null,
        is_submitted: false, // Initial draft
      });

      setDescription('');
      setDetails('');
      setStartTime('');
      setEndTime('');
      onEntryAdded();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save daily work entry.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 mb-6">
      <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
        <PlusCircle className="h-5 w-5 text-solar-600" />
        Log Activity / Work Item
      </h3>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
            Work Description *
          </label>
          <input
            type="text"
            required
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g. Contacted solar vendors regarding MB Solar Hub registration, or Developed website chatbot..."
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/30 focus:border-amber-500"
          />
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
            Work Details / Feedback / Metrics (Optional)
          </label>
          <textarea
            rows={2}
            value={details}
            onChange={(e) => setDetails(e.target.value)}
            placeholder="e.g. 24 calls made, 7 interested, 5 follow-ups required. Discussed registration process..."
            className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/30 focus:border-amber-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
              Start Time (Optional)
            </label>
            <input
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/30 focus:border-amber-500"
            />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
              End Time (Optional)
            </label>
            <input
              type="time"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/30 focus:border-amber-500"
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-solar-500 hover:bg-solar-600 text-white font-bold text-sm shadow-md shadow-amber-500/20 disabled:opacity-50 transition-all"
          >
            <Save className="h-4 w-4" />
            {loading ? 'Saving...' : 'Add Activity'}
          </button>
        </div>
      </div>
    </form>
  );
};

export default WorkEntryForm;
