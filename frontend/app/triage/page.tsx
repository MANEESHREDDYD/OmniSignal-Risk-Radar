"use client";

import { useEffect, useState } from "react";
import { ListChecks } from "lucide-react";
import { api } from "@/lib/api";
import { Message } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { MessageTable } from "@/components/MessageTable";
import { ErrorState, LoadingState } from "@/components/LoadingState";

export default function TriagePage() {
  const [messages,setMessages]=useState<Message[]|null>(null);const[error,setError]=useState(false);
  useEffect(()=>{api<Message[]>("/triage").then(setMessages).catch(()=>setError(true));},[]);
  if(error)return <ErrorState/>;if(!messages)return <LoadingState/>;
  return <>
    <PageHeader eyebrow="Human review queue" title="Resolve the signal, not the inbox." description="P0 and P1 messages arrive here with enough context to decide quickly and safely."
      action={<div className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-xs font-semibold shadow-sm"><ListChecks size={15}/>{messages.length} items</div>}/>
    <div className="mb-4 rounded-2xl border border-[#ddd8cf] bg-white p-4 text-xs leading-5 text-[#686f73]"><strong className="text-ink">Triage principle:</strong> OmniSignal recommends; you decide. Every user correction becomes an audit event and can later inform personal rules.</div>
    <MessageTable messages={messages}/>
  </>;
}

