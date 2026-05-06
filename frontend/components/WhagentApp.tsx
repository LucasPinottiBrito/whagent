"use client";

import {
  Activity,
  Bot,
  Building2,
  Car,
  CheckCircle2,
  Clock3,
  LogOut,
  MessageSquareText,
  Play,
  Plus,
  Power,
  RefreshCw,
  Send,
  Settings,
  ShieldCheck,
  Smartphone,
  UserRound,
  UsersRound,
  Wifi,
  WifiOff,
  Zap,
} from "lucide-react";
import { useRouter } from "next/navigation";
import QRCode from "qrcode";
import {
  FormEvent,
  ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { Badge, Button, EmptyState, MetricTile, TextArea, TextField } from "@/components/ui";
import { ApiError, createApiClient } from "@/services/api";
import type {
  ConversationDetail,
  ConversationSummary,
  DashboardOverview,
  LeadSummary,
  RuntimeState,
  Store,
  WhatsAppInstance,
} from "@/types/dashboard";
import type { CurrentUser } from "@/types/user";

type AppView =
  | "entry"
  | "setup"
  | "login"
  | "overview"
  | "inbox"
  | "instances"
  | "leads"
  | "company"
  | "debug";

type Notice = {
  tone: "success" | "error" | "neutral";
  text: string;
} | null;

const TOKEN_KEY = "whagent.access_token";

const navItems: Array<{
  view: AppView;
  href: string;
  label: string;
  icon: typeof Activity;
}> = [
  { view: "overview", href: "/app/overview", label: "Visão geral", icon: Activity },
  { view: "inbox", href: "/app/inbox", label: "Atendimento", icon: MessageSquareText },
  { view: "instances", href: "/app/instances", label: "Instâncias", icon: Smartphone },
  { view: "leads", href: "/app/leads", label: "Leads", icon: UsersRound },
  { view: "company", href: "/app/company", label: "Empresa", icon: Building2 },
  { view: "debug", href: "/app/debug", label: "Debug", icon: Settings },
];

export function WhagentApp({ initialView }: { initialView: AppView }) {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [health, setHealth] = useState<"ok" | "offline">("offline");
  const [setupNeedsRun, setSetupNeedsRun] = useState<boolean | null>(null);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [store, setStore] = useState<Store | null>(null);
  const [instances, setInstances] = useState<WhatsAppInstance[]>([]);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [leads, setLeads] = useState<LeadSummary[]>([]);
  const [runtime, setRuntime] = useState<RuntimeState | null>(null);
  const [notice, setNotice] = useState<Notice>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [qrImages, setQrImages] = useState<Record<string, string>>({});
  const [connectionPayloads, setConnectionPayloads] = useState<Record<string, string>>({});

  const api = useMemo(() => createApiClient(token), [token]);

  const setSession = useCallback((accessToken: string | null) => {
    if (accessToken) {
      localStorage.setItem(TOKEN_KEY, accessToken);
    } else {
      localStorage.removeItem(TOKEN_KEY);
      setUser(null);
    }
    setToken(accessToken);
  }, []);

  const refreshPublicStatus = useCallback(async () => {
    const publicApi = createApiClient();
    const [healthResult, setupResult] = await Promise.allSettled([
      publicApi.health(),
      publicApi.setupStatus(),
    ]);
    setHealth(
      healthResult.status === "fulfilled" && healthResult.value.status === "ok"
        ? "ok"
        : "offline",
    );
    if (setupResult.status === "fulfilled") {
      setSetupNeedsRun(setupResult.value.needs_setup);
    }
  }, []);

  const refreshCore = useCallback(async () => {
    if (!token) return;
    try {
      const [meResult, overviewResult] = await Promise.all([api.me(), api.overview()]);
      setUser(meResult);
      setOverview(overviewResult);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setSession(null);
        router.replace("/login");
        return;
      }
      setNotice({ tone: "error", text: errorMessage(error) });
    }
  }, [api, router, setSession, token]);

  const refreshInstances = useCallback(async () => {
    if (!token) return;
    const result = await api.instances();
    setInstances(result.items);
  }, [api, token]);

  const refreshConversations = useCallback(async () => {
    if (!token) return;
    const result = await api.conversations();
    setConversations(result.items);
    const nextSelected = selectedConversationId ?? result.items[0]?.id ?? null;
    setSelectedConversationId(nextSelected);
    if (nextSelected) {
      setConversation(await api.conversation(nextSelected));
    } else {
      setConversation(null);
    }
  }, [api, selectedConversationId, token]);

  const refreshLeads = useCallback(async () => {
    if (!token) return;
    const result = await api.leads();
    setLeads(result.items);
  }, [api, token]);

  const refreshStore = useCallback(async () => {
    if (!token) return;
    setStore(await api.store());
  }, [api, token]);

  const refreshRuntime = useCallback(async () => {
    if (!token) return;
    try {
      setRuntime(await api.runtime());
    } catch (error) {
      setRuntime(null);
      setNotice({ tone: "error", text: `Debug indisponível: ${errorMessage(error)}` });
    }
  }, [api, token]);

  useEffect(() => {
    setMounted(true);
    setToken(localStorage.getItem(TOKEN_KEY));
    refreshPublicStatus();
  }, [refreshPublicStatus]);

  useEffect(() => {
    if (initialView === "entry" && setupNeedsRun !== null) {
      if (setupNeedsRun) router.replace("/setup");
      else if (token) router.replace("/app/overview");
      else router.replace("/login");
    }
  }, [initialView, router, setupNeedsRun, token]);

  useEffect(() => {
    const protectedView = !["entry", "setup", "login"].includes(initialView);
    if (mounted && protectedView && !token) {
      router.replace("/login");
    }
  }, [initialView, mounted, router, token]);

  useEffect(() => {
    if (!token) return;
    refreshCore();
  }, [refreshCore, token]);

  useEffect(() => {
    if (!token) return;
    if (initialView === "instances" || initialView === "debug") refreshInstances();
    if (initialView === "inbox") refreshConversations();
    if (initialView === "leads") refreshLeads();
    if (initialView === "company") refreshStore();
    if (initialView === "debug") refreshRuntime();
  }, [
    initialView,
    refreshConversations,
    refreshInstances,
    refreshLeads,
    refreshRuntime,
    refreshStore,
    token,
  ]);

  const runAction = async (label: string, action: () => Promise<void>, success?: string) => {
    setBusy(label);
    setNotice(null);
    try {
      await action();
      if (success) setNotice({ tone: "success", text: success });
    } catch (error) {
      setNotice({ tone: "error", text: errorMessage(error) });
    } finally {
      setBusy(null);
    }
  };

  const logout = () => {
    setSession(null);
    router.push("/login");
  };

  if (!mounted || initialView === "entry") {
    return <LoadingScreen />;
  }

  if (initialView === "setup") {
    return (
      <SetupScreen
        needsSetup={setupNeedsRun}
        busy={busy}
        notice={notice}
        onSubmit={(payload) =>
          runAction("setup", async () => {
            const result = await api.bootstrap(payload);
            setSession(result.access_token);
            setUser(result.user);
            router.push("/app/overview");
          })
        }
      />
    );
  }

  if (initialView === "login") {
    return (
      <LoginScreen
        needsSetup={setupNeedsRun}
        health={health}
        busy={busy}
        notice={notice}
        onLogin={(email, password) =>
          runAction("login", async () => {
            const result = await api.login(email, password);
            setSession(result.access_token);
            router.push("/app/overview");
          })
        }
      />
    );
  }

  return (
    <AppShell
      activeView={initialView}
      user={user}
      health={health}
      overview={overview}
      notice={notice}
      busy={busy}
      onLogout={logout}
      onRefresh={() =>
        runAction("refresh", async () => {
          await refreshPublicStatus();
          await refreshCore();
          if (initialView === "instances") await refreshInstances();
          if (initialView === "inbox") await refreshConversations();
          if (initialView === "leads") await refreshLeads();
          if (initialView === "company") await refreshStore();
          if (initialView === "debug") await refreshRuntime();
        })
      }
    >
      {initialView === "overview" ? (
        <OverviewView overview={overview} conversations={conversations} onOpenInbox={() => router.push("/app/inbox")} />
      ) : null}
      {initialView === "instances" ? (
        <InstancesView
          instances={instances}
          qrImages={qrImages}
          connectionPayloads={connectionPayloads}
          busy={busy}
          onCreate={(payload) =>
            runAction("create-instance", async () => {
              await api.createInstance(payload);
              await refreshInstances();
              await refreshCore();
            }, "Instância criada e registrada no backend.")
          }
          onConnect={(instance) =>
            runAction("connect-instance", async () => {
              const result = await api.connectInstance(instance.id);
              setConnectionPayloads((current) => ({
                ...current,
                [instance.id]: JSON.stringify(result, null, 2),
              }));
              const code = extractQrCode(result);
              if (code) {
                const dataUrl = await QRCode.toDataURL(code, { margin: 1, width: 220 });
                setQrImages((current) => ({ ...current, [instance.id]: dataUrl }));
              }
            }, "Conexão solicitada na Evolution.")
          }
          onSyncStatus={(instance) =>
            runAction("sync-status", async () => {
              await api.syncInstanceStatus(instance.id);
              await refreshInstances();
            }, "Status consultado na Evolution.")
          }
          onSyncWebhook={(instance) =>
            runAction("sync-webhook", async () => {
              await api.syncInstanceWebhook(instance.id);
            }, "Webhook sincronizado.")
          }
          onRestart={(instance) =>
            runAction("restart-instance", async () => {
              await api.restartInstance(instance.id);
              await refreshInstances();
            }, "Instância reiniciada.")
          }
          onLogout={(instance) =>
            runAction("logout-instance", async () => {
              await api.logoutInstance(instance.id);
              await refreshInstances();
              await refreshCore();
            }, "Logout enviado para a Evolution.")
          }
        />
      ) : null}
      {initialView === "inbox" ? (
        <InboxView
          conversations={conversations}
          selectedId={selectedConversationId}
          conversation={conversation}
          busy={busy}
          onSelect={(id) =>
            runAction("select-conversation", async () => {
              setSelectedConversationId(id);
              setConversation(await api.conversation(id));
            })
          }
          onRefresh={() => runAction("refresh-inbox", refreshConversations)}
          onSendHuman={(id, content) =>
            runAction("send-human", async () => {
              await api.sendHumanMessage(id, content);
              await refreshConversations();
            }, "Mensagem humana enviada.")
          }
          onEnableAi={(id) =>
            runAction("enable-ai", async () => {
              await api.enableAi(id);
              await refreshConversations();
            }, "IA devolvida para a conversa.")
          }
          onDisableAi={(id) =>
            runAction("disable-ai", async () => {
              await api.disableAi(id);
              await refreshConversations();
            }, "IA pausada para a conversa.")
          }
          onProcessNow={(id) =>
            runAction("process-now", async () => {
              await api.processNow(id);
              await refreshConversations();
              await refreshCore();
            }, "Processamento executado.")
          }
        />
      ) : null}
      {initialView === "leads" ? (
        <LeadsView leads={leads} onRefresh={() => runAction("refresh-leads", refreshLeads)} />
      ) : null}
      {initialView === "company" ? (
        <CompanyView
          store={store}
          busy={busy}
          onSave={(payload) =>
            runAction("save-store", async () => {
              setStore(await api.updateStore(payload));
            }, "Dados da empresa salvos.")
          }
        />
      ) : null}
      {initialView === "debug" ? (
        <DebugView
          runtime={runtime}
          instances={instances}
          busy={busy}
          onRuntime={(payload) =>
            runAction("runtime", async () => {
              setRuntime(await api.updateRuntime(payload));
            }, "Runtime atualizado.")
          }
          onSimulate={(payload) =>
            runAction("simulate", async () => {
              await api.simulateInbound(payload);
              await refreshConversations();
              await refreshCore();
            }, "Mensagem simulada recebida.")
          }
        />
      ) : null}
    </AppShell>
  );
}

