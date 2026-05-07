"use client";

import { useCallback, useEffect, useState } from "react";
import { CompanyView } from "@/components/views/company";
import { useSession } from "@/hooks/use-session";
import { useAction } from "@/hooks/use-action";
import type { Store } from "@/types/dashboard";

export default function CompanyPage() {
  const { api } = useSession();
  const { busy, run } = useAction();
  const [store, setStore] = useState<Store | null>(null);

  const load = useCallback(async () => { setStore(await api.store()); }, [api]);
  useEffect(() => { load(); }, [load]);

  return (
    <CompanyView
      store={store}
      busy={busy}
      onSave={(p) => run("save", async () => { setStore(await api.updateStore(p)); }, "Dados salvos.")}
    />
  );
}
