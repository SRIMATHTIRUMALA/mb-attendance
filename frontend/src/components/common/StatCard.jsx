import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, color = 'amber' }) => {
  const colorMap = {
    amber: 'bg-amber-500/10 text-amber-600 border-amber-100',
    emerald: 'bg-emerald-500/10 text-emerald-600 border-emerald-100',
    sky: 'bg-sky-500/10 text-sky-600 border-sky-100',
    rose: 'bg-rose-500/10 text-rose-600 border-rose-100',
    purple: 'bg-purple-500/10 text-purple-600 border-purple-100',
    slate: 'bg-slate-500/10 text-slate-600 border-slate-100',
  };

  const currentStyle = colorMap[color] || colorMap.amber;

  return (
    <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-sm hover:shadow transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl border ${currentStyle}`}>
            <Icon className="h-6 w-6" />
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard;
