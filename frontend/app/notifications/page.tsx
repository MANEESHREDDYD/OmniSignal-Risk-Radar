"use client";

import { useEffect, useState } from "react";
import { BellRing } from "lucide-react";
import { api } from "@/lib/api";
import { Notification } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { NotificationCard } from "@/components/NotificationCard";
import { ErrorState, LoadingState } from "@/components/LoadingState";

export default function NotificationsPage() {
  const [items,setItems]=useState<Notification[]|null>(null); const [error,setError]=useState(false);
  const load=()=>api<Notification[]>("/notifications").then(setItems).catch(()=>setError(true));
  useEffect(()=>{load();},[]);
  const act=async(id:string,action:"snooze"|"dismiss"|"resolve")=>{await api(`/notifications/${id}/${action}`,{method:"POST",body:action==="snooze"?"{}":undefined});await load();};
  if(error)return <ErrorState/>; if(!items)return <LoadingState/>;
  const sections=[{key:"P0_IMMEDIATE",title:"Immediate action needed",copy:"High-consequence signals that should interrupt the current workflow."},{key:"P1_TODAY",title:"Needs attention today",copy:"Important, but safe to handle in a focused review block."},{key:"P2_DIGEST",title:"Digest",copy:"Useful context without interruption cost."}];
  return <>
    <PageHeader eyebrow="Notification center" title="Interruptions with a reason." description="Every alert carries its source, score, route, and explanation. Snooze, dismiss, or resolve without losing traceability."
      action={<div className="inline-flex items-center gap-2 text-xs font-semibold"><BellRing size={15}/>{items.filter(i=>i.status==="delivered").length} active</div>}/>
    {sections.map(section=>{const subset=items.filter(i=>i.priority_level===section.key&&i.status==="delivered");if(!subset.length)return null;return <section key={section.key} className="mb-8"><div className="mb-4"><h2 className="text-lg font-semibold">{section.title} <span className="ml-2 text-xs font-normal text-[#8a8f92]">{subset.length}</span></h2><p className="mt-1 text-xs text-[#858a8d]">{section.copy}</p></div><div className="space-y-3">{subset.map(item=><NotificationCard key={item.id} item={item} onAction={act}/>)}</div></section>})}
    <section><h2 className="mb-4 text-lg font-semibold">Snoozed & resolved</h2><div className="space-y-3">{items.filter(i=>i.status!=="delivered").slice(0,8).map(item=><NotificationCard key={item.id} item={item}/>)}</div></section>
  </>;
}

