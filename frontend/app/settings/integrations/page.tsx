"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle, CalendarDays, CheckCircle2, Lock, Mail, Plug, RefreshCw, ShieldCheck, Trash2, Unplug
} from "lucide-react";
import { api } from "@/lib/api";
import { GoogleConnection, GoogleStatus, RealSyncRun } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState, LoadingState } from "@/components/LoadingState";

type Alert = { kind: "ok" | "warn" | "err"; text: string } | null;

const SCOPE_LABELS: Record<string, string> = {
  "https://www.googleapis.com/auth/gmail.readonly": "Gmail read-only",
  "https://www.googleapis.com/auth/calendar.events.readonly": "Calendar events read-only",
};

export default function IntegrationsPage() {
  const [status, setStatus] = useState<GoogleStatus | null>(null);
  const [runs, setRuns] = useState<RealSyncRun[]>([]);
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [alert, setAlert] = useState<Alert>(null);

  const load = () =>
    Promise.all([
      api<GoogleStatus>("/auth/google/status"),
      api<RealSyncRun[]>("/real-sync/runs").catch(() => []),
    ])
      .then(([s, r]) => { setStatus(s); setRuns(r); })
      .catch(() => setError(true));

  useEffect(() => { load(); }, []);

  if (error) return <ErrorState />;
  if (!status) return <LoadingState />;

  const enabled = status.real_connectors_enabled;
  const configured = status.google_configured && status.token_encryption_configured;
  const connection: GoogleConnection | undefined =
    status.connections.find((c) => c.status === "connected") || status.connections[0];
  const hasConnected = connection?.status === "connected";

  const cardState = !enabled ? "Disabled" : !configured ? "Not configured" : hasConnected ? "Connected"
    : connection?.status === "error" ? "Error" : "Ready to connect";

  const run = async (label: string, fn: () => Promise<{ status?: string; authorization_url?: string; message?: string }>) => {
    setBusy(label); setAlert(null);
    try {
      const res = await fn();
      if (res.authorization_url) { window.location.href = res.authorization_url; return; }
      if (res.status && res.status.startsWith("blocked")) setAlert({ kind: "warn", text: res.message || "Action blocked." });
      else setAlert({ kind: "ok", text: `${label} complete.` });
      await load();
    } catch {
      setAlert({ kind: "err", text: `${label} failed. Is the backend running?` });
    } finally {
      setBusy(null);
    }
  };

  const connect = () => run("Connect Google", () => api("/auth/google/start"));
  const syncGmail = () => run("Sync Gmail", () => api(`/real-sync/google/${connection!.id}/gmail`, { method: "POST" }));
  const syncCalendar = () => run("Sync Calendar", () => api(`/real-sync/google/${connection!.id}/calendar`, { method: "POST" }));
  const disconnect = () => run("Disconnect", () => api(`/auth/google/disconnect/${connection!.id}`, { method: "POST" }));
  const deleteCache = () => run("Delete local cache", () => api(`/auth/google/delete-cache/${connection!.id}`, { method: "POST" }));

  const btn = "button-secondary flex items-center justify-center gap-2 disabled:cursor-not-allowed disabled:opacity-40";

  return (
    <>
      <PageHeader
        eyebrow="Settings · Real connectors"
        title="Google integration (read-only)"
        description="Optional, opt-in real Gmail and Calendar access. Synthetic demo mode stays the default and keeps working without any of this."
        action={
          <div className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-semibold ${enabled ? "bg-[#e5f2eb] text-moss" : "bg-[#f3efe7] text-[#7c5a2e]"}`}>
            <ShieldCheck size={15} /> {enabled ? "Real connectors enabled" : "Real connectors disabled"}
          </div>
        }
      />

      {/* 1. Safety banner */}
      <div className="panel mb-5 flex items-start gap-3 border-l-4 border-[#d9a57e] p-5">
        <AlertTriangle size={18} className="mt-0.5 shrink-0 text-[#bf7b3c]" />
        <p className="text-sm leading-6 text-[#5b6064]">
          Real connectors are <strong>disabled by default</strong>. Synthetic demo mode remains available.
          Enable <code className="rounded bg-[#f1eee7] px-1.5 py-0.5 text-xs">REAL_CONNECTORS_ENABLED=true</code> locally
          before connecting a real Google account. All access is <strong>read-only</strong> and stored <strong>locally</strong>.
        </p>
      </div>

      {alert && (
        <div className={`mb-5 rounded-xl px-4 py-3 text-sm font-medium ${
          alert.kind === "ok" ? "bg-[#e3f1e9] text-moss" : alert.kind === "warn" ? "bg-[#fbf0dd] text-[#8a5a1e]" : "bg-[#fbe3e0] text-[#a3322b]"
        }`}>{alert.text}</div>
      )}

      <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        {/* 2. Google integration card */}
        <div className="panel p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="grid size-11 place-items-center rounded-xl bg-[#eff1f1]"><Plug size={19} /></div>
              <div>
                <div className="text-base font-semibold">Google Workspace</div>
                <div className="text-xs text-[#858a8d]">{connection?.account_email || "No account connected"}</div>
              </div>
            </div>
            <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide ${
              cardState === "Connected" ? "bg-[#e3f1e9] text-moss" : cardState === "Error" ? "bg-[#fbe3e0] text-[#a3322b]" : "bg-[#efece6] text-[#7c5a2e]"
            }`}>{cardState}</span>
          </div>

          <div className="my-5 rounded-2xl bg-[#f7f6f2] p-4">
            <div className="eyebrow mb-2">Scopes requested (read-only)</div>
            <ul className="space-y-1.5">
              {status.scopes.map((s) => (
                <li key={s} className="flex items-center gap-2 text-xs font-medium text-[#5b6064]">
                  <Lock size={12} className="text-[#8b8f92]" /> {SCOPE_LABELS[s] || s}
                </li>
              ))}
            </ul>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button className={btn} disabled={!enabled || !configured || busy !== null} onClick={connect}>
              <Plug size={14} /> Connect Google
            </button>
            <button className={btn} disabled={!enabled || !hasConnected || busy !== null} onClick={syncGmail}>
              <Mail size={14} className={busy === "Sync Gmail" ? "animate-pulse" : ""} /> Sync Gmail read-only
            </button>
            <button className={btn} disabled={!enabled || !hasConnected || busy !== null} onClick={syncCalendar}>
              <CalendarDays size={14} className={busy === "Sync Calendar" ? "animate-pulse" : ""} /> Sync Calendar read-only
            </button>
            <button className={btn} disabled={!enabled || !hasConnected || busy !== null} onClick={disconnect}>
              <Unplug size={14} /> Disconnect
            </button>
            <button className={`${btn} col-span-2 text-[#a3322b]`} disabled={!enabled || !connection || busy !== null} onClick={deleteCache}>
              <Trash2 size={14} /> Delete local cache
            </button>
          </div>

          {!enabled && <p className="muted mt-4 text-xs">Buttons are disabled because real connectors are off. This is the safe default.</p>}
          {enabled && !configured && <p className="muted mt-4 text-xs">Set GOOGLE_CLIENT_ID / SECRET and TOKEN_ENCRYPTION_KEY to enable connecting.</p>}
        </div>

        {/* 3. Consent explanation */}
        <div className="panel p-6">
          <div className="flex items-center gap-2 text-sm font-semibold"><ShieldCheck size={16} className="text-moss" /> What this connector does</div>
          <ul className="mt-4 space-y-2.5 text-xs leading-5 text-[#5b6064]">
            {[
              "Reads selected Gmail and Calendar data only.",
              "Never sends emails.",
              "Never creates or edits calendar events.",
              "Never forwards or exports your messages.",
              "Stores synced data locally on this machine.",
              "You can disconnect and delete the local cache anytime.",
            ].map((t) => (
              <li key={t} className="flex items-start gap-2"><CheckCircle2 size={14} className="mt-0.5 shrink-0 text-[#54a87d]" /> {t}</li>
            ))}
          </ul>
          <div className="mt-5 rounded-xl bg-[#f7f6f2] p-4 text-xs text-[#5b6064]">
            Tokens are <strong>encrypted at rest</strong> and never shown in this UI or returned to the browser.
          </div>
        </div>
      </div>

      {/* 4. Real sync runs */}
      <div className="panel mt-5 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4">
          <div className="text-sm font-semibold">Recent real sync runs</div>
          <button className="button-secondary flex items-center gap-2 text-xs" onClick={load}><RefreshCw size={13} /> Refresh</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse text-left">
            <thead><tr className="border-y border-[#e4e1da] bg-[#faf9f6] text-[10px] uppercase tracking-[.13em] text-[#858a8d]">
              <th className="px-5 py-3">Provider</th><th className="px-3 py-3">Sync type</th><th className="px-3 py-3">Status</th><th className="px-3 py-3">Seen / Created</th><th className="px-5 py-3 text-right">Started</th>
            </tr></thead>
            <tbody>
              {runs.length === 0 && <tr><td colSpan={5} className="px-5 py-6 text-center text-xs text-[#8b8f92]">No real sync runs yet.</td></tr>}
              {runs.map((r) => (
                <tr key={r.id} className="border-b border-[#ece9e3] last:border-0">
                  <td className="px-5 py-3 text-xs font-semibold capitalize">{r.provider}</td>
                  <td className="px-3 py-3 text-xs capitalize text-[#596267]">{r.sync_type.replaceAll("_", " ")}</td>
                  <td className="px-3 py-3"><span className={`rounded-full px-2 py-0.5 text-[10px] font-bold uppercase ${
                    r.status === "completed" ? "bg-[#e3f1e9] text-moss" : r.status === "failed" ? "bg-[#fbe3e0] text-[#a3322b]" : "bg-[#efece6] text-[#7c5a2e]"
                  }`}>{r.status.replaceAll("_", " ")}</span>{r.error_message && <span className="ml-2 text-[10px] text-[#a3322b]">{r.error_message}</span>}</td>
                  <td className="px-3 py-3 text-xs text-[#596267]">{r.messages_seen + r.calendar_events_seen} / {r.messages_created + r.calendar_events_created}</td>
                  <td className="px-5 py-3 text-right text-xs text-[#898e91]">{new Date(r.started_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Back to demo mode */}
      <div className="mt-5 rounded-2xl border border-dashed border-[#cfcac0] p-5">
        <div className="text-sm font-semibold">Back to demo mode</div>
        <p className="muted mt-1">Synthetic demo accounts continue to work without any real connector setup. Real synced messages appear in the unified inbox and radar with a small <span className="rounded-full bg-[#fde8d4] px-1.5 py-0.5 text-[10px] font-bold uppercase text-[#a35a1c]">Real</span> badge.</p>
      </div>
    </>
  );
}
