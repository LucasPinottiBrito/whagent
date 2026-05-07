"use client";

import { useCallback, useEffect, useState } from "react";
import { DebugView } from "@/components/views/debug";
import { useSession } from "@/hooks/use-session";
import { useAction } from "@/hooks/use-action";
import type { RuntimeState, WhatsAppInstance } from "@/types/dashboard";

export default function DebugPage() {
  const { api, user, refreshCore } = useSession();
  const { busy, run } = useAction();
  const [runtime, setRuntime] = useState<RuntimeState | null>(null);
  const [instances, setInstances] = useState<WhatsAppInstance[]>([]);

  const load = useCallback(async () => {
    try { setRuntime(await api.runtime()); } catch { setRuntime(null); }
    setInstances((await api.instances()).items);
  }, [api]);

  useEffect(() => { load(); }, [load]);

  if (user?.role !== "admin") return <p className="text-muted-foreground p-4">Acesso restrito a admins.</p>;

  return (
    <DebugView
      runtime={runtime} instances={instances} busy={busy}
      onRuntime={(p) => run("runtime", async () => { setRuntime(await api.updateRuntime(p)); }, "Runtime atualizado.")}
      onSimulate={(p) => run("simulate", async () => { await api.simulateInbound(p); await refreshCore(); }, "Simulado.")}
    />
  );
}
