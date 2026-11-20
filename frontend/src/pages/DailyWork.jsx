import React, { useState, useEffect } from 'react';
import { getDailyWork } from '../services/work';
import WorkEntryForm from '../components/work/WorkEntryForm';
import WorkEntryList from '../components/work/WorkEntryList';
import { Calendar, Info } from 'lucide-react';

export const DailyWork = () => {
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadEntries = async (dateVal) => {
    setLoading(true);
    try {
      const data = await getDailyWork({ work_date: dateVal });
      setEntries(data);
    } catch (err) {
      console.error('Error loading daily work:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEntries(selectedDate);
  }, [selectedDate]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-black text-slate-900">Daily Work & Activity Log</h1>
          <p className="text-xs text-slate-500 mt-1">
            Log your daily calls, client follow-ups, or technical activities without separate Excel sheets.
          </p>
        </div>

        {/* Date Selector */}
        <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-slate-200">
          <Calendar className="h-4 w-4 text-solar-600" />
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="text-xs font-bold text-slate-700 bg-transparent focus:outline-none"
          />
        </div>
      </div>

      <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200/80 text-xs text-amber-900 flex items-start gap-2.5">
        <Info className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-bold">Flexible Daily Activities</p>
          <p className="mt-0.5 text-amber-800">
            Enter your tasks for the day (e.g. <i>"Contacted solar vendors regarding MB Solar Hub registration - 24 calls made, 7 interested, 5 follow-ups required"</i> or <i>"Developed and tested website chatbot"</i>). You can add multiple tasks per day.
          </p>
        </div>
      </div>

      <WorkEntryForm
        defaultDate={selectedDate}
        onEntryAdded={() => loadEntries(selectedDate)}
      />

      {loading ? (
        <div className="p-8 text-center text-slate-400 text-xs">Loading activities...</div>
      ) : (
        <WorkEntryList
          entries={entries}
          onRefresh={() => loadEntries(selectedDate)}
        />
      )}
    </div>
  );
};

export default DailyWork;
