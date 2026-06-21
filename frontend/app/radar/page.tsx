"use client";

import { useEffect, useState } from "react";
import { Activity, AlertTriangle, CalendarClock, Clock3, RadioTower, ShieldAlert, Workflow } from "lucide-react";
import { api } from "@/lib/api";
import { Message } from "@/lib/types";
import { MetricCard } from "@/components/MetricCard";
import { PageHeader } from "@/components/PageHeader";
import { DistributionBars } from "@/components/DistributionBars";
import { MessageTable } from "@/components/MessageTable";
import { ErrorState, LoadingState } from "@/components/LoadingState";

interface Summary {immediate_alerts:number; attention_today:number; action_needed:number; scheduling_risks:number; security_finance_alerts:number; deadlines_soon:number; accounts_monitored:number; priority_distribution:Record<string,number>}

export default function RadarPage() {
  const [data, setData] = useState<{summary: Summary; reasons: {reason:string;count:number}[]; platforms:{platform:string;count:number}[]; messages:Message[]} | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {Promise.all([api<Summary>("/radar/summary"), api<{reason:string;count:number}[]>("/radar/by-reason"), api<{platform:string;count:number}[]>("/radar/by-platform"), api<Message[]>("/radar/high-risk")]).then(([summary,reasons,platforms,messages])=>setData({summary,reasons,platforms,messages})).catch(()=>setError(true));},[]);
  if (error) return <ErrorState/>;
  if (!data) return <LoadingState/>;
  return <>
    <PageHeader eyebrow="Risk radar" title="The shape of attention." description="A cross-platform view of urgency, consequence risk, and explicit user action—ranked before it becomes a missed commitment."/>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard label="Immediate" value={data.summary.immediate_alerts} note="P0 intervention" icon={ShieldAlert} tone="red"/>
      <MetricCard label="Attention today" value={data.summary.attention_today} note="P1 review queue" icon={Clock3} tone="amber"/>
      <MetricCard label="Scheduling risks" value={data.summary.scheduling_risks} note="Simulated review marker" icon={CalendarClock}/>
      <MetricCard label="Security + finance" value={data.summary.security_finance_alerts} note="High-consequence signals" icon={AlertTriangle} tone="red"/>
    </div>
    <div className="mt-5 grid gap-5 lg:grid-cols-3">
      <div className="panel p-6 lg:col-span-2"><div className="flex items-center gap-2"><Activity size={17}/><h2 className="font-semibold">Top detected reasons</h2></div><div className="mt-6"><DistributionBars data={data.reasons.slice(0,8)} labelKey="reason" valueKey="count"/></div></div>
      <div className="panel p-6"><div className="flex items-center gap-2"><RadioTower size={17}/><h2 className="font-semibold">Source coverage</h2></div><div className="mt-6"><DistributionBars data={data.platforms} labelKey="platform" valueKey="count"/></div><div className="mt-6 flex items-start gap-3 rounded-2xl bg-[#edf2ef] p-4"><Workflow size={18} className="mt-0.5 text-moss"/><p className="text-xs leading-5 text-[#52615a]">All sources feed one normalized scoring contract, so adding a future OAuth connector does not change the decision layer.</p></div></div>
    </div>
    <div className="mb-4 mt-8"><div className="eyebrow">Escalated signals</div><h2 className="mt-2 text-xl font-semibold">High-risk message queue</h2></div>
    <MessageTable messages={data.messages}/>
  </>;
}
