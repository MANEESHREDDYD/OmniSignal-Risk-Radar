"use client";

import { useEffect, useState } from "react";
import { Plus, SlidersHorizontal, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState, LoadingState } from "@/components/LoadingState";

interface Rule {id:string;rule_name:string;rule_type:string;conditions:Record<string,string>;action:Record<string,string>;is_enabled:boolean}

export default function RulesPage() {
  const [rules,setRules]=useState<Rule[]|null>(null);const[error,setError]=useState(false);
  const load=()=>api<Rule[]>("/rules").then(setRules).catch(()=>setError(true)); useEffect(()=>{load();},[]);
  const toggle=async(rule:Rule)=>{await api(`/rules/${rule.id}`,{method:"PATCH",body:JSON.stringify({...rule,is_enabled:!rule.is_enabled})});load();};
  const remove=async(id:string)=>{await api(`/rules/${id}`,{method:"DELETE"});load();};
  const add=async()=>{await api("/rules",{method:"POST",body:JSON.stringify({rule_name:"VIP sender requires review",rule_type:"sender",conditions:{sender_type:"vip"},action:{minimum_priority:"P1_TODAY"},is_enabled:true})});load();};
  if(error)return <ErrorState/>;if(!rules)return <LoadingState/>;
  return <>
    <PageHeader eyebrow="Attention policy" title="You decide what breaks through." description="Rules shape interruption thresholds while preserving the underlying deterministic score and audit record."
      action={<button onClick={add} className="button-primary inline-flex items-center gap-2"><Plus size={15}/> Add rule</button>}/>
    <div className="panel overflow-hidden">
      {rules.map((rule,index)=><div key={rule.id} className={`flex flex-col gap-4 p-5 md:flex-row md:items-center ${index<rules.length-1?"border-b border-[#e7e4de]":""}`}>
        <div className="grid size-10 shrink-0 place-items-center rounded-xl bg-[#eff1f1]"><SlidersHorizontal size={16}/></div>
        <div className="min-w-0 flex-1"><div className="text-sm font-semibold">{rule.rule_name}</div><div className="mt-1 truncate text-xs text-[#858a8d]">{rule.rule_type} · If {JSON.stringify(rule.conditions)} → {JSON.stringify(rule.action)}</div></div>
        <button onClick={()=>toggle(rule)} className={`relative h-7 w-12 rounded-full transition ${rule.is_enabled?"bg-moss":"bg-[#d6d7d5]"}`}><span className={`absolute top-1 size-5 rounded-full bg-white shadow transition ${rule.is_enabled?"left-6":"left-1"}`}/></button>
        <button onClick={()=>remove(rule.id)} className="grid size-9 place-items-center rounded-lg text-[#9a9e9f] hover:bg-[#fbe8e5] hover:text-signal"><Trash2 size={15}/></button>
      </div>)}
    </div>
  </>;
}
