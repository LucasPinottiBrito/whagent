"use client";

import { useRouter } from "next/navigation";
import { SetupScreen } from "@/components/auth-screens";
import { useSession } from "@/hooks/use-session";
import { useAction } from "@/hooks/use-action";

export default function SetupPage() {
  const router = useRouter();
  const { setSession, api } = useSession();
  const { busy, run } = useAction();

  return (
    <SetupScreen
      needsSetup={null}
      busy={busy}
      onSubmit={(payload) =>
        run("setup", async () => {
          const r = await api.bootstrap(payload);
          setSession(r.access_token);
          router.push("/app/overview");
        })
      }
    />
  );
}
