"use client";

import { useEffect, useState } from "react";
import { Activity, BarChart3, CircleGauge, MessageSquareMore } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { MetricCard } from "@/components/MetricCard";
import { DistributionBars } from "@/components/DistributionBars";
import { ErrorState, LoadingState } from "@/components/LoadingState";

interface Summary {messages_analyzed:number;p0_alerts:number;p1_alerts:number;p2_digest:number;p3_low:number;action_needed_rate:number;average_priority_score:number}
interface Evaluation {total_messages:number;priority_accuracy:number;action_routing_accuracy:number;p0_precision:number;p0_recall:number;scheduling_routing_accuracy:number;newsletter_suppression_accuracy:number}

export default function AnalyticsPage() {
  const[data,setData]=useState<{summary:Summary;priority:{name:string;value:number}[];platforms:{name:string;value:number}[];reasons:{name:string;value:number}[];evaluation:Evaluation}|null>(null);const[error,setError]=useState(false);
  useEffect(()=>{Promise.all([api<Summary>("/analytics/summary"),api<{name:string;value:number}[]>("/analytics/priority-distribution"),api<{name:string;value:number}[]>("/analytics/platform-breakdown"),api<{name:string;value:number}[]>("/analytics/top-risk-reasons"),api<Evaluation>("/evaluation/latest")]).then(([summary,priority,platforms,reasons,evaluation])=>setData({summary,priority,platforms,reasons,evaluation})).catch(()=>setError(true));},[]);
  if(error)return <ErrorState/>;if(!data)return <LoadingState/>;
  return <>
    <PageHeader eyebrow="Reliability analytics" title="Measure attention quality." description="Portfolio-grade evaluation of routing accuracy, alert restraint, source coverage, and explainability."/>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><MetricCard label="Messages analyzed" value={data.summary.messages_analyzed} note="Synthetic evaluation set" icon={MessageSquareMore}/><MetricCard label="Priority accuracy" value={`${Math.round(data.evaluation.priority_accuracy*100)}%`} note="Expected vs actual tier" icon={CircleGauge} tone="green"/><MetricCard label="P0 recall" value={`${Math.round(data.evaluation.p0_recall*100)}%`} note="True urgent signals caught" icon={Activity} tone="red"/><MetricCard label="Action-needed rate" value={`${data.summary.action_needed_rate}%`} note="Explicit user asks" icon={BarChart3} tone="amber"/></div>
    <div className="mt-5 grid gap-5 lg:grid-cols-3"><div className="panel p-6"><h2 className="mb-6 font-semibold">Priority distribution</h2><DistributionBars data={data.priority}/></div><div className="panel p-6"><h2 className="mb-6 font-semibold">Platform breakdown</h2><DistributionBars data={data.platforms}/></div><div className="panel p-6"><h2 className="mb-6 font-semibold">Top risk reasons</h2><DistributionBars data={data.reasons.slice(0,6)}/></div></div>
    <div className="mt-5 panel p-6"><div className="eyebrow">Evaluation harness</div><div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">{[["Routing accuracy",data.evaluation.action_routing_accuracy],["P0 precision",data.evaluation.p0_precision],["P0 recall",data.evaluation.p0_recall],["Scheduling routing",data.evaluation.scheduling_routing_accuracy],["Newsletter suppression",data.evaluation.newsletter_suppression_accuracy]].map(([label,value])=><div key={String(label)} className="rounded-2xl bg-[#f7f6f2] p-4"><div className="text-2xl font-semibold">{Math.round(Number(value)*100)}%</div><div className="mt-1 text-xs text-[#7c8285]">{label}</div></div>)}</div></div>
  </>;
}

