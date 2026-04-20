import { Link, Outlet, useRouterState } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";

import { IkatStripe } from "@/components/IkatStripe";
import { Logo } from "@/components/Logo";
import { cn } from "@/lib/cn";
import { useAuth } from "@/stores/auth";

const NAV = [
  { to: "/", label: "dashboard" as const },
  { to: "/integrations", label: "integrations" as const },
  // Placeholders; implemented in later sprints.
  { to: "/products", label: "products" as const },
  { to: "/orders", label: "orders" as const },
  { to: "/stocks", label: "stocks" as const },
  { to: "/finance", label: "finance" as const },
];

export function AppShell() {
  const { t } = useTranslation();
  const location = useRouterState({ select: (s) => s.location.pathname });
  const user = useAuth((s) => s.user);
  const logout = useAuth((s) => s.logout);

  return (
    <div className="min-h-screen grid grid-cols-[240px_1fr] grid-rows-[1fr_auto]">
      {/* Sidebar */}
      <aside className="row-span-2 border-r border-[var(--color-border-hair)] flex flex-col bg-[var(--color-bg-raised)]">
        <div className="p-5 border-b border-[var(--color-border-hair)]">
          <Logo />
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map((item) => {
            const isActive =
              item.to === "/" ? location === "/" : location.startsWith(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  "relative flex items-center gap-3 px-3 py-2 rounded-sm text-sm transition-colors",
                  isActive
                    ? "bg-[var(--color-bg-elevated)] text-[var(--color-fg-primary)]"
                    : "text-[var(--color-fg-muted)] hover:text-[var(--color-fg-primary)] hover:bg-[var(--color-bg-elevated)]",
                )}
              >
                {isActive && (
                  <IkatStripe className="absolute left-0 top-1 bottom-1" />
                )}
                <span className={cn(isActive && "ml-2")}>{t(`nav.${item.label}`)}</span>
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-[var(--color-border-hair)] text-xs">
          <div className="text-[var(--color-fg-muted)] truncate">{user?.email}</div>
          <button
            type="button"
            onClick={logout}
            className="mt-2 label-micro hover:text-[var(--color-accent-gold)] cursor-pointer"
          >
            {t("common.logout")}
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="overflow-auto">
        <Outlet />
      </main>

      {/* Status bar */}
      <footer className="col-start-2 border-t border-[var(--color-border-hair)] bg-[var(--color-bg-raised)] px-5 py-2 flex items-center justify-between text-xs font-mono text-[var(--color-fg-muted)]">
        <span>v0.1.0 · {import.meta.env.MODE}</span>
        <span>Anasklad-ERP · {new Date().getFullYear()}</span>
      </footer>
    </div>
  );
}
