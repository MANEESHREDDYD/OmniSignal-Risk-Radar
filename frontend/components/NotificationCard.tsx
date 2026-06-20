"use client";

import { AlarmClock, Check, ExternalLink, X } from "lucide-react";
import Link from "next/link";
import { Notification } from "@/lib/types";
import { PriorityBadge } from "./Badges";

export function NotificationCard({item, onAction}: {item: Notification; onAction?: (id: string, action: "snooze" | "dismiss" | "resolve") => void}) {
  return (
    <div className="panel p-5">
      <div className="flex flex-col justify-between gap-4 sm:flex-row">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2"><PriorityBadge priority={item.priority_level}/><span className="text-[10px] font-semibold uppercase tracking-wider text-[#8a8f92]">{item.platform} · {item.account_label}</span></div>
          <h3 className="mt-3 text-[15px] font-semibold tracking-tight">{item.title}</h3>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-[#666d71]">{item.body}</p>
          <div className="mt-3 flex flex-wrap gap-2">{item.reasons.map(reason => <span key={reason.reason_code} className="rounded-lg bg-[#f1f0ec] px-2.5 py-1 text-[10px] font-semibold text-[#697075]">{reason.reason_code.replaceAll("_", " ")}</span>)}</div>
        </div>
        <div className="flex shrink-0 items-start gap-2">
          <Link href={`/triage/${item.message_id}`} className="button-primary inline-flex items-center gap-2">Open <ExternalLink size={13}/></Link>
          {onAction && <>
            <button title="Snooze" onClick={() => onAction(item.id, "snooze")} className="grid size-10 place-items-center rounded-xl border border-[#ddd9d1] bg-white hover:bg-[#f8f6f1]"><AlarmClock size={15}/></button>
            <button title="Resolve" onClick={() => onAction(item.id, "resolve")} className="grid size-10 place-items-center rounded-xl border border-[#ddd9d1] bg-white hover:bg-[#f8f6f1]"><Check size={15}/></button>
            <button title="Dismiss" onClick={() => onAction(item.id, "dismiss")} className="grid size-10 place-items-center rounded-xl border border-[#ddd9d1] bg-white hover:bg-[#f8f6f1]"><X size={15}/></button>
          </>}
        </div>
      </div>
    </div>
  );
}

