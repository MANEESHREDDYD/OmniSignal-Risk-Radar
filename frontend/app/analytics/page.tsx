"use client";

import { useEffect, useState } from "react";
import { Activity, BarChart3, CircleGauge, MessageSquareMore } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { MetricCard } from "@/components/MetricCard";
import { DistributionBars } from "@/components/DistributionBars";
import { ErrorState, LoadingState } from "@/components/LoadingState";

interface Summary {messages_analyzed:number;p0_alerts:number;p1_alerts:number;p2_digest:number;p3_low:number;action_needed_rate:number;average_priority_score:number}
interface Evaluation {total_messages:number;labeled_count:number;ignored_unlabeled_count:number;priority_accuracy:number;action_routing_accuracy:number;p0_precision:number;p0_recall:number;reason_recall:number|null;scheduling_routing_accuracy:number;newsletter_suppression_accuracy:number}

export default function AnalyticsPage() {
  const[data,setData]=useState<{summary:Summary;priority:{name:string;value:number}[];platforms:{name:string;value:number}[];reasons:{name:string;value:number}[];evaluation:Evaluation}|null>(null);const[error,setError]=useState(false);
  useEffect(()=>{Promise.all([api<Summary>("/analytics/summary"),api<{name:string;value:number}[]>("/analytics/priority-distribution"),api<{name:string;value:number}[]>("/analytics/platform-breakdown"),api<{name:string;value:number}[]>("/analytics/top-risk-reasons"),api<Evaluation>("/evaluation/latest")]).then(([summary,priority,platforms,reasons,evaluation])=>setData({summary,priority,platforms,reasons,evaluation})).catch(()=>setError(true));},[]);
  if(error)return <ErrorState/>;if(!data)return <LoadingState/>;
  return <>
    <PageHeader eyebrow="Synthetic fixture analytics" title="Measure deterministic fixture conformance." description={`These metrics cover ${data.evaluation.labeled_count} labeled synthetic fixtures, not real-world inbox accuracy. ${data.evaluation.ignored_unlabeled_count} unlabeled record(s) were excluded.`}/>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><MetricCard label="Labeled fixtures" value={data.evaluation.labeled_count} note="Synthetic benchmark only" icon={MessageSquareMore}/><MetricCard label="Priority conformance" value={`${Math.round(data.evaluation.priority_accuracy*100)}%`} note="Expected vs actual fixture tier" icon={CircleGauge} tone="green"/><MetricCard label="P0 fixture recall" value={`${Math.round(data.evaluation.p0_recall*100)}%`} note="Within labeled fixtures only" icon={Activity} tone="red"/><MetricCard label="Action-needed rate" value={`${data.summary.action_needed_rate}%`} note="Stored message assessments" icon={BarChart3} tone="amber"/></div>
    <div className="mt-5 grid gap-5 lg:grid-cols-3"><div className="panel p-6"><h2 className="mb-6 font-semibold">Priority distribution</h2><DistributionBars data={data.priority}/></div><div className="panel p-6"><h2 className="mb-6 font-semibold">Platform breakdown</h2><DistributionBars data={data.platforms}/></div><div className="panel p-6"><h2 className="mb-6 font-semibold">Top risk reasons</h2><DistributionBars data={data.reasons.slice(0,6)}/></div></div>
    <div className="mt-5 panel p-6"><div className="eyebrow">Synthetic evaluation harness</div><div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-6">{[["Routing conformance",data.evaluation.action_routing_accuracy],["P0 precision",data.evaluation.p0_precision],["P0 recall",data.evaluation.p0_recall],["Reason recall",data.evaluation.reason_recall],["Scheduling routing",data.evaluation.scheduling_routing_accuracy],["Newsletter suppression",data.evaluation.newsletter_suppression_accuracy]].map(([label,value])=><div key={String(label)} className="rounded-2xl bg-[#f7f6f2] p-4"><div className="text-2xl font-semibold">{value===null?"N/A":`${Math.round(Number(value)*100)}%`}</div><div className="mt-1 text-xs text-[#7c8285]">{label}</div></div>)}</div><p className="mt-4 text-xs leading-5 text-[#7c8285]">The fixtures are repeated, hand-labeled scenarios designed to verify deterministic behavior. These percentages are not production accuracy claims.</p></div>
  </>;
}
