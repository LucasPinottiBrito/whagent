"use client";

import { Edit2, RefreshCw, Trash2 } from "lucide-react";
import { useState } from "react";
import { Button, Dialog, DialogContent, EmptyState, TextField } from "@/components/ui";

type CustomerItem = {
  id: string;
  phone: string;
  name: string | null;
  last_seen_at: string | null;
  created_at: string;
};

export function CustomersView({
  customers,
  onRefresh,
  onUpdate,
  onDelete,
}: {
  customers: CustomerItem[];
  onRefresh: () => void;
  onUpdate: (id: string, p: Record<string, unknown>) => void;
  onDelete: (id: string) => void;
}) {
  const [editing, setEditing] = useState<CustomerItem | null>(null);
  const [editName, setEditName] = useState("");
  const [editPhone, setEditPhone] = useState("");

  const openEdit = (c: CustomerItem) => { setEditing(c); setEditName(c.name ?? ""); setEditPhone(c.phone); };
  const saveEdit = () => { if (!editing) return; onUpdate(editing.id, { name: editName, phone: editPhone }); setEditing(null); };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">Clientes</h1>
          <p className="text-sm text-muted-foreground">Contatos registrados pelo atendimento.</p>
        </div>
        <Button onClick={onRefresh}><RefreshCw size={15} />Atualizar</Button>
      </div>

      <div className="glass-panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Nome</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Telefone</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Último contato</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Ações</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((c) => (
              <tr key={c.id} className="border-b border-border hover:bg-accent/50 transition-colors">
                <td className="px-4 py-3 text-foreground">{c.name ?? "-"}</td>
                <td className="px-4 py-3 text-muted-foreground">{c.phone}</td>
                <td className="px-4 py-3 text-muted-foreground text-xs">{c.last_seen_at ? new Date(c.last_seen_at).toLocaleDateString("pt-BR") : "-"}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" onClick={() => openEdit(c)}><Edit2 size={14} /></Button>
                    <Button size="sm" variant="ghost" onClick={() => onDelete(c.id)}><Trash2 size={14} className="text-destructive" /></Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!customers.length && <EmptyState title="Sem clientes" text="Clientes são criados automaticamente via webhook." />}
      </div>

      <Dialog open={!!editing} onOpenChange={(open) => !open && setEditing(null)}>
        <DialogContent title="Editar Cliente">
          <div className="grid gap-3">
            <TextField label="Nome" value={editName} onChange={(e) => setEditName(e.target.value)} />
            <TextField label="Telefone" value={editPhone} onChange={(e) => setEditPhone(e.target.value)} />
            <Button variant="primary" onClick={saveEdit}>Salvar</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