function LoadingScreen() {
  return (
    <main className="auth-shell">
      <section className="auth-panel compact">
        <div className="brand-mark">W</div>
        <h1>Carregando Whagent</h1>
        <p>Preparando o painel operacional.</p>
      </section>
    </main>
  );
}

function SetupScreen({
  needsSetup,
  busy,
  notice,
  onSubmit,
}: {
  needsSetup: boolean | null;
  busy: string | null;
  notice: Notice;
  onSubmit: (payload: {
    store_name: string;
    store_slug: string;
    store_document?: string;
    store_phone?: string;
    admin_email: string;
    admin_full_name: string;
    admin_password: string;
  }) => void;
}) {
  const [storeName, setStoreName] = useState("Loja Demo");
  const [storeSlug, setStoreSlug] = useState("loja-demo");
  const [document, setDocument] = useState("");
  const [phone, setPhone] = useState("5511999999999");
  const [email, setEmail] = useState("admin@example.com");
  const [fullName, setFullName] = useState("Admin Demo");
  const [password, setPassword] = useState("admin123");

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onSubmit({
      store_name: storeName,
      store_slug: storeSlug,
      store_document: document || undefined,
      store_phone: phone || undefined,
      admin_email: email,
      admin_full_name: fullName,
      admin_password: password,
    });
  };

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <div className="auth-heading">
          <div className="brand-mark">W</div>
          <div>
            <h1>Criar primeira empresa</h1>
            <p>Bootstrap inicial: depois que existir um usuário, esta rota fica bloqueada.</p>
          </div>
        </div>
        {needsSetup === false ? (
          <NoticeBox notice={{ tone: "neutral", text: "Setup já foi executado. Use o login." }} />
        ) : null}
        <form className="form-grid" onSubmit={submit}>
          <TextField label="Empresa" value={storeName} onChange={(event) => setStoreName(event.target.value)} required />
          <TextField label="Slug" value={storeSlug} onChange={(event) => setStoreSlug(event.target.value)} required />
          <TextField label="Documento" value={document} onChange={(event) => setDocument(event.target.value)} />
          <TextField label="Telefone da loja" value={phone} onChange={(event) => setPhone(event.target.value)} />
          <TextField label="E-mail admin" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          <TextField label="Nome admin" value={fullName} onChange={(event) => setFullName(event.target.value)} required />
          <TextField label="Senha" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          <Button variant="primary" disabled={busy === "setup"}>{busy === "setup" ? "Criando..." : "Criar e entrar"}</Button>
        </form>
        <NoticeBox notice={notice} />
      </section>
    </main>
  );
}

