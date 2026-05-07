"use client";

import { Archive, Bot, Play, Power, RefreshCw, Send, Trash2 } from "lucide-react";
import { FormEvent, useState } from "react";
import { Badge, Button, EmptyState } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { ConversationDetail, ConversationSummary } from "@/types/dashboard";

function formatDate(value: string | null) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function senderLabel(sender: string) {
  if (sender === "agent") return "IA";
  if (sender === "human") return "Humano";
  if (sender === "customer") return "Cliente";
  return "Sistema";
}

export function InboxView({
  conversations,
  selectedId,
  conversation,
  busy,
  onSelect,
  onRefresh,
  onSendHuman,
  onEnableAi,
  onDisableAi,
  onArchive,
  onDelete,
}: {
  conversations: ConversationSummary[];
  selectedId: string | null;
  conversation: ConversationDetail | null;
  busy: string | null;
  onSelect: (id: string) => void;
  onRefresh: () => void;
  onSendHuman: (id: string, content: string) => void;
  onEnableAi: (id: string) => void;
  onDisableAi: (id: string) => void;
  onArchive: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  const [message, setMessage] = useState("");
  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!conversation || !message.trim()) return;
    onSendHuman(conversation.id, message);
    setMessage("");
  };

  return (
    <div className="flex flex-col md:flex-row gap-4 h-[calc(100vh-8rem)]">
      {/* Conversation list */}
      <section className={cn(
        "w-full md:w-72 shrink-0 glass-panel flex flex-col overflow-hidden",
        selectedId ? "hidden md:flex" : "flex"
      )}>
        <div className="p-3 border-b border-border flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground">Conversas</h2>
          <Button size="icon" variant="ghost" onClick={onRefresh}><RefreshCw size={14} /></Button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {conversations.map((item) => (
            <button
              key={item.id}
              className={`w-full text-left px-3 py-3 border-b border-border transition-colors cursor-pointer ${
                selectedId === item.id ? "bg-primary/10" : "hover:bg-accent"
              }`}
              onClick={() => onSelect(item.id)}
            >
              <span className="text-sm text-foreground block truncate">{item.customer.name ?? item.customer.phone}</span>
              <small className="text-xs text-muted-foreground block truncate">{item.last_message?.content ?? "Sem mensagens"}</small>
              <Badge tone={item.ai_enabled ? "green" : "amber"} className="mt-1">{item.status}</Badge>
            </button>
          ))}
          {!conversations.length && <EmptyState title="Sem conversas" text="Use o webhook ou debug para criar." />}
        </div>
      </section>

      {/* Chat */}
      <section className={cn(
        "flex-1 glass-panel flex flex-col overflow-hidden",
        selectedId ? "flex" : "hidden md:flex"
      )}>
        {conversation ? (
          <>
            <div className="p-4 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Button variant="ghost" size="icon" className="md:hidden" onClick={() => onSelect("")}>
                  <Archive size={18} />
                </Button>
                <div>
                  <h2 className="text-sm font-semibold text-foreground">{conversation.customer.name ?? conversation.customer.phone}</h2>
                  <p className="text-xs text-muted-foreground">{conversation.whatsapp_instance.instance_name}</p>
                </div>
              </div>
              <Badge tone={conversation.ai_enabled ? "green" : "amber"}>{conversation.ai_enabled ? "IA ativa" : "IA pausada"}</Badge>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {conversation.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`max-w-[75%] rounded-xl px-3 py-2 text-sm ${
                    msg.direction === "inbound"
                      ? "bg-muted text-foreground self-start"
                      : msg.sender_type === "agent"
                        ? "bg-primary/15 text-primary ml-auto"
                        : "bg-success/15 text-success ml-auto"
                  }`}
                >
                  <span className="text-[10px] uppercase tracking-wide opacity-70 block">{senderLabel(msg.sender_type)}</span>
                  <p>{msg.content}</p>
                  <small className="text-[10px] opacity-50 block text-right">{formatDate(msg.created_at)}</small>
                </div>
              ))}
            </div>
            <form className="p-3 border-t border-border flex gap-2" onSubmit={submit}>
              <input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Responder como humano"
                className="flex-1 h-9 rounded-lg border border-input bg-muted px-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
              <Button variant="primary" loading={busy === "send"} disabled={busy === "send"}><Send size={15} /></Button>
            </form>
          </>
        ) : (
          <EmptyState title="Selecione uma conversa" text="A timeline e controles aparecem aqui." />
        )}
      </section>

      {/* Detail panel */}
      <aside className={cn(
        "w-full xl:w-64 shrink-0 glass-panel overflow-y-auto p-4 space-y-4",
        selectedId ? "flex flex-col" : "hidden xl:flex xl:flex-col"
      )}>
        {conversation ? (
          <>
            <h2 className="text-sm font-semibold text-foreground flex items-center gap-2"><Bot size={16} />Gestão de Atendimento</h2>
            <div className="space-y-2">
              <Button
                size="sm"
                variant={conversation.ai_enabled ? "ghost" : "primary"}
                className={cn("w-full justify-between", conversation.ai_enabled ? "bg-success/10 text-success hover:bg-success/20 hover:text-success" : "")}
                loading={busy === "ai"}
                onClick={() => conversation.ai_enabled ? onDisableAi(conversation.id) : onEnableAi(conversation.id)}
              >
                <div className="flex items-center gap-2">
                  {conversation.ai_enabled ? <Bot size={14} /> : <Power size={14} />}
                  <span>{conversation.ai_enabled ? "IA Ativa" : "Ativar IA"}</span>
                </div>
                <Badge tone={conversation.ai_enabled ? "green" : "amber"}>{conversation.ai_enabled ? "LIGADO" : "DESLIGADO"}</Badge>
              </Button>
              <Button size="sm" className="w-full justify-start" loading={busy === "archive"} onClick={() => onArchive(conversation.id)}><Archive size={14} />Arquivar</Button>
              <Button size="sm" variant="danger" className="w-full justify-start" loading={busy === "delete"} onClick={() => onDelete(conversation.id)}><Trash2 size={14} />Excluir</Button>
            </div>

            <div className="pt-3 border-t border-border">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase mb-2">Lead</h3>
              {conversation.lead ? (
                <dl className="text-xs space-y-1">
                  <div className="flex justify-between"><dt className="text-muted-foreground">Status</dt><dd className="text-foreground">{conversation.lead.status}</dd></div>
                  <div className="flex justify-between"><dt className="text-muted-foreground">Score</dt><dd className="text-foreground">{conversation.lead.score}</dd></div>
                  <div className="flex justify-between"><dt className="text-muted-foreground">Interesse</dt><dd className="text-foreground">{conversation.lead.vehicle_interest ?? "-"}</dd></div>
                </dl>
              ) : <p className="text-xs text-muted-foreground">Nenhum lead gerado.</p>}
            </div>
          </>
        ) : null}
      </aside>
    </div>
  );
}
