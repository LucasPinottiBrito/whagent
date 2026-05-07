"use client";

import { useCallback, useEffect, useState } from "react";
import { InboxView } from "@/components/views/inbox";
import { useSession } from "@/hooks/use-session";
import { useAction } from "@/hooks/use-action";
import type { ConversationDetail, ConversationSummary } from "@/types/dashboard";

export default function InboxPage() {
  const { api, refreshCore } = useSession();
  const { busy, run } = useAction();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ConversationDetail | null>(null);

  const loadList = useCallback(async () => {
    const r = await api.conversations();
    setConversations(r.items);
  }, [api]);

  const loadDetail = useCallback(async (id: string) => {
    setSelectedId(id);
    setDetail(await api.conversation(id));
  }, [api]);

  useEffect(() => { 
    loadList(); 
    const interval = setInterval(() => {
      loadList();
      if (selectedId) {
        api.conversation(selectedId).then(setDetail);
      }
    }, 15000);
    return () => clearInterval(interval);
  }, [loadList, selectedId, api]);

  return (
    <InboxView
      conversations={conversations} selectedId={selectedId} conversation={detail} busy={busy}
      onSelect={(id) => run("select", () => loadDetail(id))}
      onRefresh={() => run("refresh", loadList)}
      onSendHuman={(id, c) => run("send", async () => { await api.sendHumanMessage(id, c); await loadDetail(id); }, "Enviada.")}
      onEnableAi={(id) => run("ai", async () => { await api.enableAi(id); await loadDetail(id); }, "Atendimento automático ligado.")}
      onDisableAi={(id) => run("ai", async () => { await api.disableAi(id); await loadDetail(id); }, "Atendimento automático pausado.")}
      onArchive={(id) => run("archive", async () => { await api.archiveConversation(id); await loadList(); setSelectedId(null); setDetail(null); }, "Arquivada.")}
      onDelete={(id) => run("delete", async () => { await api.deleteConversation(id); await loadList(); setSelectedId(null); setDetail(null); }, "Excluída.")}
    />
  );
}
