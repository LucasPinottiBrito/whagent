"use client";

import { Edit2, Plus, RefreshCw, Trash2 } from "lucide-react";
import { FormEvent, useState } from "react";
import { Badge, Button, Dialog, DialogContent, EmptyState, TextField } from "@/components/ui";

type UserItem = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
};

export function UsersView({
  users,
  busy,
  onRefresh,
  onCreate,
  onUpdate,
  onDelete,
}: {
  users: UserItem[];
  busy: string | null;
  onRefresh: () => void;
  onCreate: (p: { email: string; full_name: string; password: string; role: string }) => void;
  onUpdate: (id: string, p: Record<string, unknown>) => void;
  onDelete: (id: string) => void;
}) {
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<UserItem | null>(null);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("salesperson");
  const [editName, setEditName] = useState("");
  const [editRole, setEditRole] = useState("");

  const submitCreate = (e: FormEvent) => {
    e.preventDefault();
    onCreate({ email, full_name: fullName, password, role });
    setShowCreate(false);
    setEmail(""); setFullName(""); setPassword(""); setRole("salesperson");
  };

  const openEdit = (u: UserItem) => { setEditing(u); setEditName(u.full_name); setEditRole(u.role); };
  const saveEdit = () => { if (!editing) return; onUpdate(editing.id, { full_name: editName, role: editRole }); setEditing(null); };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">Usuários</h1>
          <p className="text-sm text-muted-foreground">Gerencie os membros da equipe.</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={onRefresh}><RefreshCw size={15} /></Button>
          <Button variant="primary" onClick={() => setShowCreate(true)}><Plus size={15} />Novo usuário</Button>
        </div>
      </div>

      <div className="glass-panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Nome</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">E-mail</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Role</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-muted-foreground uppercase">Ações</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-border hover:bg-accent/50 transition-colors">
                <td className="px-4 py-3 text-foreground">{u.full_name}</td>
                <td className="px-4 py-3 text-muted-foreground">{u.email}</td>
                <td className="px-4 py-3"><Badge tone={u.role === "admin" ? "blue" : "neutral"}>{u.role}</Badge></td>
                <td className="px-4 py-3"><Badge tone={u.is_active ? "green" : "red"}>{u.is_active ? "ativo" : "inativo"}</Badge></td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" onClick={() => openEdit(u)}><Edit2 size={14} /></Button>
                    <Button size="sm" variant="ghost" onClick={() => onDelete(u.id)}><Trash2 size={14} className="text-destructive" /></Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!users.length && <EmptyState title="Sem usuários" text="Adicione o primeiro membro da equipe." />}
      </div>

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent title="Novo Usuário">
          <form className="grid gap-3" onSubmit={submitCreate}>
            <TextField label="E-mail" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <TextField label="Nome completo" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
            <TextField label="Senha" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <TextField label="Role" value={role} onChange={(e) => setRole(e.target.value)} />
            <Button variant="primary">Criar</Button>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={!!editing} onOpenChange={(open) => !open && setEditing(null)}>
        <DialogContent title="Editar Usuário">
          <div className="grid gap-3">
            <TextField label="Nome" value={editName} onChange={(e) => setEditName(e.target.value)} />
            <TextField label="Role" value={editRole} onChange={(e) => setEditRole(e.target.value)} />
            <Button variant="primary" onClick={saveEdit}>Salvar</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
