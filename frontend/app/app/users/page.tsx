"use client";

import { useCallback, useEffect, useState } from "react";
import { UsersView } from "@/components/views/users";
import { useSession } from "@/hooks/use-session";
import { useAction } from "@/hooks/use-action";

export default function UsersPage() {
  const { api } = useSession();
  const { busy, run } = useAction();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [users, setUsers] = useState<any[]>([]);

  const load = useCallback(async () => { setUsers((await api.users()).items); }, [api]);
  useEffect(() => { load(); }, [load]);

  return (
    <UsersView
      users={users}
      busy={busy}
      onRefresh={() => run("refresh", load)}
      onCreate={(p) => run("create", async () => { await api.createUser(p); await load(); }, "Usuário criado.")}
      onUpdate={(id, p) => run("update", async () => { await api.updateUser(id, p); await load(); }, "Atualizado.")}
      onDelete={(id) => run("delete", async () => { await api.deleteUser(id); await load(); }, "Excluído.")}
    />
  );
}
