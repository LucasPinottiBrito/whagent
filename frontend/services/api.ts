import type {
  AuthToken,
  BootstrapPayload,
  ConversationDetail,
  ConversationSummary,
  CreateInstancePayload,
  DashboardOverview,
  LeadSummary,
  RuntimeState,
  SetupStatus,
  Store,
  WhatsAppInstance,
} from "@/types/dashboard";
import type { CurrentUser } from "@/types/user";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function backendFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  return apiFetch<T>(path, init);
}

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit & { token?: string | null; bodyJson?: unknown },
): Promise<T> {
  const { token, bodyJson, ...requestInit } = init ?? {};
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...requestInit,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(requestInit.headers ?? {}),
    },
    body: bodyJson === undefined ? requestInit.body : JSON.stringify(bodyJson),
  });

  if (!response.ok) {
    let message = `Backend request failed: ${response.status}`;
    try {
      const payload = await response.json();
      if (payload?.detail) {
        message = Array.isArray(payload.detail)
          ? payload.detail.map((item: { msg?: string }) => item.msg).join(", ")
          : String(payload.detail);
      }
    } catch {
      // Keep the generic error when the backend did not return JSON.
    }
    throw new ApiError(response.status, message);
  }

  return response.json() as Promise<T>;
}

export function createApiClient(token?: string | null) {
  return {
    health: () => apiFetch<{ status: string }>("/health"),
    setupStatus: () => apiFetch<SetupStatus>("/api/setup/status"),
    bootstrap: (payload: BootstrapPayload) =>
      apiFetch<AuthToken & { store: Store; user: CurrentUser }>("/api/setup/bootstrap", {
        method: "POST",
        bodyJson: payload,
      }),
    login: (email: string, password: string) =>
      apiFetch<AuthToken>("/api/auth/login", {
        method: "POST",
        bodyJson: { email, password },
      }),
    me: () => apiFetch<CurrentUser>("/api/auth/me", { token }),
    store: () => apiFetch<Store>("/api/store/me", { token }),
    updateStore: (payload: Partial<Store>) =>
      apiFetch<Store>("/api/store/me", {
        method: "PATCH",
        token,
        bodyJson: payload,
      }),
    overview: () =>
      apiFetch<DashboardOverview>("/api/dashboard/overview", { token }),
    instances: () =>
      apiFetch<{ items: WhatsAppInstance[] }>("/api/whatsapp-instances", { token }),
    createInstance: (payload: CreateInstancePayload) =>
      apiFetch<WhatsAppInstance>("/api/whatsapp-instances", {
        method: "POST",
        token,
        bodyJson: payload,
      }),
    getInstance: (id: string) =>
      apiFetch<WhatsAppInstance>(`/api/whatsapp-instances/${id}`, { token }),
    connectInstance: (id: string) =>
      apiFetch<Record<string, unknown>>(`/api/whatsapp-instances/${id}/connect`, {
        method: "POST",
        token,
      }),
    syncInstanceStatus: (id: string) =>
      apiFetch<{ state: string | null; evolution: unknown }>(
        `/api/whatsapp-instances/${id}/sync-status`,
        { method: "POST", token },
      ),
    syncInstanceWebhook: (id: string) =>
      apiFetch<Record<string, unknown>>(
        `/api/whatsapp-instances/${id}/sync-webhook`,
        { method: "POST", token },
      ),
    restartInstance: (id: string) =>
      apiFetch<Record<string, unknown>>(`/api/whatsapp-instances/${id}/restart`, {
        method: "POST",
        token,
      }),
    logoutInstance: (id: string) =>
      apiFetch<Record<string, unknown>>(`/api/whatsapp-instances/${id}/logout`, {
        method: "POST",
        token,
      }),
    conversations: () =>
      apiFetch<{ items: ConversationSummary[] }>("/api/conversations", { token }),
    conversation: (id: string) =>
      apiFetch<ConversationDetail>(`/api/conversations/${id}`, { token }),
    sendHumanMessage: (id: string, content: string) =>
      apiFetch<{ message: unknown; evolution: unknown }>(
        `/api/conversations/${id}/messages/human`,
        { method: "POST", token, bodyJson: { content } },
      ),
    enableAi: (id: string) =>
      apiFetch<{ status: string; conversation_id: string; ai_enabled: boolean }>(
        `/api/conversations/${id}/ai/enable`,
        { method: "POST", token },
      ),
    disableAi: (id: string) =>
      apiFetch<{ status: string; conversation_id: string; ai_enabled: boolean }>(
        `/api/conversations/${id}/ai/disable`,
        { method: "POST", token },
      ),
    processNow: (id: string) =>
      apiFetch<Record<string, unknown>>(`/api/conversations/${id}/process-now`, {
        method: "POST",
        token,
      }),
    leads: () => apiFetch<{ items: LeadSummary[] }>("/api/leads", { token }),
    lead: (id: string) => apiFetch<LeadSummary>(`/api/leads/${id}`, { token }),
    updateLead: (id: string, payload: Record<string, unknown>) =>
      apiFetch<LeadSummary>(`/api/leads/${id}`, { method: "PATCH", token, bodyJson: payload }),
    deleteLead: (id: string) =>
      apiFetch<{ status: string }>(`/api/leads/${id}`, { method: "DELETE", token }),
    updateInstance: (id: string, payload: Record<string, unknown>) =>
      apiFetch<Record<string, unknown>>(`/api/whatsapp-instances/${id}`, { method: "PATCH", token, bodyJson: payload }),
    deleteInstance: (id: string) =>
      apiFetch<{ status: string }>(`/api/whatsapp-instances/${id}`, { method: "DELETE", token }),
    users: () => apiFetch<{ items: Record<string, unknown>[] }>("/api/users", { token }),
    createUser: (payload: Record<string, unknown>) =>
      apiFetch<Record<string, unknown>>("/api/users", { method: "POST", token, bodyJson: payload }),
    updateUser: (id: string, payload: Record<string, unknown>) =>
      apiFetch<Record<string, unknown>>(`/api/users/${id}`, { method: "PATCH", token, bodyJson: payload }),
    deleteUser: (id: string) =>
      apiFetch<{ status: string }>(`/api/users/${id}`, { method: "DELETE", token }),
    customers: () => apiFetch<{ items: Record<string, unknown>[] }>("/api/customers", { token }),
    updateCustomer: (id: string, payload: Record<string, unknown>) =>
      apiFetch<Record<string, unknown>>(`/api/customers/${id}`, { method: "PATCH", token, bodyJson: payload }),
    deleteCustomer: (id: string) =>
      apiFetch<{ status: string }>(`/api/customers/${id}`, { method: "DELETE", token }),
    archiveConversation: (id: string) =>
      apiFetch<{ status: string }>(`/api/conversations/${id}/archive`, { method: "POST", token }),
    deleteConversation: (id: string) =>
      apiFetch<{ status: string }>(`/api/conversations/${id}`, { method: "DELETE", token }),
    runtime: () => apiFetch<RuntimeState>("/api/debug/runtime", { token }),
    updateRuntime: (payload: Partial<RuntimeState>) =>
      apiFetch<RuntimeState>("/api/debug/runtime", {
        method: "PATCH",
        token,
        bodyJson: payload,
      }),
    simulateInbound: (payload: {
      instance_name: string;
      webhook_secret?: string;
      phone: string;
      text: string;
      push_name?: string;
      process_now?: boolean;
    }) =>
      apiFetch<Record<string, unknown>>("/api/debug/evolution/simulate-inbound", {
        method: "POST",
        token,
        bodyJson: payload,
      }),
  };
}
