"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AlarmClock, ArrowLeft, CalendarPlus, CheckCircle2, ExternalLink, FileText, Mail, ShieldCheck, UserRound } from "lucide-react";
import { api, formatPlatform } from "@/lib/api";
import { Message } from "@/lib/types";
import { PriorityBadge } from "@/components/Badges";
import { ScoreGauge } from "@/components/ScoreGauge";
import { ErrorState, LoadingState } from "@/components/LoadingState";

export default function TriageDetailPage() {
  const {messageId}=useParams<{messageId:string}>();const router=useRouter();const[message,setMessage]=useState<Message|null>(null);const[error,setError]=useState(false);const[notice,setNotice]=useState("");
  useEffect(()=>{api<Message>(`/triage/${messageId}`).then(setMessage).catch(()=>setError(true));},[messageId]);
  const action=async(path:string,label:string)=>{await api(`/triage/${messageId}/${path}`,{method:"POST"});setNotice(label);};
  if(error)return <ErrorState message="This message could not be loaded from the triage API."/>;if(!message)return <LoadingState/>;
  const a=message.assessment;
  return <>
    <button onClick={()=>router.back()} className="mb-5 inline-flex items-center gap-2 text-xs font-semibold text-[#697075]"><ArrowLeft size={14}/> Back to queue</button>
    {notice&&<div className="mb-4 rounded-xl bg-[#e3f1e9] px-4 py-3 text-xs font-semibold text-moss">{notice}</div>}
    <div className="grid gap-5 xl:grid-cols-[1.15fr_.85fr]">
      <section className="panel overflow-hidden">
        <div className="border-b border-[#e4e1db] bg-[#faf9f6] p-6">
          <div className="flex flex-wrap items-center justify-between gap-3"><PriorityBadge priority={a.priority_level}/><span className="text-[10px] font-bold uppercase tracking-wider text-[#8a8f92]">{formatPlatform(message.platform)} · {message.account_label}</span></div>
          <h1 className="mt-5 text-2xl font-semibold tracking-[-.03em]">{message.subject||"Message from "+message.sender_name}</h1>
          <div className="mt-4 flex flex-wrap gap-5 text-xs text-[#747a7e]"><span className="inline-flex items-center gap-1.5"><UserRound size={14}/>{message.sender_name}</span><span className="inline-flex items-center gap-1.5"><Mail size={14}/>{message.sender_identifier}</span></div>
        </div>
        <div className="p-6"><div className="eyebrow">Original message</div><p className="mt-4 whitespace-pre-wrap text-[15px] leading-8 text-[#454d52]">{message.body_text}</p>{message.has_attachments&&<div className="mt-6 inline-flex items-center gap-2 rounded-xl border border-[#dedad2] bg-[#faf9f6] px-3 py-2 text-xs font-semibold"><FileText size={14}/> Attachment detected</div>}</div>
      </section>
      <aside className="space-y-5">
        <section className="panel p-6"><div className="flex items-center justify-between"><div><div className="eyebrow">Decision</div><h2 className="mt-2 text-lg font-semibold capitalize">{a.recommended_action.replaceAll("_"," ")}</h2></div><div className="grid size-11 place-items-center rounded-xl bg-[#fbe8e5] text-signal"><ShieldCheck size={19}/></div></div><p className="muted mt-4">{a.summary}</p></section>
        <section className="panel space-y-6 p-6"><ScoreGauge label="Urgency" value={a.urgency_score} color="#e64b3c"/><ScoreGauge label="Consequence risk" value={a.risk_score} color="#e79a34"/><ScoreGauge label="Action needed" value={a.action_score} color="#45836a"/><ScoreGauge label="Weighted priority" value={a.priority_score} color="#17212b"/></section>
        <section className="panel p-6"><div className="eyebrow">Why it surfaced</div><div className="mt-4 space-y-3">{a.reasons.map(reason=><div key={reason.reason_code} className="rounded-xl bg-[#f7f6f2] p-3"><div className="flex justify-between gap-3 text-xs font-semibold capitalize"><span>{reason.reason_code.replaceAll("_"," ")}</span><span className="text-signal">{reason.points>0?"+":""}{reason.points}</span></div><p className="mt-1 text-[11px] leading-5 text-[#7a8083]">{reason.explanation}</p></div>)}</div></section>
        <section className="panel p-4"><div className="grid gap-2 sm:grid-cols-2">
          <button onClick={()=>action("create-task","Task created and recorded in the audit log.")} className="button-primary inline-flex items-center justify-center gap-2"><CheckCircle2 size={14}/> Create task</button>
          <button onClick={()=>action("send-to-scheduling-review","Sent to TrustOps scheduling review.")} className="button-secondary inline-flex items-center justify-center gap-2"><CalendarPlus size={14}/> Scheduling review</button>
          <button className="button-secondary inline-flex items-center justify-center gap-2"><AlarmClock size={14}/> Snooze</button>
          <button onClick={()=>action("mark-safe","Marked safe; related notifications resolved.")} className="button-secondary inline-flex items-center justify-center gap-2"><ShieldCheck size={14}/> Mark safe</button>
        </div></section>
      </aside>
    </div>
  </>;
}

