"use client";

import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect } from "react";
import { AppShell, type AppView } from "@/components/app-shell";
import { useSession } from "@/hooks/use-session";
import { useAction } from "@/hooks/use-action";

const viewFromPath: Record<string, AppView> = {
  "/app/overview": "overview",
  "/app/inbox": "inbox",
  "/app/instances": "instances",
  "/app/leads": "leads",
  "/app/users": "users",
  "/app/customers": "customers",
  "/app/company": "company",
  "/app/debug": "debug",
};

export default function AppDashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { token, user, overview, setSession } = useSession();
  const { busy } = useAction();

  useEffect(() => {
    if (token === null) router.replace("/login");
  }, [token, router]);

  if (!token) return null;

  const activeView = viewFromPath[pathname] ?? "overview";

  return (
    <AppShell
      activeView={activeView}
      user={user}
      overview={overview}
      busy={busy}
      onLogout={() => { setSession(null); router.push("/login"); }}
    >
      {children}
    </AppShell>
  );
}
