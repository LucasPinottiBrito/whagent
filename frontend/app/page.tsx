import { backendFetch } from "@/services/api";

type Health = {
  status: string;
};

async function getBackendHealth(): Promise<string> {
  try {
    const health = await backendFetch<Health>("/health", { cache: "no-store" });
    return health.status;
  } catch {
    return "offline";
  }
}

export default async function HomePage() {
  const backendStatus = await getBackendHealth();

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">WhatsApp AI Agent SaaS</p>
        <h1>Atendimento inteligente para lojas de carros.</h1>
        <p className="lede">
          Painel reservado para login, conversas, leads, handoff humano e
          configuracao de instancias WhatsApp. O frontend fala apenas com o
          backend.
        </p>
        <div className="status-card">
          <span>Backend</span>
          <strong>{backendStatus}</strong>
        </div>
      </section>
    </main>
  );
}