function LoginScreen({
  needsSetup,
  health,
  busy,
  notice,
  onLogin,
}: {
  needsSetup: boolean | null;
  health: "ok" | "offline";
  busy: string | null;
  notice: Notice;
  onLogin: (email: string, password: string) => void;
}) {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("admin123");

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onLogin(email, password);
  };

  return (
    <main className="auth-shell">
      <section className="auth-panel compact">
        <div className="auth-heading">
          <div className="brand-mark">W</div>
          <div>
            <h1>Entrar no Whagent</h1>
            <p>Use o usuário local criado no setup ou pelo seed.</p>
          </div>
        </div>
        <div className="status-strip">
          {health === "ok" ? <Wifi size={16} /> : <WifiOff size={16} />}
          Backend {health === "ok" ? "online" : "offline"}
        </div>
        {needsSetup ? <NoticeBox notice={{ tone: "neutral", text: "Nenhum usuário encontrado. Execute o setup inicial." }} /> : null}
        <form className="form-grid" onSubmit={submit}>
          <TextField label="E-mail" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          <TextField label="Senha" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          <Button variant="primary" disabled={busy === "login"}>{busy === "login" ? "Entrando..." : "Entrar"}</Button>
        </form>
        <NoticeBox notice={notice} />
      </section>
    </main>
  );
}

