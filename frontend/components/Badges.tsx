import { AlertTriangle, ArrowDown, ArrowUp, Circle, Zap } from "lucide-react";
import { Priority } from "@/lib/types";

const styles: Record<Priority, string> = {
  P0_IMMEDIATE: "bg-[#fbe8e5] text-[#c53d31] border-[#f1c7c1]",
  P1_TODAY: "bg-[#fff1dc] text-[#a96714] border-[#eed5ad]",
  P2_DIGEST: "bg-[#e8f0f5] text-[#4c7185] border-[#cfdee7]",
  P3_LOW: "bg-[#eeefed] text-[#717774] border-[#dfe1de]",
};
const labels: Record<Priority, string> = {P0_IMMEDIATE: "P0 Immediate", P1_TODAY: "P1 Today", P2_DIGEST: "P2 Digest", P3_LOW: "P3 Low"};

export function PriorityBadge({priority}: {priority: Priority}) {
  return <span className={`inline-flex whitespace-nowrap rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide ${styles[priority]}`}>{labels[priority]}</span>;
}

export function ScorePill({value, kind}: {value: number; kind: "urgency" | "risk" | "action"}) {
  const Icon = kind === "urgency" ? Zap : kind === "risk" ? AlertTriangle : Circle;
  const color = value >= 70 ? "text-signal" : value >= 40 ? "text-amber" : "text-moss";
  return <span className={`inline-flex items-center gap-1 text-xs font-bold ${color}`}><Icon size={12}/>{value}</span>;
}

export function Delta({value}: {value: number}) {
  const positive = value >= 0;
  return <span className={`inline-flex items-center gap-0.5 text-[11px] font-semibold ${positive ? "text-signal" : "text-moss"}`}>{positive ? <ArrowUp size={11}/> : <ArrowDown size={11}/>} {Math.abs(value)}%</span>;
}

