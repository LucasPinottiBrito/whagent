"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { LoadingScreen } from "@/components/auth-screens";

export default function EntryPage() {
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (checked) return;
    (async () => {
      const token = localStorage.getItem("whagent.access_token");
      router.replace(token ? "/app/overview" : "/login");
      setChecked(true);
    })();
  }, [checked, router]);

  return <LoadingScreen />;
}