function AppShell({
  activeView,
  user,
  health,
  overview,
  notice,
  busy,
  children,
  onLogout,
  onRefresh,
}: {
  activeView: AppView;
  user: CurrentUser | null;
  health: "ok" | "offline";
  overview: DashboardOverview | null;
  notice: Notice;
  busy: string | null;
  children: ReactNode;
  onLogout: () => void;
  onRefresh: () => void;
}) {
  const router = useRouter();
  return (
    <main className="app-frame">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">W</div>
          <div>
            <strong>Whagent</strong>
            <span>Atendimento IA</span>
          </div>
        </div>
        <nav className="nav-list" aria-label="Navegação principal">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.href}
                className={activeView === item.view ? "nav-item active" : "nav-item"}
                onClick={() => router.push(item.href)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <div className="mini-stat">
            <span>Conversas</span>
            <strong>{overview?.conversations_total ?? 0}</strong>
          </div>
          <div className="mini-stat">
            <span>Leads</span>
            <strong>{overview?.leads_total ?? 0}</strong>
          </div>
        </div>
      </aside>
      <section className="workspace">
        <header className="topbar">
          <div>
            <strong>{pageTitle(activeView)}</strong>
            <span>{user ? `${user.full_name} - ${user.role}` : "Sessão local"}</span>
          </div>
          <div className="topbar-actions">
            <span className={health === "ok" ? "status-pill online" : "status-pill offline"}>
              {health === "ok" ? <Wifi size={15} /> : <WifiOff size={15} />}
              Backend
            </span>
            <Button onClick={onRefresh} disabled={busy === "refresh"}>
              <RefreshCw size={15} />
              Atualizar
            </Button>
            <Button onClick={onLogout} variant="ghost">
              <LogOut size={15} />
              Sair
            </Button>
          </div>
        </header>
        <NoticeBox notice={notice} />
        {children}
      </section>
    </main>
  );
}

