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

