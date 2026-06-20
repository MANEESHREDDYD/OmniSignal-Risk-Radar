export function ScoreGauge({label, value, color}: {label: string; value: number; color: string}) {
  return <div>
    <div className="mb-2 flex items-end justify-between"><span className="text-xs font-semibold">{label}</span><span className="text-xl font-semibold">{value}<span className="text-[10px] text-[#929699]">/100</span></span></div>
    <div className="h-2.5 overflow-hidden rounded-full bg-[#ebe9e4]"><div className="h-full rounded-full transition-all" style={{width: `${value}%`, background: color}}/></div>
  </div>;
}
