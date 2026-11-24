import React from 'react';

const colorMap = {
  brand: 'bg-brand-500/10 text-brand-400 border-brand-500/20',
  emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
  rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
};

export const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'brand',
}) => {
  return (
    <div className="glass-card glass-card-hover p-5 rounded-2xl flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</span>
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center border ${colorMap[color]}`}>
          {Icon && <Icon className="w-5 h-5" />}
        </div>
      </div>
      <div className="mt-4">
        <div className="text-2xl font-black tracking-tight text-white">{value}</div>
        {subtitle && <div className="text-xs text-slate-400 mt-1">{subtitle}</div>}
      </div>
    </div>
  );
};

export default StatCard;