function OverviewView({
  overview,
  conversations,
  onOpenInbox,
}: {
  overview: DashboardOverview | null;
  conversations: ConversationSummary[];
  onOpenInbox: () => void;
}) {
  return (
    <div className="view-stack">
      <section className="page-header">
        <div>
          <h1>Operação da loja</h1>
          <p>Resumo do atendimento, IA, instâncias e leads sem abrir banco ou terminal.</p>
        </div>
        <Button variant="primary" onClick={onOpenInbox}>
          <MessageSquareText size={16} />
          Abrir atendimento
        </Button>
      </section>
      <section className="metrics-grid">
        <MetricTile label="Conversas" value={overview?.conversations_total ?? 0} detail="total aberto no backend" />
        <MetricTile label="Leads" value={overview?.leads_total ?? 0} detail="qualificados pelo agente" />
        <MetricTile label="Instâncias" value={overview?.instances_total ?? 0} detail="Evolution controladas" />
        <MetricTile label="Pendentes" value={overview?.pending_conversations ?? 0} detail="aguardando debounce/worker" />
      </section>
      <section className="split-grid">
        <div className="panel">
          <div className="panel-heading">
            <h2>Estado da IA</h2>
            <Bot size={18} />
          </div>
          <div className="stacked-bars">
            <StatusRow label="IA ativa" value={overview?.ai_active_conversations ?? 0} tone="green" />
            <StatusRow label="Humano ativo" value={overview?.human_active_conversations ?? 0} tone="amber" />
            <StatusRow label="Processamento pendente" value={overview?.pending_conversations ?? 0} tone="blue" />
          </div>
        </div>
        <div className="panel">
          <div className="panel-heading">
            <h2>Últimas conversas carregadas</h2>
            <Clock3 size={18} />
          </div>
          {conversations.length ? (
            <div className="compact-list">
              {conversations.slice(0, 4).map((conversation) => (
                <div key={conversation.id} className="compact-row">
                  <span>{conversation.customer.name ?? conversation.customer.phone}</span>
                  <Badge tone={conversation.ai_enabled ? "green" : "amber"}>{conversation.status}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="Sem conversas carregadas" text="Abra a área de atendimento para sincronizar a lista." />
          )}
        </div>
      </section>
    </div>
  );
}

function InstancesView({
  instances,
  qrImages,
  connectionPayloads,
  busy,
  onCreate,
  onConnect,
  onSyncStatus,
  onSyncWebhook,
  onRestart,
  onLogout,
}: {
  instances: WhatsAppInstance[];
  qrImages: Record<string, string>;
  connectionPayloads: Record<string, string>;
  busy: string | null;
  onCreate: (payload: { instance_name: string; phone?: string; webhook_secret?: string }) => void;
  onConnect: (instance: WhatsAppInstance) => void;
  onSyncStatus: (instance: WhatsAppInstance) => void;
  onSyncWebhook: (instance: WhatsAppInstance) => void;
  onRestart: (instance: WhatsAppInstance) => void;
  onLogout: (instance: WhatsAppInstance) => void;
}) {
  const [name, setName] = useState("loja-principal");
  const [phone, setPhone] = useState("5511999999999");
  const [secret, setSecret] = useState("");
  const submit = (event: FormEvent) => {
    event.preventDefault();
    onCreate({ instance_name: name, phone: phone || undefined, webhook_secret: secret || undefined });
  };

  return (
    <div className="view-stack">
      <section className="page-header">
        <div>
          <h1>Instâncias WhatsApp</h1>
          <p>Crie, conecte e sincronize Evolution sem acessar o container.</p>
        </div>
      </section>
      <section className="panel">
        <form className="instance-form" onSubmit={submit}>
          <TextField label="Nome da instância" value={name} onChange={(event) => setName(event.target.value)} required />
          <TextField label="Telefone" value={phone} onChange={(event) => setPhone(event.target.value)} />
          <TextField label="Webhook secret opcional" value={secret} onChange={(event) => setSecret(event.target.value)} />
          <Button variant="primary" disabled={busy === "create-instance"}>
            <Plus size={16} />
            Criar instância
          </Button>
        </form>
      </section>
      <section className="instance-grid">
        {instances.map((instance) => (
          <article className="instance-panel" key={instance.id}>
            <div className="instance-main">
              <div>
                <h2>{instance.instance_name}</h2>
                <p>{instance.phone ?? "telefone não informado"}</p>
              </div>
              <Badge tone={instance.active ? "green" : "red"}>{instance.active ? "ativa" : "desconectada"}</Badge>
            </div>
            <div className="instance-actions">
              <Button onClick={() => onConnect(instance)}><Zap size={15} />Conectar</Button>
              <Button onClick={() => onSyncStatus(instance)}><RefreshCw size={15} />Status</Button>
              <Button onClick={() => onSyncWebhook(instance)}><ShieldCheck size={15} />Webhook</Button>
              <Button onClick={() => onRestart(instance)}><Power size={15} />Restart</Button>
              <Button variant="danger" onClick={() => onLogout(instance)}><LogOut size={15} />Logout</Button>
            </div>
            {qrImages[instance.id] ? (
              <div className="qr-box">
                <img src={qrImages[instance.id]} alt={`QR code da instância ${instance.instance_name}`} />
              </div>
            ) : null}
            {connectionPayloads[instance.id] ? (
              <pre className="payload-box">{connectionPayloads[instance.id]}</pre>
            ) : null}
          </article>
        ))}
        {!instances.length ? (
          <EmptyState title="Nenhuma instância" text="Crie a primeira instância para receber webhooks e enviar mensagens." />
        ) : null}
      </section>
    </div>
  );
}

function InboxView({
  conversations,
  selectedId,
  conversation,
  busy,
  onSelect,
  onRefresh,
  onSendHuman,
  onEnableAi,
  onDisableAi,
  onProcessNow,
}: {
  conversations: ConversationSummary[];
  selectedId: string | null;
  conversation: ConversationDetail | null;
  busy: string | null;
  onSelect: (id: string) => void;
  onRefresh: () => void;
  onSendHuman: (id: string, content: string) => void;
  onEnableAi: (id: string) => void;
  onDisableAi: (id: string) => void;
  onProcessNow: (id: string) => void;
}) {
  const [message, setMessage] = useState("");
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!conversation || !message.trim()) return;
    onSendHuman(conversation.id, message);
    setMessage("");
  };

  return (
    <div className="inbox-layout">
      <section className="conversation-list">
        <div className="panel-heading">
          <h2>Conversas</h2>
          <Button onClick={onRefresh}><RefreshCw size={15} /></Button>
        </div>
        {conversations.map((item) => (
          <button
            key={item.id}
            className={selectedId === item.id ? "conversation-row active" : "conversation-row"}
            onClick={() => onSelect(item.id)}
          >
            <span>{item.customer.name ?? item.customer.phone}</span>
            <small>{item.last_message?.content ?? "Sem mensagens"}</small>
            <Badge tone={item.ai_enabled ? "green" : "amber"}>{item.status}</Badge>
          </button>
        ))}
        {!conversations.length ? <EmptyState title="Sem conversas" text="Use o debug ou o webhook para criar a primeira conversa." /> : null}
      </section>
      <section className="chat-panel">
        {conversation ? (
          <>
            <div className="chat-header">
              <div>
                <h2>{conversation.customer.name ?? conversation.customer.phone}</h2>
                <p>{conversation.whatsapp_instance.instance_name}</p>
              </div>
              <Badge tone={conversation.ai_enabled ? "green" : "amber"}>{conversation.ai_enabled ? "IA ativa" : "IA pausada"}</Badge>
            </div>
            <div className="message-timeline">
              {conversation.messages.map((item) => (
                <div key={item.id} className={`message-bubble ${item.direction} ${item.sender_type}`}>
                  <span>{senderLabel(item.sender_type)}</span>
                  <p>{item.content}</p>
                  <small>{formatDate(item.created_at)}</small>
                </div>
              ))}
            </div>
            <form className="composer" onSubmit={submit}>
              <input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Responder como humano" />
              <Button variant="primary" disabled={busy === "send-human"}>
                <Send size={16} />
                Enviar
              </Button>
            </form>
          </>
        ) : (
          <EmptyState title="Selecione uma conversa" text="A timeline, lead e controles aparecem aqui." />
        )}
      </section>
      <aside className="detail-panel">
        {conversation ? (
          <>
            <div className="panel-heading">
              <h2>Controle</h2>
              <Bot size={18} />
            </div>
            <div className="control-stack">
              <Button onClick={() => onProcessNow(conversation.id)}><Play size={15} />Processar agora</Button>
              <Button onClick={() => onDisableAi(conversation.id)}><Power size={15} />Pausar IA</Button>
              <Button variant="primary" onClick={() => onEnableAi(conversation.id)}><Bot size={15} />Devolver para IA</Button>
            </div>
            <DetailBlock title="Lead">
              {conversation.lead ? (
                <dl className="details-list">
                  <div><dt>Status</dt><dd>{conversation.lead.status}</dd></div>
                  <div><dt>Score</dt><dd>{conversation.lead.score}</dd></div>
                  <div><dt>Interesse</dt><dd>{conversation.lead.vehicle_interest ?? "-"}</dd></div>
                  <div><dt>Resumo</dt><dd>{conversation.lead.interest_summary ?? "-"}</dd></div>
                </dl>
              ) : (
                <p className="muted">Nenhum lead gerado ainda.</p>
              )}
            </DetailBlock>
            <DetailBlock title="Execuções IA">
              {conversation.agent_runs.length ? conversation.agent_runs.slice(0, 3).map((run) => (
                <div className="run-row" key={run.id}>
                  <Badge tone={run.status === "success" ? "green" : "red"}>{run.status}</Badge>
                  <small>{run.model ?? "fallback"}</small>
                </div>
              )) : <p className="muted">Sem execuções.</p>}
            </DetailBlock>
          </>
        ) : null}
      </aside>
    </div>
  );
}

function LeadsView({ leads, onRefresh }: { leads: LeadSummary[]; onRefresh: () => void }) {
  return (
    <div className="view-stack">
      <section className="page-header">
        <div>
          <h1>Leads</h1>
          <p>Qualificação estruturada produzida pelo agente de atendimento.</p>
        </div>
        <Button onClick={onRefresh}><RefreshCw size={15} />Atualizar</Button>
      </section>
      <section className="table-panel">
        <table>
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Status</th>
              <th>Score</th>
              <th>Interesse</th>
              <th>Pagamento</th>
              <th>Resumo</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id}>
                <td>{lead.customer?.name ?? lead.customer?.phone ?? lead.customer_id}</td>
                <td><Badge tone={lead.status === "qualified" ? "green" : "neutral"}>{lead.status}</Badge></td>
                <td>{lead.score}</td>
                <td>{lead.vehicle_interest ?? "-"}</td>
                <td>{lead.payment_type ?? "-"}</td>
                <td>{lead.interest_summary ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!leads.length ? <EmptyState title="Sem leads" text="Processar uma conversa com IA cria ou atualiza um lead." /> : null}
      </section>
    </div>
  );
}

