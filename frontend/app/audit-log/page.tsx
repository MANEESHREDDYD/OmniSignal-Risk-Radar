"use client";

import { useEffect, useState } from "react";
import { FileClock, Search } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState, LoadingState } from "@/components/LoadingState";

interface Audit {id:string;actor:string;action:string;target_type:string;target_id:string;after:Record<string,unknown>|null;created_at:string}

export default function AuditLogPage() {
  const[items,setItems]=useState<Audit[]|null>(null);const[error,setError]=useState(false);useEffect(()=>{api<Audit[]>("/audit").then(setItems).catch(()=>setError(true));},[]);
  if(error)return <ErrorState/>;if(!items)return <LoadingState/>;
  return <>
    <PageHeader eyebrow="Trust & traceability" title="Every decision leaves a trail." description="System analysis, notification routing, and user interventions are recorded for review and future tuning."
      action={<div className="inline-flex items-center gap-2 text-xs font-semibold"><FileClock size={15}/>{items.length} recent events</div>}/>
    <div className="mb-4 flex justify-end"><label className="relative"><Search size={14} className="absolute left-3 top-3.5 text-[#969a9d]"/><input className="input w-64 pl-9" placeholder="Search audit events"/></label></div>
    <div className="panel overflow-hidden"><div className="overflow-x-auto"><table className="w-full min-w-[780px] text-left"><thead><tr className="border-b border-[#e4e1da] bg-[#faf9f6] text-[10px] uppercase tracking-wider text-[#858a8d]"><th className="px-5 py-3.5">Time</th><th className="px-3 py-3.5">Actor</th><th className="px-3 py-3.5">Action</th><th className="px-3 py-3.5">Target</th><th className="px-5 py-3.5">Result</th></tr></thead><tbody>{items.map(item=><tr key={item.id} className="border-b border-[#ece9e3] last:border-0"><td className="whitespace-nowrap px-5 py-4 text-xs text-[#818689]">{new Date(item.created_at).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</td><td className="px-3 py-4 text-xs font-semibold">{item.actor}</td><td className="px-3 py-4 text-sm">{item.action}</td><td className="px-3 py-4"><span className="rounded-lg bg-[#f0efeb] px-2 py-1 font-mono text-[10px]">{item.target_id}</span></td><td className="max-w-[320px] truncate px-5 py-4 text-xs text-[#777d80]">{item.after?JSON.stringify(item.after):"Recorded"}</td></tr>)}</tbody></table></div></div>
  </>;
}
