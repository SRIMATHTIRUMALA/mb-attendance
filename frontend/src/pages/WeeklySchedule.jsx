import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { getDayName, formatDate } from '../utils/formatters';
import { Calendar, CheckCircle2, Clock, Info } from 'lucide-react';

export const WeeklySchedule = () => {
  const { user } = useAuth();
  const [schedules, setSchedules] = useState([]);
  const [holidays, setHolidays] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [schedRes, holRes] = await Promise.all([
          api.get('/schedules'),
          api.get('/schedules/holidays'),
        ]);
        setSchedules(schedRes.data);
        setHolidays(holRes.data);
      } catch (err) {
        console.error('Error fetching schedules:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const activeSchedule = schedules.length > 0 ? schedules[0] : null;
  const offDayName = activeSchedule ? getDayName(activeSchedule.weekly_off_day) : 'Sunday';

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-black text-slate-900">Weekly Shift & Schedule</h1>
        <p className="text-xs text-slate-500 mt-1">
          MB Solar Hub operates flexible weekly offs. Working days are computed from your assigned schedule.
        </p>
      </div>

      {/* Flexible Weekly Off Notice */}
      <div className="bg-gradient-to-r from-solar-500/10 via-amber-500/10 to-transparent p-6 rounded-2xl border border-solar-200">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-solar-500 text-white rounded-xl shadow-md shadow-amber-500/20">
            <Calendar className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900">
              Your Recurring Weekly Off Day: <span className="text-solar-700 text-base">{offDayName}</span>
            </h2>
            <p className="text-xs text-slate-600 mt-1 max-w-2xl leading-relaxed">
              At MB Solar Hub, Sunday is not an assumed universal holiday. Some team members work on Sundays and take offs on other days (e.g. Wednesday). You are only scheduled to work on your designated working days.
            </p>
          </div>
        </div>
      </div>

      {/* Week Grid */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
        <h3 className="text-sm font-bold text-slate-900 mb-4">Standard Weekly Schedule</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          {daysOfWeek.map((day, idx) => {
            const isOff = activeSchedule ? activeSchedule.weekly_off_day === idx : idx === 6;
            return (
              <div
                key={day}
                className={`p-4 rounded-xl border text-center ${
                  isOff
                    ? 'bg-sky-50 border-sky-200 text-sky-800'
                    : 'bg-slate-50 border-slate-200 text-slate-800'
                }`}
              >
                <p className="text-xs font-bold uppercase tracking-wider">{day.slice(0, 3)}</p>
                <p className="text-sm font-black mt-2">{isOff ? 'OFF' : 'WORK'}</p>
                <p className="text-[10px] text-slate-500 mt-1">
                  {isOff ? 'Weekly Off' : '9:00 AM - 6:00 PM'}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Company Holidays */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
        <h3 className="text-sm font-bold text-slate-900 mb-4">Official Company Holidays</h3>
        {holidays.length === 0 ? (
          <p className="text-xs text-slate-400">No upcoming company holidays scheduled.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {holidays.map((h) => (
              <div key={h.id} className="py-3 flex justify-between items-center text-xs">
                <span className="font-bold text-slate-800">{h.name}</span>
                <span className="text-slate-500">{formatDate(h.holiday_date)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default WeeklySchedule;
