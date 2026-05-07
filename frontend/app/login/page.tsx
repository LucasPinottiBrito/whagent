"use client";

import { useRouter } from "next/navigation";
import { LoginScreen } from "@/components/auth-screens";
import { useSession } from "@/hooks/use-session";
import { useAction } from "@/hooks/use-action";

export default function LoginPage() {
  const router = useRouter();
  const { health, setSession, api } = useSession();
  const { busy, run } = useAction();

  return (
    <LoginScreen
      needsSetup={false}
      health={health}
      busy={busy}
      onLogin={(email, password) =>
        run("login", async () => {
          const r = await api.login(email, password);
          setSession(r.access_token);
          router.push("/app/overview");
        })
      }
    />
  );
}
