"use client";

import { LogOut, Plus, Power, RefreshCw, ShieldCheck, Trash2, Zap } from "lucide-react";
import { FormEvent, useState } from "react";
import { Badge, Button, EmptyState, TextField } from "@/components/ui";
import type { WhatsAppInstance } from "@/types/dashboard";

export function InstancesView({
  instances,
  qrImages,
  connectionPayloads,
  busy,
  onCreate,
  onConnect,
  onSyncStatus,
  onSyncWebhook,
  onRestart,
  onLogout,
  onDelete,
}: {
  instances: WhatsAppInstance[];
  qrImages: Record<string, string>;
  connectionPayloads: Record<string, string>;
  busy: string | null;
  onCreate: (p: { instance_name: string; phone?: string; webhook_secret?: string }) => void;
  onConnect: (i: WhatsAppInstance) => void;
  onSyncStatus: (i: WhatsAppInstance) => void;
  onSyncWebhook: (i: WhatsAppInstance) => void;
  onRestart: (i: WhatsAppInstance) => void;
  onLogout: (i: WhatsAppInstance) => void;
  onDelete: (i: WhatsAppInstance) => void;
}) {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [secret, setSecret] = useState("");

  const submit = (e: FormEvent) => {
    e.preventDefault();
    onCreate({ instance_name: name, phone: phone || undefined, webhook_secret: secret || undefined });
    setName("");
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Conexões do WhatsApp</h1>
        <p className="text-sm text-muted-foreground">Crie, conecte e sincronize números de vendas e atendimento.</p>
      </div>

      <div className="glass-panel p-5">
        <form className="flex flex-wrap items-end gap-3" onSubmit={submit}>
          <TextField label="Nome da conexão" value={name} onChange={(e) => setName(e.target.value)} required className="flex-1 min-w-[180px]" />
          <TextField label="Telefone" value={phone} onChange={(e) => setPhone(e.target.value)} className="w-44" />
          <TextField label="Webhook secret" value={secret} onChange={(e) => setSecret(e.target.value)} className="w-44" />
          <Button variant="primary" disabled={busy === "create-instance"}>
            <Plus size={16} />
            Criar
          </Button>
        </form>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {instances.map((inst) => (
          <article key={inst.id} className="glass-panel p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-foreground">{inst.instance_name}</h2>
                <p className="text-xs text-muted-foreground">{inst.phone ?? "telefone não informado"}</p>
              </div>
              <Badge tone={inst.active ? "green" : "red"}>{inst.active ? "ativa" : "desconectada"}</Badge>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button size="sm" onClick={() => onConnect(inst)}><Zap size={14} />Conectar</Button>
              <Button size="sm" onClick={() => onSyncStatus(inst)}><RefreshCw size={14} />Status</Button>
              <Button size="sm" onClick={() => onSyncWebhook(inst)}><ShieldCheck size={14} />Webhook</Button>
              <Button size="sm" onClick={() => onRestart(inst)}><Power size={14} />Restart</Button>
              <Button size="sm" variant="danger" onClick={() => onLogout(inst)}><LogOut size={14} />Logout</Button>
              <Button size="sm" variant="danger" onClick={() => onDelete(inst)}><Trash2 size={14} />Excluir</Button>
            </div>
            {qrImages[inst.id] && (
              <div className="bg-white rounded-lg p-3 w-fit">
                <img src={qrImages[inst.id]} alt={`QR ${inst.instance_name}`} className="w-48 h-48" />
              </div>
            )}
            {connectionPayloads[inst.id] && (
              <pre className="text-xs bg-muted p-3 rounded-lg overflow-x-auto text-muted-foreground max-h-32">
                {connectionPayloads[inst.id]}
              </pre>
            )}
          </article>
        ))}
        {!instances.length && <EmptyState title="Nenhuma conexão" text="Conecte seu primeiro número de WhatsApp." />}
      </div>
    </div>
  );
}
