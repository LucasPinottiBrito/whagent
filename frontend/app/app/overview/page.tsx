"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { OverviewView } from "@/components/views/overview";
import { useSession } from "@/hooks/use-session";
import type { ConversationSummary } from "@/types/dashboard";

export default function OverviewPage() {
  const router = useRouter();
  const { api, overview } = useSession();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);

  useEffect(() => {
    api.conversations().then((r) => setConversations(r.items)).catch(() => {});
  }, [api]);

  return (
    <OverviewView
      overview={overview}
      conversations={conversations}
      onOpenInbox={() => router.push("/app/inbox")}
    />
  );
}
