import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Logo } from './Logo';
import { LogOut, Clock, UserCheck } from 'lucide-react';

export const Navbar = () => {
  const { user, isAdmin, logout } = useAuth();
  const [istTime, setIstTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      // Format to IST
      const timeStr = now.toLocaleTimeString('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      });
      setIstTime(timeStr);
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-6 flex items-center justify-between sticky top-0 z-30">
      <Logo size="default" />

      <div className="flex items-center gap-6">
        {/* Live IST Clock */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-semibold">
          <Clock className="h-3.5 w-3.5 text-solar-600" />
          <span>{istTime || 'Loading...'} IST</span>
        </div>

        {/* User Role Tag */}
        <div className="flex items-center gap-3">
          <span
            className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
              isAdmin
                ? 'bg-amber-100 text-amber-800 border border-amber-300'
                : 'bg-slate-100 text-slate-700'
            }`}
          >
            {isAdmin ? 'Admin (Sir)' : user?.employee_id || 'Employee'}
          </span>

          <button
            onClick={logout}
            title="Log Out"
            className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-rose-600 hover:bg-rose-50 px-2.5 py-1.5 rounded-lg transition-colors"
          >
            <LogOut className="h-4 w-4" />
            <span className="hidden md:inline">Sign Out</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
