"use client";

import { Activity, Bot, MessageSquareText, Play, UserRound } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { Button, TextAreaField, TextField } from "@/components/ui";
import type { RuntimeState, WhatsAppInstance } from "@/types/dashboard";

export function DebugView({
  runtime,
  instances,
  busy,
  onRuntime,
  onSimulate,
}: {
  runtime: RuntimeState | null;
  instances: WhatsAppInstance[];
  busy: string | null;
  onRuntime: (p: Partial<RuntimeState>) => void;
  onSimulate: (p: { instance_name: string; webhook_secret?: string; phone: string; text: string; push_name?: string; process_now?: boolean }) => void;
}) {
  const defaultInstance = instances[0]?.instance_name ?? "demo-instance";
  const [instanceName, setInstanceName] = useState(defaultInstance);
  const [secret, setSecret] = useState("");
  const [phone, setPhone] = useState("5511977776666");
  const [name, setName] = useState("Cliente Debug");
  const [text, setText] = useState("Quero um Corolla automático até 120 mil");
  const [processNow, setProcessNow] = useState(true);

  useEffect(() => {
    if (instances[0]?.instance_name && instanceName === "demo-instance") setInstanceName(instances[0].instance_name);
  }, [instanceName, instances]);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSimulate({ instance_name: instanceName, webhook_secret: secret || undefined, phone, text, push_name: name, process_now: processNow });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Debug local</h1>
        <p className="text-sm text-muted-foreground">Simule inbound e runtime. Rotas existem apenas fora de produção.</p>
      </div>
      <div className="grid lg:grid-cols-2 gap-4">
        <div className="glass-panel p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-foreground">Runtime</h2>
            <Activity size={17} className="text-muted-foreground" />
          </div>
          {runtime ? (
            <div className="space-y-2">
              <Button size="sm" className="w-full justify-start" onClick={() => onRuntime({ ai_runtime_enabled: !runtime.ai_runtime_enabled })}>
                <Bot size={14} />{runtime.ai_runtime_enabled ? "Desligar IA global" : "Ligar IA global"}
              </Button>
              <Button size="sm" className="w-full justify-start" onClick={() => onRuntime({ allow_from_me_as_inbound: !runtime.allow_from_me_as_inbound })}>
                <UserRound size={14} />{runtime.allow_from_me_as_inbound ? "Desligar self-group" : "Ligar self-group"}
              </Button>
            </div>
          ) : <p className="text-xs text-muted-foreground">Runtime indisponível.</p>}
        </div>
        <div className="glass-panel p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-foreground">Simular inbound</h2>
            <MessageSquareText size={17} className="text-muted-foreground" />
          </div>
          <form className="grid gap-3" onSubmit={submit}>
            <TextField label="Instância" value={instanceName} onChange={(e) => setInstanceName(e.target.value)} required />
            <TextField label="Webhook secret" value={secret} onChange={(e) => setSecret(e.target.value)} />
            <TextField label="Telefone" value={phone} onChange={(e) => setPhone(e.target.value)} required />
            <TextField label="Nome cliente" value={name} onChange={(e) => setName(e.target.value)} />
            <TextAreaField label="Mensagem" value={text} onChange={(e) => setText(e.target.value)} required rows={3} />
            <label className="flex items-center gap-2 text-sm text-muted-foreground cursor-pointer">
              <input type="checkbox" checked={processNow} onChange={(e) => setProcessNow(e.target.checked)} className="rounded" />
              Processar com IA imediatamente
            </label>
            <Button variant="primary" disabled={busy === "simulate"}><Play size={16} />Simular</Button>
          </form>
        </div>
      </div>
    </div>
  );
}
