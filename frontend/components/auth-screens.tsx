"use client";

import { Wifi, WifiOff } from "lucide-react";
import { FormEvent, useState } from "react";
import { Button, TextField } from "@/components/ui";

export function SetupScreen({
  needsSetup,
  busy,
  onSubmit,
}: {
  needsSetup: boolean | null;
  busy: string | null;
  onSubmit: (payload: {
    store_name: string;
    store_slug: string;
    store_document?: string;
    store_phone?: string;
    admin_email: string;
    admin_full_name: string;
    admin_password: string;
  }) => void;
}) {
  const [storeName, setStoreName] = useState("Loja Demo");
  const [storeSlug, setStoreSlug] = useState("loja-demo");
  const [document, setDocument] = useState("");
  const [phone, setPhone] = useState("5511999999999");
  const [email, setEmail] = useState("admin@example.com");
  const [fullName, setFullName] = useState("Admin Demo");
  const [password, setPassword] = useState("admin123");

  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit({
      store_name: storeName,
      store_slug: storeSlug,
      store_document: document || undefined,
      store_phone: phone || undefined,
      admin_email: email,
      admin_full_name: fullName,
      admin_password: password,
    });
  };

  return (
    <main className="flex items-center justify-center min-h-screen bg-background p-4">
      <section className="glass-panel w-full max-w-md p-8 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center text-primary font-bold text-lg">W</div>
          <div>
            <h1 className="text-lg font-semibold text-foreground">Criar primeira empresa</h1>
            <p className="text-xs text-muted-foreground">Bootstrap inicial — após existir um usuário, esta rota fica bloqueada.</p>
          </div>
        </div>
        {needsSetup === false && (
          <div className="rounded-lg bg-accent p-3 text-sm text-foreground">Setup já foi executado. Use o login.</div>
        )}
        <form className="grid gap-3" onSubmit={submit}>
          <TextField label="Empresa" value={storeName} onChange={(e) => setStoreName(e.target.value)} required />
          <TextField label="Slug" value={storeSlug} onChange={(e) => setStoreSlug(e.target.value)} required />
          <TextField label="Documento" value={document} onChange={(e) => setDocument(e.target.value)} />
          <TextField label="Telefone da loja" value={phone} onChange={(e) => setPhone(e.target.value)} />
          <TextField label="E-mail admin" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <TextField label="Nome admin" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          <TextField label="Senha" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Button variant="primary" loading={busy === "setup"} disabled={busy === "setup"}>{busy === "setup" ? "Criando..." : "Criar e entrar"}</Button>
        </form>
      </section>
    </main>
  );
}

export function LoginScreen({
  needsSetup,
  health,
  busy,
  onLogin,
}: {
  needsSetup: boolean | null;
  health: "ok" | "offline";
  busy: string | null;
  onLogin: (email: string, password: string) => void;
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submit = (e: FormEvent) => {
    e.preventDefault();
    onLogin(email, password);
  };

  return (
    <main className="flex items-center justify-center min-h-screen bg-background p-4">
      <section className="glass-panel w-full max-w-sm p-8 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center text-primary font-bold text-lg">W</div>
          <div>
            <h1 className="text-lg font-semibold text-foreground">Entrar no Whagent</h1>
            <p className="text-xs text-muted-foreground">Acesse com seu e-mail e senha.</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          {health === "ok" ? <Wifi size={14} className="text-success" /> : <WifiOff size={14} className="text-destructive" />}
          Backend {health === "ok" ? "online" : "offline"}
        </div>
        {needsSetup && <div className="rounded-lg bg-accent p-3 text-sm text-foreground">Nenhum usuário encontrado. Execute o setup inicial.</div>}
        <form className="grid gap-3" onSubmit={submit}>
          <TextField label="E-mail" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <TextField label="Senha" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Button variant="primary" loading={busy === "login"} disabled={busy === "login"}>{busy === "login" ? "Entrando..." : "Entrar"}</Button>
        </form>
      </section>
    </main>
  );
}

export function LoadingScreen() {
  return (
    <main className="flex items-center justify-center min-h-screen bg-background">
      <div className="text-center space-y-3">
        <div className="w-12 h-12 mx-auto rounded-xl bg-primary/20 flex items-center justify-center text-primary font-bold text-xl animate-pulse">W</div>
        <p className="text-sm text-muted-foreground">Carregando Whagent...</p>
      </div>
    </main>
  );
}
