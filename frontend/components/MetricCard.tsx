import { LucideIcon } from "lucide-react";

export function MetricCard({label, value, note, icon: Icon, tone = "ink"}: {label: string; value: string | number; note: string; icon: LucideIcon; tone?: "ink" | "red" | "amber" | "green"}) {
  const tones = {
    ink: "bg-[#edf0f1] text-ink",
    red: "bg-[#fbe8e5] text-signal",
    amber: "bg-[#fff0da] text-[#b47118]",
    green: "bg-[#e3f1e9] text-moss",
  };
  return (
    <div className="panel p-5">
      <div className={`mb-5 grid size-10 place-items-center rounded-xl ${tones[tone]}`}><Icon size={18}/></div>
      <div className="text-3xl font-semibold tracking-[-.04em]">{value}</div>
      <div className="mt-1 text-sm font-semibold">{label}</div>
      <div className="mt-2 text-xs text-[#858a8d]">{note}</div>
    </div>
  );
}

