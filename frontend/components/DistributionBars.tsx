const colors = ["#e64b3c", "#e79a34", "#557f93", "#a1a7a3", "#45836a", "#6a5d9f"];

export function DistributionBars({data, labelKey = "name", valueKey = "value"}: {data: Record<string, any>[]; labelKey?: string; valueKey?: string}) {
  const max = Math.max(...data.map(item => Number(item[valueKey])), 1);
  return <div className="space-y-4">{data.map((item, index) => (
    <div key={String(item[labelKey])}>
      <div className="mb-1.5 flex items-center justify-between text-xs"><span className="font-semibold capitalize">{String(item[labelKey]).replaceAll("_", " ").toLowerCase()}</span><span className="text-[#858a8d]">{item[valueKey]}</span></div>
      <div className="h-2 overflow-hidden rounded-full bg-[#eceae5]"><div className="h-full rounded-full" style={{width: `${Math.max(4, Number(item[valueKey]) / max * 100)}%`, background: colors[index % colors.length]}}/></div>
    </div>
  ))}</div>;
}

