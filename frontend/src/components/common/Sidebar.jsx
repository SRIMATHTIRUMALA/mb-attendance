import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard,
  Clock,
  Briefcase,
  Calendar,
  FileText,
  Users,
  Settings,
  ShieldCheck,
  ClipboardList
} from 'lucide-react';

export const Sidebar = () => {
  const { user, isAdmin } = useAuth();

  const employeeLinks = [
    { to: '/', label: 'My Dashboard', icon: LayoutDashboard },
    { to: '/work', label: 'Daily Work', icon: Briefcase },
    { to: '/attendance-history', label: 'Attendance History', icon: Clock },
    { to: '/schedule', label: 'Weekly Schedule', icon: Calendar },
    { to: '/requests', label: 'Leave & Corrections', icon: FileText },
  ];

  const adminLinks = [
    { to: '/admin', label: 'Admin Overview', icon: ShieldCheck },
    { to: '/admin/employees', label: 'Employee Management', icon: Users },
    { to: '/admin/attendance', label: 'Attendance Review', icon: Clock },
    { to: '/admin/reports', label: 'Work & Activity Reports', icon: ClipboardList },
    { to: '/admin/settings', label: 'System Settings', icon: Settings },
  ];

  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
      isActive
        ? 'bg-solar-500 text-white shadow-md shadow-amber-500/25'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
    }`;

  return (
    <aside className="w-64 bg-white border-r border-slate-200/80 flex flex-col h-screen sticky top-0">
      <div className="p-5 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <div className="h-8 w-2 bg-solar-500 rounded-full" />
          <span className="text-xs font-black uppercase tracking-wider text-slate-400">Navigation</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {isAdmin && (
          <div>
            <p className="px-3 mb-2 text-[11px] font-bold uppercase tracking-wider text-solar-700">
              Management (Sir)
            </p>
            <nav className="space-y-1">
              {adminLinks.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink key={item.to} to={item.to} end={item.to === '/admin'} className={linkClass}>
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </nav>
          </div>
        )}

        <div>
          <p className="px-3 mb-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            {isAdmin ? 'Employee Operations View' : 'Employee Portal'}
          </p>
          <nav className="space-y-1">
            {employeeLinks.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink key={item.to} to={item.to} end={item.to === '/'} className={linkClass}>
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-slate-200 text-slate-700 font-bold flex items-center justify-center text-sm">
            {user?.full_name ? user.full_name[0] : 'U'}
          </div>
          <div className="overflow-hidden">
            <p className="text-xs font-bold text-slate-900 truncate">{user?.full_name}</p>
            <p className="text-[11px] text-slate-500 truncate">{user?.designation}</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