function CompanyView({
  store,
  busy,
  onSave,
}: {
  store: Store | null;
  busy: string | null;
  onSave: (payload: Partial<Store>) => void;
}) {
  const [name, setName] = useState("");
  const [document, setDocument] = useState("");
  const [phone, setPhone] = useState("");

  useEffect(() => {
    if (!store) return;
    setName(store.name);
    setDocument(store.document ?? "");
    setPhone(store.phone ?? "");
  }, [store]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onSave({ name, document, phone });
  };

  return (
    <div className="view-stack">
      <section className="page-header">
        <div>
          <h1>Empresa</h1>
          <p>Dados usados para operação local e multiempresa simples.</p>
        </div>
      </section>
      <section className="panel narrow">
        <form className="form-grid" onSubmit={submit}>
          <TextField label="Nome" value={name} onChange={(event) => setName(event.target.value)} required />
          <TextField label="Documento" value={document} onChange={(event) => setDocument(event.target.value)} />
          <TextField label="Telefone" value={phone} onChange={(event) => setPhone(event.target.value)} />
          <Button variant="primary" disabled={busy === "save-store"}><CheckCircle2 size={16} />Salvar empresa</Button>
        </form>
      </section>
    </div>
  );
}

function DebugView({
  runtime,
  instances,
  busy,
  onRuntime,
  onSimulate,
}: {
  runtime: RuntimeState | null;
  instances: WhatsAppInstance[];
  busy: string | null;
  onRuntime: (payload: Partial<RuntimeState>) => void;
  onSimulate: (payload: { instance_name: string; webhook_secret?: string; phone: string; text: string; push_name?: string; process_now?: boolean }) => void;
}) {
  const defaultInstance = instances[0]?.instance_name ?? "demo-instance";
  const [instanceName, setInstanceName] = useState(defaultInstance);
  const [secret, setSecret] = useState("");
  const [phone, setPhone] = useState("5511977776666");
  const [name, setName] = useState("Cliente Debug");
  const [text, setText] = useState("Quero um Corolla automático até 120 mil");
  const [processNow, setProcessNow] = useState(true);

  useEffect(() => {
    if (instances[0]?.instance_name && instanceName === "demo-instance") {
      setInstanceName(instances[0].instance_name);
    }
  }, [instanceName, instances]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onSimulate({
      instance_name: instanceName,
      webhook_secret: secret || undefined,
      phone,
      text,
      push_name: name,
      process_now: processNow,
    });
  };

  return (
    <div className="view-stack">
      <section className="page-header">
        <div>
          <h1>Debug local</h1>
          <p>Simule inbound e runtime sem abrir terminal. Rotas existem apenas fora de produção.</p>
        </div>
      </section>
      <section className="split-grid">
        <div className="panel">
          <div className="panel-heading">
            <h2>Runtime</h2>
            <Activity size={18} />
          </div>
          {runtime ? (
            <div className="control-stack">
              <Button onClick={() => onRuntime({ ai_runtime_enabled: !runtime.ai_runtime_enabled })}>
                <Bot size={15} />
                {runtime.ai_runtime_enabled ? "Desligar IA global" : "Ligar IA global"}
              </Button>
              <Button onClick={() => onRuntime({ allow_from_me_as_inbound: !runtime.allow_from_me_as_inbound })}>
                <UserRound size={15} />
                {runtime.allow_from_me_as_inbound ? "Desligar self-group" : "Ligar self-group"}
              </Button>
            </div>
          ) : (
            <p className="muted">Runtime indisponível.</p>
          )}
        </div>
        <div className="panel">
          <div className="panel-heading">
            <h2>Simular inbound</h2>
            <MessageSquareText size={18} />
          </div>
          <form className="form-grid" onSubmit={submit}>
            <TextField label="Instância" value={instanceName} onChange={(event) => setInstanceName(event.target.value)} required />
            <TextField label="Webhook secret" value={secret} onChange={(event) => setSecret(event.target.value)} />
            <TextField label="Telefone cliente" value={phone} onChange={(event) => setPhone(event.target.value)} required />
            <TextField label="Nome cliente" value={name} onChange={(event) => setName(event.target.value)} />
            <TextArea label="Mensagem" value={text} onChange={(event) => setText(event.target.value)} required rows={4} />
            <label className="checkbox-row">
              <input type="checkbox" checked={processNow} onChange={(event) => setProcessNow(event.target.checked)} />
              Processar com IA imediatamente
            </label>
            <Button variant="primary" disabled={busy === "simulate"}><Play size={16} />Simular</Button>
          </form>
        </div>
      </section>
    </div>
  );
}

