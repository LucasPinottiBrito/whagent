"use client";

import { CheckCircle2 } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { Button, TextField } from "@/components/ui";
import type { Store } from "@/types/dashboard";

export function CompanyView({
  store,
  busy,
  onSave,
}: {
  store: Store | null;
  busy: string | null;
  onSave: (payload: Partial<Store>) => void;
}) {
  const [name, setName] = useState("");
  const [document, setDocument] = useState("");
  const [phone, setPhone] = useState("");

  useEffect(() => {
    if (!store) return;
    setName(store.name);
    setDocument(store.document ?? "");
    setPhone(store.phone ?? "");
  }, [store]);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSave({ name, document, phone });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Empresa</h1>
        <p className="text-sm text-muted-foreground">Dados usados para operação local.</p>
      </div>
      <div className="glass-panel p-5 max-w-md">
        <form className="grid gap-3" onSubmit={submit}>
          <TextField label="Nome" value={name} onChange={(e) => setName(e.target.value)} required />
          <TextField label="Documento" value={document} onChange={(e) => setDocument(e.target.value)} />
          <TextField label="Telefone" value={phone} onChange={(e) => setPhone(e.target.value)} />
          <Button variant="primary" disabled={busy === "save-store"}><CheckCircle2 size={16} />Salvar empresa</Button>
        </form>
      </div>
    </div>
  );
}
