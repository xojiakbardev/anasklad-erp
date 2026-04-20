import { createFileRoute } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";

import { Panel } from "@/components/Panel";
import { formatLedger } from "@/lib/format";

export const Route = createFileRoute("/_auth/")({
  component: DashboardPage,
});

function DashboardPage() {
  const { t } = useTranslation();
  return (
    <div className="p-8 space-y-6">
      <header>
        <div className="label-micro mb-2">Anasklad-ERP</div>
        <h1 className="display-title text-4xl">{t("nav.dashboard")}</h1>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Panel label="BUGUNGI SOF FOYDA" showIkat>
          <div className="p-6">
            <div className="ledger-number display-title text-5xl text-[var(--color-accent-gold)]">
              {formatLedger(12487500)}
            </div>
            <div className="label-micro mt-3 text-[var(--color-signal-up)]">
              ▲ 14.2% · kechagi kun
            </div>
          </div>
        </Panel>

        <Panel label="FBS BUYURTMALAR">
          <div className="p-6">
            <div className="ledger-number display-title text-5xl">{formatLedger(27)}</div>
            <div className="label-micro mt-3 text-[var(--color-fg-muted)]">
              tasdiq kutmoqda
            </div>
          </div>
        </Panel>

        <Panel label="KRITIK QOLDIQ">
          <div className="p-6">
            <div className="ledger-number display-title text-5xl text-[var(--color-signal-warn)]">
              {formatLedger(8)}
            </div>
            <div className="label-micro mt-3 text-[var(--color-fg-muted)]">
              SKU kam qoldi
            </div>
          </div>
        </Panel>
      </div>

      <Panel label="DASHBOARD V1" title="Keyingi sprintlarda to'ldiriladi">
        <div className="p-6 text-[var(--color-fg-muted)] text-sm leading-relaxed">
          Bu sahifa Sprint 5-6 da real ma'lumotlar bilan to'ldiriladi: P&L chart,
          top SKU ro'yxati, ABC hisobot, real-time buyurtma oqimi. Hozircha
          <span className="text-[var(--color-accent-gold)]"> /integrations </span>
          sahifasidan boshlang.
        </div>
      </Panel>
    </div>
  );
}
