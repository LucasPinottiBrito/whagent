"use client";

import { useCallback, useEffect, useState } from "react";
import { LeadsView } from "@/components/views/leads";
import { useSession } from "@/hooks/use-session";
import { useAction } from "@/hooks/use-action";
import type { LeadSummary } from "@/types/dashboard";

export default function LeadsPage() {
  const { api } = useSession();
  const { run } = useAction();
  const [leads, setLeads] = useState<LeadSummary[]>([]);

  const load = useCallback(async () => { setLeads((await api.leads()).items); }, [api]);
  useEffect(() => { load(); }, [load]);

  return (
    <LeadsView
      leads={leads}
      onRefresh={() => run("refresh", load)}
      onUpdate={(id, p) => run("update", async () => { await api.updateLead(id, p); await load(); }, "Lead atualizado.")}
      onDelete={(id) => run("delete", async () => { await api.deleteLead(id); await load(); }, "Lead excluído.")}
    />
  );
}
