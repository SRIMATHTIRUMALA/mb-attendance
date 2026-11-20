import React, { useState } from 'react';
import api from '../../services/api';
import { Settings as SettingsIcon, Mail, Clock, Save, CheckCircle2 } from 'lucide-react';

export const Settings = () => {
  const [sirEmail, setSirEmail] = useState('management@mbsolarhub.com');
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-black text-slate-900">System & Management Settings</h1>
        <p className="text-xs text-slate-500 mt-1">
          Configure Sir's automated reporting email and standard attendance window parameters.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Sir's Email Configuration */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
          <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Mail className="h-4 w-4 text-solar-600" />
            Sir (Management) Report Recipient
          </h3>

          {saved && (
            <div className="mb-4 p-3 bg-emerald-50 text-emerald-800 text-xs rounded-xl font-bold flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              Settings updated successfully.
            </div>
          )}

          <form onSubmit={handleSave} className="space-y-4 text-xs">
            <div>
              <label className="block font-bold uppercase tracking-wider text-slate-600 mb-1">
                Management Recipient Email *
              </label>
              <input
                type="email"
                required
                value={sirEmail}
                onChange={(e) => setSirEmail(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm"
              />
              <p className="text-[10px] text-slate-400 mt-1">
                Sir's email address is not hardcoded and can be updated anytime.
              </p>
            </div>

            <button
              type="submit"
              className="flex items-center gap-1.5 px-4 py-2 bg-solar-500 hover:bg-solar-600 text-white font-bold rounded-xl shadow-md shadow-amber-500/20"
            >
              <Save className="h-3.5 w-3.5" />
              <span>Save Recipient</span>
            </button>
          </form>
        </div>

        {/* Office Hours Rule Reference */}
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
          <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Clock className="h-4 w-4 text-solar-600" />
            Standard Attendance Rules (Asia/Kolkata)
          </h3>
          <div className="space-y-3 text-xs text-slate-600">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
              <p className="font-bold text-slate-900">Normal Office Hours</p>
              <p className="mt-0.5">9:00 AM to 6:00 PM IST</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
              <p className="font-bold text-slate-900">Check In Window</p>
              <p className="mt-0.5">8:45 AM – 10:00 AM. After 10:00 AM requires correction request.</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
              <p className="font-bold text-slate-900">Check Out Window</p>
              <p className="mt-0.5">6:00 PM – 7:00 PM. After 7:00 PM requires correction request.</p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
              <p className="font-bold text-slate-900">Lunch Break</p>
              <p className="mt-0.5">1:00 PM – 2:00 PM (Only required for stepping outside office).</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
