"use client";

import { Bot, Clock3, MessageSquareText } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from "recharts";
import { Badge, Button, EmptyState, MetricTile, StatusDot } from "@/components/ui";
import type { ConversationSummary, DashboardOverview } from "@/types/dashboard";

export function OverviewView({
  overview,
  conversations,
  onOpenInbox,
}: {
  overview: DashboardOverview | null;
  conversations: ConversationSummary[];
  onOpenInbox: () => void;
}) {
  const chartData = [
    { name: "Automático", value: overview?.ai_active_conversations ?? 0, color: "#22c55e" },
    { name: "Manual", value: overview?.human_active_conversations ?? 0, color: "#f59e0b" },
    { name: "Aguardando", value: overview?.pending_conversations ?? 0, color: "#22d3ee" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-foreground">Operação de Vendas</h1>
          <p className="text-sm text-muted-foreground">Visão geral de funil, leads e canais de atendimento.</p>
        </div>
        <Button variant="primary" onClick={onOpenInbox}>
          <MessageSquareText size={16} />
          Abrir atendimento
        </Button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricTile label="Conversas" value={overview?.conversations_total ?? 0} detail="na plataforma" />
        <MetricTile label="Leads" value={overview?.leads_total ?? 0} detail="qualificados" />
        <MetricTile label="Conexões" value={overview?.instances_total ?? 0} detail="ativas" />
        <MetricTile label="Pendentes" value={overview?.pending_conversations ?? 0} detail="aguardando resposta" />
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="glass-panel p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-foreground">Distribuição de Atendimento</h2>
            <Bot size={17} className="text-muted-foreground" />
          </div>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" width={80} tick={{ fill: "#a1a1aa", fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ background: "#111113", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: "#fafafa" }}
                />
                <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={20}>
                  {chartData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2">
            {chartData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <StatusDot tone={item.color === "#22c55e" ? "green" : item.color === "#f59e0b" ? "amber" : "blue"} />
                  <span className="text-muted-foreground">{item.name}</span>
                </div>
                <strong className="text-foreground">{item.value}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-foreground">Últimas conversas</h2>
            <Clock3 size={17} className="text-muted-foreground" />
          </div>
          {conversations.length ? (
            <div className="space-y-2">
              {conversations.slice(0, 5).map((c) => (
                <div key={c.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                  <span className="text-sm text-foreground truncate">{c.customer.name ?? c.customer.phone}</span>
                  <Badge tone={c.ai_enabled ? "green" : "amber"}>{c.status}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="Sem conversas" text="Abra a área de atendimento para sincronizar." />
          )}
        </div>
      </div>
    </div>
  );
}
