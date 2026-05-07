"use client";

import QRCode from "qrcode";
import { useCallback, useEffect, useState } from "react";
import { InstancesView } from "@/components/views/instances";
import { useSession } from "@/hooks/use-session";
import { useAction } from "@/hooks/use-action";
import type { WhatsAppInstance } from "@/types/dashboard";

function extractQrCode(payload: Record<string, unknown>) {
  const direct = payload.code ?? payload.qrcode ?? payload.base64 ?? payload.pairingCode;
  if (typeof direct === "string" && direct.length > 0) return direct;
  const nested = payload.instance;
  if (nested && typeof nested === "object") {
    const v = (nested as Record<string, unknown>).code ?? (nested as Record<string, unknown>).qrcode;
    if (typeof v === "string" && v.length > 0) return v;
  }
  return null;
}

export default function InstancesPage() {
  const { api, refreshCore } = useSession();
  const { busy, run } = useAction();
  const [instances, setInstances] = useState<WhatsAppInstance[]>([]);
  const [qrImages, setQrImages] = useState<Record<string, string>>({});
  const [connectionPayloads, setConnectionPayloads] = useState<Record<string, string>>({});

  const load = useCallback(async () => { setInstances((await api.instances()).items); }, [api]);
  useEffect(() => { load(); }, [load]);

  return (
    <InstancesView
      instances={instances} qrImages={qrImages} connectionPayloads={connectionPayloads} busy={busy}
      onCreate={(p) => run("create-instance", async () => { await api.createInstance(p); await load(); await refreshCore(); }, "Conexão criada.")}
      onConnect={(i) => run("connect", async () => {
        const r = await api.connectInstance(i.id);
        setConnectionPayloads((c) => ({ ...c, [i.id]: JSON.stringify(r, null, 2) }));
        const code = extractQrCode(r);
        if (code) { const url = await QRCode.toDataURL(code, { margin: 1, width: 220 }); setQrImages((c) => ({ ...c, [i.id]: url })); }
      }, "Conexão solicitada.")}
      onSyncStatus={(i) => run("sync", async () => { await api.syncInstanceStatus(i.id); await load(); }, "Status consultado.")}
      onSyncWebhook={(i) => run("webhook", async () => { await api.syncInstanceWebhook(i.id); }, "Webhook sincronizado.")}
      onRestart={(i) => run("restart", async () => { await api.restartInstance(i.id); await load(); }, "Reiniciada.")}
      onLogout={(i) => run("logout", async () => { await api.logoutInstance(i.id); await load(); }, "Logout enviado.")}
      onDelete={(i) => run("delete", async () => { await api.deleteInstance(i.id); await load(); await refreshCore(); }, "Excluída.")}
    />
  );
}
