"use client";

import Link from "next/link";
import { Paperclip } from "lucide-react";
import { formatPlatform, timeAgo } from "@/lib/api";
import { Message } from "@/lib/types";
import { PriorityBadge, ScorePill } from "./Badges";

export function MessageTable({messages}: {messages: Message[]}) {
  return (
    <div className="panel overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] border-collapse text-left">
          <thead><tr className="border-b border-[#e4e1da] bg-[#faf9f6] text-[10px] uppercase tracking-[.13em] text-[#858a8d]">
            <th className="px-5 py-3.5">Priority</th><th className="px-3 py-3.5">Source</th><th className="px-3 py-3.5">Sender & signal</th><th className="px-3 py-3.5">Scores</th><th className="px-3 py-3.5">Route</th><th className="px-5 py-3.5 text-right">Age</th>
          </tr></thead>
          <tbody>
            {messages.map((message) => (
              <tr key={message.id} className="border-b border-[#ece9e3] last:border-0 hover:bg-[#fcfbf8]">
                <td className="px-5 py-4"><PriorityBadge priority={message.assessment.priority_level}/></td>
                <td className="px-3 py-4"><div className="text-xs font-bold">{formatPlatform(message.platform)}</div><div className="mt-1 text-[10px] text-[#8b8f92]">{message.account_label}</div></td>
                <td className="max-w-[410px] px-3 py-4">
                  <Link href={`/triage/${message.id}`} className="block">
                    <div className="flex items-center gap-1.5 text-sm font-semibold">{message.sender_name}{message.has_attachments && <Paperclip size={12} className="text-[#8b8f92]"/>}</div>
                    <div className="mt-1 truncate text-xs text-[#747a7e]">{message.subject || message.body_text}</div>
                  </Link>
                </td>
                <td className="px-3 py-4"><div className="flex gap-3"><ScorePill value={message.assessment.urgency_score} kind="urgency"/><ScorePill value={message.assessment.risk_score} kind="risk"/><ScorePill value={message.assessment.action_score} kind="action"/></div></td>
                <td className="px-3 py-4 text-xs font-semibold capitalize text-[#596267]">{message.assessment.recommended_action.replaceAll("_", " ")}</td>
                <td className="px-5 py-4 text-right text-xs text-[#898e91]">{timeAgo(message.received_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

