"use client";

import { Wifi, WifiOff } from "lucide-react";
import { FormEvent, useState } from "react";
import { Button, TextField } from "@/components/ui";

export function LoginScreen({
  health,
  busy,
  onLogin,
}: {
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
