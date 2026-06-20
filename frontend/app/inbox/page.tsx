"use client";

import { useEffect, useMemo, useState } from "react";
import { Filter, Search } from "lucide-react";
import { api } from "@/lib/api";
import { Message, Priority } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { MessageTable } from "@/components/MessageTable";
import { ErrorState, LoadingState } from "@/components/LoadingState";

const filters: {label:string; value:"ALL"|Priority|"ACTION"}[] = [
  {label:"All signals",value:"ALL"},{label:"P0 immediate",value:"P0_IMMEDIATE"},{label:"P1 today",value:"P1_TODAY"},{label:"Action needed",value:"ACTION"},{label:"Digest",value:"P2_DIGEST"},{label:"Low",value:"P3_LOW"}
];

export default function InboxPage() {
  const [messages,setMessages] = useState<Message[]|null>(null); const [error,setError]=useState(false); const [filter,setFilter]=useState<(typeof filters)[number]["value"]>("ALL"); const [search,setSearch]=useState("");
  useEffect(()=>{api<Message[]>("/inbox").then(setMessages).catch(()=>setError(true));},[]);
  const visible=useMemo(()=>messages?.filter(m=>(filter==="ALL"||filter==="ACTION"&&m.assessment.action_score>=30||m.assessment.priority_level===filter)&&(`${m.sender_name} ${m.subject} ${m.body_text}`.toLowerCase().includes(search.toLowerCase())))||[],[messages,filter,search]);
  if(error)return <ErrorState/>; if(!messages)return <LoadingState/>;
  return <>
    <PageHeader eyebrow="Unified inbox" title="Every channel. One decision layer." description="Gmail, Outlook, SMS, iMessage, and calendar alerts normalized into a single explainable queue."/>
    <div className="mb-4 flex flex-col justify-between gap-3 xl:flex-row">
      <div className="flex flex-wrap gap-2">{filters.map(item=><button key={item.value} onClick={()=>setFilter(item.value)} className={`rounded-xl px-3.5 py-2 text-xs font-semibold transition ${filter===item.value?"bg-ink text-white":"border border-[#dcd8d0] bg-white text-[#697075] hover:bg-[#faf9f6]"}`}>{item.label}</button>)}</div>
      <div className="flex gap-2"><label className="relative"><Search size={15} className="absolute left-3 top-3.5 text-[#959a9d]"/><input value={search} onChange={e=>setSearch(e.target.value)} className="input w-64 pl-9" placeholder="Search sender or signal"/></label><button className="button-secondary inline-flex items-center gap-2"><Filter size={14}/> Filters</button></div>
    </div>
    <div className="mb-3 text-xs text-[#858a8d]">{visible.length} messages shown</div>
    <MessageTable messages={visible}/>
  </>;
}
