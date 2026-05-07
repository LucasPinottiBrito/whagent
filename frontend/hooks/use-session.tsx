"use client";

import { useRouter } from "next/navigation";
import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { ApiError, createApiClient } from "@/services/api";
import type { DashboardOverview } from "@/types/dashboard";
import type { CurrentUser } from "@/types/user";

const TOKEN_KEY = "whagent.access_token";

type SessionCtx = {
  token: string | null;
  user: CurrentUser | null;
  health: "ok" | "offline";
  overview: DashboardOverview | null;
  api: ReturnType<typeof createApiClient>;
  setSession: (t: string | null) => void;
  refreshCore: () => Promise<void>;
  refreshHealth: () => Promise<void>;
};

const Ctx = createContext<SessionCtx | null>(null);

export function useSession() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useSession must be inside SessionProvider");
  return ctx;
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [health, setHealth] = useState<"ok" | "offline">("offline");
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [mounted, setMounted] = useState(false);

  const api = useMemo(() => createApiClient(token), [token]);

  const setSession = useCallback((t: string | null) => {
    if (t) localStorage.setItem(TOKEN_KEY, t);
    else { localStorage.removeItem(TOKEN_KEY); setUser(null); }
    setTokenState(t);
  }, []);

  const refreshHealth = useCallback(async () => {
    const pub = createApiClient();
    try { const r = await pub.health(); setHealth(r.status === "ok" ? "ok" : "offline"); }
    catch { setHealth("offline"); }
  }, []);

  const refreshCore = useCallback(async () => {
    if (!token) return;
    try {
      const [me, ov] = await Promise.all([api.me(), api.overview()]);
      setUser(me); setOverview(ov);
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) { setSession(null); router.replace("/login"); }
    }
  }, [api, router, setSession, token]);

  useEffect(() => { setMounted(true); setTokenState(localStorage.getItem(TOKEN_KEY)); refreshHealth(); }, [refreshHealth]);
  useEffect(() => { if (mounted && token) refreshCore(); }, [mounted, refreshCore, token]);

  if (!mounted) return null;

  return (
    <Ctx.Provider value={{ token, user, health, overview, api, setSession, refreshCore, refreshHealth }}>
      {children}
    </Ctx.Provider>
  );
}
