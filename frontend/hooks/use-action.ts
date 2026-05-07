"use client";

import { useCallback, useState } from "react";
import { toast } from "./use-toast";

function errorMessage(err: unknown) {
  return err instanceof Error ? err.message : "Erro inesperado";
}

export function useAction() {
  const [busy, setBusy] = useState<string | null>(null);

  const run = useCallback(
    async (label: string, action: () => Promise<void>, success?: string) => {
      setBusy(label);
      try {
        await action();
        if (success) {
          toast({
            variant: "success",
            title: "Sucesso",
            description: success,
          });
        }
      } catch (e) {
        toast({
          variant: "destructive",
          title: "Erro",
          description: errorMessage(e),
        });
      } finally {
        setBusy(null);
      }
    },
    []
  );

  return { busy, run };
}
