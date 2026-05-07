"use client";

import {
  Activity,
  Building2,
  LogOut,
  MessageSquareText,
  Settings,
  Smartphone,
  UserRound,
  UsersRound,
  Menu,
  X,
  Moon,
  Sun,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { ReactNode, useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui";
import type { CurrentUser } from "@/types/user";
import type { DashboardOverview } from "@/types/dashboard";

type AppView = "overview" | "inbox" | "instances" | "leads" | "company" | "users" | "customers" | "debug";


const navItems: Array<{
  view: AppView;
  href: string;
  label: string;
  icon: typeof Activity;
  adminOnly?: boolean;
}> = [
  { view: "overview", href: "/app/overview", label: "Visão geral", icon: Activity },
  { view: "inbox", href: "/app/inbox", label: "Atendimento", icon: MessageSquareText },
  { view: "instances", href: "/app/instances", label: "Conexões", icon: Smartphone },
  { view: "leads", href: "/app/leads", label: "Leads", icon: UsersRound },
  { view: "users", href: "/app/users", label: "Usuários", icon: UserRound, adminOnly: true },
  { view: "customers", href: "/app/customers", label: "Clientes", icon: UsersRound },
  { view: "company", href: "/app/company", label: "Empresa", icon: Building2 },
  { view: "debug", href: "/app/debug", label: "Debug", icon: Settings, adminOnly: true },
];

function pageTitle(view: AppView) {
  return navItems.find((n) => n.view === view)?.label ?? "Whagent";
}

export { navItems, type AppView };

export function AppShell({
  activeView,
  user,
  overview,
  busy,
  children,
  onLogout,
}: {
  activeView: AppView;
  user: CurrentUser | null;
  overview: DashboardOverview | null;
  busy: string | null;
  children: ReactNode;
  onLogout: () => void;
}) {
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => setMounted(true), []);

  const visibleNav = navItems.filter(
    (item) => !item.adminOnly || user?.role === "admin"
  );

  const SidebarContent = () => (
    <>
      <div className="p-4 flex items-center gap-3 border-b border-border">
        <div className="w-9 h-9 rounded-xl bg-primary/20 flex items-center justify-center text-primary font-bold">W</div>
        <div className="leading-tight">
          <strong className="text-sm text-foreground block">Whagent</strong>
          <span className="text-[11px] text-muted-foreground">Atendimento IA</span>
        </div>
      </div>
      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto" aria-label="Navegação principal">
        {visibleNav.map((item) => {
          const Icon = item.icon;
          const active = activeView === item.view;
          return (
            <button
              key={item.href}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${
                active
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              }`}
              onClick={() => {
                setMobileMenuOpen(false);
                router.push(item.href);
              }}
            >
              <Icon size={17} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
      <div className="p-4 border-t border-border grid grid-cols-2 gap-2 text-center">
        <div>
          <span className="text-[10px] uppercase text-muted-foreground tracking-wider">Conversas</span>
          <strong className="block text-lg text-foreground">{overview?.conversations_total ?? 0}</strong>
        </div>
        <div>
          <span className="text-[10px] uppercase text-muted-foreground tracking-wider">Leads</span>
          <strong className="block text-lg text-foreground">{overview?.leads_total ?? 0}</strong>
        </div>
      </div>
    </>
  );

  return (
    <main className="flex h-screen bg-background overflow-hidden relative">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-60 shrink-0 border-r border-border flex-col bg-card">
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 z-40 md:hidden"
              onClick={() => setMobileMenuOpen(false)}
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", bounce: 0, duration: 0.3 }}
              className="fixed inset-y-0 left-0 w-64 bg-card z-50 flex flex-col md:hidden border-r border-border shadow-2xl"
            >
              <SidebarContent />
              <Button 
                variant="ghost" 
                size="icon" 
                className="absolute top-3 right-3" 
                onClick={() => setMobileMenuOpen(false)}
              >
                <X size={18} />
              </Button>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Main */}
      <section className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="h-14 shrink-0 border-b border-border flex items-center justify-between px-4 md:px-5 bg-card/50">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(true)}
            >
              <Menu size={20} />
            </Button>
            <div className="leading-tight">
              <strong className="text-sm text-foreground">{pageTitle(activeView)}</strong>
              <span className="text-xs text-muted-foreground ml-2 hidden sm:inline-block">
                {user ? `${user.full_name} · ${user.role}` : "Sessão local"}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {mounted && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                title="Alternar tema"
              >
                {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
              </Button>
            )}
            <Button size="sm" variant="ghost" onClick={onLogout}>
              <LogOut size={14} className="md:mr-2" />
              <span className="hidden md:inline-block">Sair</span>
            </Button>
          </div>
        </header>
        <motion.div
          key={activeView}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="flex-1 overflow-y-auto p-5"
        >
          {children}
        </motion.div>
      </section>
    </main>
  );
}
