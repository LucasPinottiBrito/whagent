import type { CurrentUser } from "./user";

export type AuthToken = {
  access_token: string;
  token_type: "bearer";
};

export type SetupStatus = {
  needs_setup: boolean;
};

export type BootstrapPayload = {
  store_name: string;
  store_slug: string;
  store_document?: string;
  store_phone?: string;
  admin_email: string;
  admin_full_name: string;
  admin_password: string;
};

export type Store = {
  id: string;
  name: string;
  slug: string;
  document: string | null;
  phone: string | null;
  created_at: string;
  updated_at: string;
};

export type DashboardOverview = {
  customers_total: number;
  conversations_total: number;
  leads_total: number;
  instances_total: number;
  ai_active_conversations: number;
  human_active_conversations: number;
  pending_conversations: number;
};

export type WhatsAppInstance = {
  id: string;
  store_id: string;
  instance_name: string;
  phone: string | null;
  evolution_instance_id: string | null;
  active: boolean;
  webhook_url?: string;
  evolution?: unknown;
  created_at: string;
  updated_at: string;
};

export type CreateInstancePayload = {
  instance_name: string;
  phone?: string;
  webhook_secret?: string;
};

export type ConversationMessage = {
  id: string;
  conversation_id: string;
  direction: "inbound" | "outbound";
  sender_type: "customer" | "agent" | "human" | "system";
  content: string;
  evolution_message_id: string | null;
  created_at: string;
};

export type LeadSummary = {
  id: string;
  customer_id: string;
  status: string;
  score: number;
  intent: string | null;
  vehicle_interest: string | null;
  budget_min: string | number | null;
  budget_max: string | number | null;
  payment_type: string | null;
  trade_in_vehicle: string | null;
  interest_summary: string | null;
  conversation_id?: string;
  customer?: {
    id: string;
    name: string | null;
    phone: string;
  } | null;
  updated_at: string;
};

export type ConversationSummary = {
  id: string;
  status: string;
  ai_enabled: boolean;
  pending_agent_processing: boolean;
  last_intent: string | null;
  last_customer_message_at: string | null;
  last_processing_error: string | null;
  customer: {
    id: string;
    name: string | null;
    phone: string;
  };
  whatsapp_instance: {
    id: string;
    instance_name: string;
    phone: string | null;
  };
  lead: LeadSummary | null;
  last_message: ConversationMessage | null;
  created_at: string;
  updated_at: string;
};

export type AgentRun = {
  id: string;
  input_text: string;
  output_text: string | null;
  model: string | null;
  tools_used: string[] | null;
  status: string;
  error: string | null;
  created_at: string;
  updated_at: string;
};

export type HandoffEvent = {
  id: string;
  event_type: string;
  salesperson_id: string | null;
  reason: string | null;
  metadata: unknown;
  created_at: string;
};

export type ConversationDetail = ConversationSummary & {
  messages: ConversationMessage[];
  agent_runs: AgentRun[];
  handoff_events: HandoffEvent[];
};

export type RuntimeState = {
  ai_runtime_enabled: boolean;
  allow_from_me_as_inbound: boolean;
};

export type SessionState = {
  token: string | null;
  user: CurrentUser | null;
};
