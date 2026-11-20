import React from 'react';
import { Sun } from 'lucide-react';

export const Logo = ({ size = 'default', showSubtitle = true }) => {
  const isLarge = size === 'large';
  return (
    <div className="flex items-center gap-3">
      <div className={`rounded-xl bg-gradient-to-tr from-solar-500 to-amber-300 p-2 text-white shadow-md shadow-amber-500/20 flex items-center justify-center ${isLarge ? 'h-12 w-12' : 'h-10 w-10'}`}>
        <Sun className={isLarge ? 'h-7 w-7' : 'h-6 w-6'} strokeWidth={2.5} />
      </div>
      <div>
        <div className={`font-black tracking-wider text-slate-900 ${isLarge ? 'text-2xl' : 'text-lg'}`}>
          MB SOLAR <span className="text-solar-600">HUB</span>
        </div>
        {showSubtitle && (
          <div className="text-[11px] font-medium tracking-tight text-slate-500 uppercase">
            Attendance & Work System
          </div>
        )}
      </div>
    </div>
  );
};

export default Logo;
