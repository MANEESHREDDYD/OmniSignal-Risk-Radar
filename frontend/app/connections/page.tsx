"use client";

import { useEffect, useState } from "react";
import { CalendarDays, Check, Mail, MessageSquareText, RefreshCw, ShieldCheck } from "lucide-react";
import { api, formatPlatform } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState, LoadingState } from "@/components/LoadingState";

interface Account {id:string;platform:string;account_label:string;account_identifier:string;connection_status:string;last_sync_at:string;messages_synced:number;is_demo:boolean}

const iconFor = (platform:string) => platform === "calendar" ? CalendarDays : ["sms","imessage"].includes(platform) ? MessageSquareText : Mail;

export default function ConnectionsPage() {
  const [accounts,setAccounts]=useState<Account[]|null>(null); const [error,setError]=useState(false); const [syncing,setSyncing]=useState<string|null>(null);
  const load=()=>api<Account[]>("/connections").then(setAccounts).catch(()=>setError(true));
  useEffect(()=>{load();},[]);
  const sync=async(id:string)=>{setSyncing(id);await api(`/connections/${id}/sync`,{method:"POST"});await load();setSyncing(null);};
  if(error)return <ErrorState/>; if(!accounts)return <LoadingState/>;
  const demoAccounts=accounts.filter(account=>account.is_demo);
  return <>
    <PageHeader eyebrow="Synthetic connector demo" title={`${demoAccounts.length} demo accounts. Zero credentials.`} description="These cards use local fixtures. Optional read-only Google setup lives under Integrations and has not been live-validated in this repository."
      action={<div className="inline-flex items-center gap-2 rounded-xl bg-[#e5f2eb] px-4 py-2.5 text-xs font-semibold text-moss"><ShieldCheck size={15}/> Demo mode protected</div>}/>
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {demoAccounts.map(account=>{const Icon=iconFor(account.platform);return <div key={account.id} className="panel p-5">
        <div className="flex items-start justify-between"><div className="grid size-11 place-items-center rounded-xl bg-[#eff1f1]"><Icon size={19}/></div><span className="inline-flex items-center gap-1 rounded-full bg-[#e3f1e9] px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-moss"><Check size={11}/> Connected</span></div>
        <div className="mt-5 text-base font-semibold">{account.account_label}</div><div className="mt-1 text-xs text-[#858a8d]">{account.account_identifier}</div>
        <div className="my-5 grid grid-cols-2 gap-3 rounded-2xl bg-[#f7f6f2] p-4"><div><div className="eyebrow">Platform</div><div className="mt-1 text-xs font-semibold">{formatPlatform(account.platform)}</div></div><div><div className="eyebrow">Messages</div><div className="mt-1 text-xs font-semibold">{account.messages_synced} synced</div></div></div>
        <button disabled={syncing===account.id} onClick={()=>sync(account.id)} className="button-secondary flex w-full items-center justify-center gap-2"><RefreshCw size={14} className={syncing===account.id?"animate-spin":""}/>{syncing===account.id?"Syncing…":"Sync demo data"}</button>
      </div>})}
    </div>
    <div className="mt-5 rounded-2xl border border-dashed border-[#cfcac0] p-5"><div className="text-sm font-semibold">Connector status</div><p className="muted mt-1">Gmail and Google Calendar have an optional read-only foundation under Integrations, tested with mocks only. Microsoft Graph, Slack, Teams, SMS, and real iMessage connectors are not implemented.</p></div>
  </>;
}
