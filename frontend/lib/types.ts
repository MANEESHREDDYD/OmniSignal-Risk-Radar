export type Priority = "P0_IMMEDIATE" | "P1_TODAY" | "P2_DIGEST" | "P3_LOW";

export interface Reason {
  reason_code: string;
  reason_type: string;
  points: number;
  explanation: string;
}

export interface Assessment {
  urgency_score: number;
  risk_score: number;
  action_score: number;
  priority_score: number;
  priority_level: Priority;
  recommended_action: string;
  summary: string;
  reasons: Reason[];
}

export interface Message {
  id: string;
  connected_account_id: string;
  account_label: string;
  is_demo?: boolean;
  platform: string;
  sender_name: string;
  sender_identifier: string;
  subject: string | null;
  body_text: string;
  received_at: string;
  has_attachments: boolean;
  assessment: Assessment;
  entities?: { entity_type: string; entity_value: string; confidence: number }[];
}

export interface GoogleConnection {
  id: string;
  provider: string;
  account_email: string | null;
  display_name: string | null;
  status: string;
  is_read_only: boolean;
  scopes: string[];
  connected_at: string | null;
  disconnected_at: string | null;
  last_sync_at: string | null;
  has_stored_tokens: boolean;
}

export interface GoogleStatus {
  real_connectors_enabled: boolean;
  google_configured: boolean;
  token_encryption_configured: boolean;
  scopes: string[];
  redirect_uri: string;
  connections: GoogleConnection[];
}

export interface RealSyncRun {
  id: string;
  oauth_connection_id: string;
  provider: string;
  sync_type: string;
  status: string;
  messages_seen: number;
  messages_created: number;
  calendar_events_seen: number;
  calendar_events_created: number;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
}

export interface Notification {
  id: string;
  message_id: string;
  notification_type: string;
  priority_level: Priority;
  title: string;
  body: string;
  status: string;
  snoozed_until?: string;
  sender_name: string;
  platform: string;
  account_label: string;
  recommended_action: string;
  reasons: Reason[];
}

