"use client";

import { useCallback, useEffect, useState } from "react";
import { CustomersView } from "@/components/views/customers";
import { useSession } from "@/hooks/use-session";
import { useAction } from "@/hooks/use-action";

export default function CustomersPage() {
  const { api } = useSession();
  const { run } = useAction();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [customers, setCustomers] = useState<any[]>([]);

  const load = useCallback(async () => { setCustomers((await api.customers()).items); }, [api]);
  useEffect(() => { load(); }, [load]);

  return (
    <CustomersView
      customers={customers}
      onRefresh={() => run("refresh", load)}
      onUpdate={(id, p) => run("update", async () => { await api.updateCustomer(id, p); await load(); }, "Atualizado.")}
      onDelete={(id) => run("delete", async () => { await api.deleteCustomer(id); await load(); }, "Excluído.")}
    />
  );
}