function DetailBlock({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="detail-block">
      <h3>{title}</h3>
      {children}
    </section>
  );
}

function NoticeBox({ notice }: { notice: Notice }) {
  if (!notice) return null;
  return <div className={`notice notice-${notice.tone}`}>{notice.text}</div>;
}

function StatusRow({ label, value, tone }: { label: string; value: number; tone: "green" | "amber" | "blue" }) {
  return (
    <div className="status-row-line">
      <span className={`status-dot ${tone}`} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function pageTitle(view: AppView) {
  const item = navItems.find((nav) => nav.view === view);
  return item?.label ?? "Whagent";
}

function errorMessage(error: unknown) {
  if (error instanceof Error) return error.message;
  return "Erro inesperado";
}

function formatDate(value: string | null) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function senderLabel(sender: string) {
  if (sender === "agent") return "IA";
  if (sender === "human") return "Humano";
  if (sender === "customer") return "Cliente";
  return "Sistema";
}

function extractQrCode(payload: Record<string, unknown>) {
  const direct = payload.code ?? payload.qrcode ?? payload.base64 ?? payload.pairingCode;
  if (typeof direct === "string" && direct.length > 0) return direct;
  const nested = payload.instance;
  if (nested && typeof nested === "object") {
    const value = (nested as Record<string, unknown>).code ?? (nested as Record<string, unknown>).qrcode;
    if (typeof value === "string" && value.length > 0) return value;
  }
  return null;
}
