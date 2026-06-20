"use client";

import {
  Activity, Bell, BookOpenCheck, Cable, Inbox, ListChecks, Radar,
  ScrollText, Settings2, ShieldCheck, Sparkles
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  {href: "/", label: "Command center", icon: Activity},
  {href: "/inbox", label: "Unified inbox", icon: Inbox},
  {href: "/radar", label: "Risk radar", icon: Radar},
  {href: "/notifications", label: "Notifications", icon: Bell},
  {href: "/triage", label: "Triage", icon: ListChecks},
  {href: "/connections", label: "Connections", icon: Cable},
  {href: "/rules", label: "Rules", icon: Settings2},
  {href: "/analytics", label: "Analytics", icon: BookOpenCheck},
  {href: "/audit-log", label: "Audit log", icon: ScrollText},
];

export function AppShell({children}: {children: React.ReactNode}) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[250px_1fr]">
      <aside className="hidden min-h-screen bg-ink px-4 py-5 text-white lg:flex lg:flex-col lg:sticky lg:top-0 lg:h-screen">
        <div className="flex items-center gap-3 px-2 pb-8">
          <div className="grid size-10 place-items-center rounded-xl bg-signal"><Sparkles size={19}/></div>
          <div>
            <div className="text-[15px] font-semibold tracking-tight">OmniSignal</div>
            <div className="text-[10px] uppercase tracking-[.17em] text-white/45">SecretaryOps</div>
          </div>
        </div>
        <nav className="space-y-1">
          {nav.map(({href, label, icon: Icon}) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link key={href} href={href} className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] transition ${active ? "bg-white text-ink" : "text-white/65 hover:bg-white/8 hover:text-white"}`}>
                <Icon size={17}/><span>{label}</span>
                {label === "Notifications" && <span className="ml-auto rounded-full bg-signal px-2 py-0.5 text-[10px] font-bold text-white">25</span>}
              </Link>
            );
          })}
        </nav>
        <div className="mt-auto rounded-2xl border border-white/10 bg-white/[.045] p-4">
          <div className="flex items-center gap-2 text-xs font-semibold"><ShieldCheck size={15} className="text-[#73c29b]"/> Demo privacy mode</div>
          <p className="mt-2 text-[11px] leading-5 text-white/45">Synthetic messages only. No credentials, outbound sends, or paid APIs.</p>
        </div>
      </aside>
      <main className="min-w-0">
        <header className="flex h-[70px] items-center justify-between border-b border-[#ddd9d0] bg-paper/90 px-5 backdrop-blur md:px-8">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#697075]">
            <span className="size-2 rounded-full bg-[#54a87d] shadow-[0_0_0_4px_rgba(84,168,125,.13)]"/>
            All systems monitoring
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden text-right sm:block"><div className="text-xs font-semibold">Maneesh</div><div className="text-[10px] text-[#81868a]">6 accounts connected</div></div>
            <div className="grid size-9 place-items-center rounded-full bg-[#d9a57e] text-xs font-bold text-white">M</div>
          </div>
        </header>
        <div className="mx-auto max-w-[1480px] p-5 md:p-8">{children}</div>
      </main>
    </div>
  );
}

