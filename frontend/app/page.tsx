"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, BellRing, CalendarClock, ChevronRight, CircleCheckBig, ShieldAlert, Sparkles, Zap } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Message, Notification } from "@/lib/types";
import { MetricCard } from "@/components/MetricCard";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState, LoadingState } from "@/components/LoadingState";
import { MessageTable } from "@/components/MessageTable";
import { DistributionBars } from "@/components/DistributionBars";

interface Summary {
  immediate_alerts: number; attention_today: number; action_needed: number; scheduling_risks: number;
  security_finance_alerts: number; deadlines_soon: number; accounts_monitored: number; messages_analyzed: number;
  priority_distribution: Record<string, number>;
}

export default function Home() {
  const [data, setData] = useState<{summary: Summary; messages: Message[]; notifications: Notification[]} | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    Promise.all([api<Summary>("/radar/summary"), api<Message[]>("/radar/high-risk"), api<Notification[]>("/notifications")])
      .then(([summary, messages, notifications]) => setData({summary, messages, notifications}))
      .catch(() => setError(true));
  }, []);
  if (error) return <ErrorState/>;
  if (!data) return <LoadingState/>;
  const distribution = Object.entries(data.summary.priority_distribution).map(([name, value]) => ({name, value}));
  const top = data.notifications.filter(n => n.status === "delivered").slice(0, 3);

  return <>
    <PageHeader eyebrow="Executive attention layer" title="Good morning, Maneesh." description={`OmniSignal analyzed ${data.summary.messages_analyzed} messages across ${data.summary.accounts_monitored} demo accounts. Here is what deserves your attention.`}
      action={<Link href="/triage" className="button-primary inline-flex items-center gap-2"><Sparkles size={15}/> Start triage</Link>}/>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard label="Immediate alerts" value={data.summary.immediate_alerts} note="Interrupt-worthy signals" icon={ShieldAlert} tone="red"/>
      <MetricCard label="Needs attention today" value={data.summary.attention_today} note="Before the day closes" icon={BellRing} tone="amber"/>
      <MetricCard label="Action needed" value={data.summary.action_needed} note="Explicit asks detected" icon={CircleCheckBig} tone="green"/>
      <MetricCard label="Scheduling risks" value={data.summary.scheduling_risks} note="Ambiguity or conflict" icon={CalendarClock}/>
    </div>
    <div className="mt-5 grid gap-5 xl:grid-cols-[1.55fr_.8fr]">
      <section className="panel p-6">
        <div className="mb-6 flex items-start justify-between"><div><div className="eyebrow">Live attention queue</div><h2 className="mt-2 text-xl font-semibold tracking-tight">Why the radar is lit</h2></div><Link href="/notifications" className="text-xs font-semibold text-signal">View all</Link></div>
        <div className="space-y-3">
          {top.map((item, index) => <Link key={item.id} href={`/triage/${item.message_id}`} className="group flex items-center gap-4 rounded-2xl border border-[#e5e2dc] p-4 transition hover:border-[#cfcac0] hover:bg-[#fcfbf8]">
            <div className={`grid size-10 shrink-0 place-items-center rounded-xl ${item.priority_level === "P0_IMMEDIATE" ? "bg-[#fbe8e5] text-signal" : "bg-[#fff0da] text-amber"}`}>{index === 0 ? <Zap size={17}/> : <AlertTriangle size={17}/>}</div>
            <div className="min-w-0 flex-1"><div className="truncate text-sm font-semibold">{item.title}</div><div className="mt-1 truncate text-xs text-[#7d8285]">{item.sender_name} · {item.account_label}</div></div>
            <ChevronRight size={16} className="text-[#a2a6a8] transition group-hover:translate-x-0.5"/>
          </Link>)}
        </div>
      </section>
      <section className="panel p-6">
        <div className="eyebrow">Signal shape</div><h2 className="mb-6 mt-2 text-xl font-semibold tracking-tight">Priority distribution</h2>
        <DistributionBars data={distribution}/>
        <div className="mt-6 rounded-2xl bg-ink p-4 text-white">
          <div className="text-xs font-semibold">Quiet by design</div>
          <p className="mt-1 text-[11px] leading-5 text-white/55">Low-value newsletters remain in the inbox. Only explainable risk reaches the interruption layer.</p>
        </div>
      </section>
    </div>
    <div className="mb-4 mt-8 flex items-end justify-between"><div><div className="eyebrow">Cross-platform view</div><h2 className="mt-2 text-xl font-semibold tracking-tight">Highest-risk messages</h2></div><Link href="/inbox" className="text-xs font-semibold">Open inbox →</Link></div>
    <MessageTable messages={data.messages.slice(0, 8)}/>
  </>;
}
