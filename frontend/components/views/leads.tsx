"use client";

import { Edit2, RefreshCw, Trash2 } from "lucide-react";
import { useState } from "react";
import { Badge, Button, Dialog, DialogContent, EmptyState, TextField } from "@/components/ui";
import type { LeadSummary } from "@/types/dashboard";

export function LeadsView({
  leads,
  onRefresh,
  onUpdate,
  onDelete,
}: {
  leads: LeadSummary[];
  onRefresh: () => void;
  onUpdate: (id: string, payload: Record<string, unknown>) => void;
  onDelete: (id: string) => void;
}) {
  const [editing, setEditing] = useState<LeadSummary | null>(null);
  const [editStatus, setEditStatus] = useState("");
  const [editScore, setEditScore] = useState("");

  const openEdit = (lead: LeadSummary) => {
    setEditing(lead);
    setEditStatus(lead.status);
    setEditScore(String(lead.score));
  };

  const saveEdit = () => {
    if (!editing) return;
    onUpdate(editing.id, { status: editStatus, score: Number(editScore) });
    setEditing(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">Leads</h1>
          <p className="text-sm text-muted-foreground">Qualificação produzida pelo agente de atendimento.</p>
        </div>
        <Button onClick={onRefresh}><RefreshCw size={15} />Atualizar</Button>
      </div>

      <div className="glass-panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Cliente</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Score</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Interesse</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Pagamento</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Ações</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id} className="border-b border-border hover:bg-accent/50 transition-colors">
                <td className="px-4 py-3 text-foreground">{lead.customer?.name ?? lead.customer?.phone ?? lead.customer_id}</td>
                <td className="px-4 py-3"><Badge tone={lead.status === "qualified" ? "green" : "neutral"}>{lead.status}</Badge></td>
                <td className="px-4 py-3 text-foreground">{lead.score}</td>
                <td className="px-4 py-3 text-muted-foreground">{lead.vehicle_interest ?? "-"}</td>
                <td className="px-4 py-3 text-muted-foreground">{lead.payment_type ?? "-"}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" onClick={() => openEdit(lead)}><Edit2 size={14} /></Button>
                    <Button size="sm" variant="ghost" onClick={() => onDelete(lead.id)}><Trash2 size={14} className="text-destructive" /></Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!leads.length && <EmptyState title="Sem leads" text="Processar uma conversa com IA cria ou atualiza um lead." />}
      </div>

      <Dialog open={!!editing} onOpenChange={(open) => !open && setEditing(null)}>
        <DialogContent title="Editar Lead">
          <div className="grid gap-3">
            <TextField label="Status" value={editStatus} onChange={(e) => setEditStatus(e.target.value)} />
            <TextField label="Score" type="number" value={editScore} onChange={(e) => setEditScore(e.target.value)} />
            <Button variant="primary" onClick={saveEdit}>Salvar</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
