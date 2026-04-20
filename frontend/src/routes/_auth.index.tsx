import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";

import { financeApi } from "@/api/finance";
import { integrationsApi } from "@/api/integrations";
import { ordersApi } from "@/api/orders";
import { OnboardingModal, useOnboarding } from "@/components/OnboardingModal";
import { Panel } from "@/components/Panel";
import { ProfitChart } from "@/components/ProfitChart";
import { cn } from "@/lib/cn";
import { formatLedger } from "@/lib/format";

export const Route = createFileRoute("/_auth/")({
  component: DashboardPage,
});

function DashboardPage() {
  const { t } = useTranslation();
  const onboarding = useOnboarding();

  const { data: integrations } = useQuery({
    queryKey: ["integrations"],
    queryFn: integrationsApi.list,
  });

  const { data: summary } = useQuery({
    queryKey: ["finance", "summary", 30],
    queryFn: () => financeApi.summary(30),
    refetchInterval: 120_000,
  });

  const { data: ordersList } = useQuery({
    queryKey: ["orders", "count_dashboard"],
    queryFn: () => ordersApi.list({ size: 1 }),
    refetchInterval: 60_000,
  });

  const todayProfit = summary?.today.profit ?? 0;
  const periodRevenue = summary?.period.revenue ?? 0;
  const periodProfit = summary?.period.profit ?? 0;
  const periodMargin =
    periodRevenue > 0 ? (periodProfit / periodRevenue) * 100 : null;
  const pendingFbs =
    (ordersList?.counts_by_status?.CREATED ?? 0) +
    (ordersList?.counts_by_status?.PACKING ?? 0);

  const showOnboarding =
    onboarding.open || (integrations !== undefined && integrations.length === 0);

  return (
    <div className="p-8 space-y-6">
      <OnboardingModal open={showOnboarding} onClose={onboarding.close} />
      <header>
        <div className="label-micro mb-2">ANASKLAD · TERMINAL</div>
        <h1 className="display-title text-4xl">{t("nav.dashboard")}</h1>
        <p className="text-[var(--color-fg-muted)] mt-1 text-sm">
          Oxirgi 30 kun · bugun yangilangan
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Panel label="BUGUNGI SOF FOYDA" showIkat>
          <div className="p-6">
            <div
              className={cn(
                "ledger-number display-title text-5xl",
                todayProfit >= 0
                  ? "text-[var(--color-accent-gold)]"
                  : "text-[var(--color-signal-down)]",
              )}
            >
              {formatLedger(todayProfit)}
            </div>
            <div className="label-micro mt-3">
              {summary?.today.sales_count ?? 0} ta sotuv ·{" "}
              {summary?.today.units_sold ?? 0} dona
            </div>
          </div>
        </Panel>

        <Panel label="FBS KUTMOQDA">
          <div className="p-6">
            <div
              className={cn(
                "ledger-number display-title text-5xl",
                pendingFbs > 10 ? "text-[var(--color-signal-warn)]" : "",
              )}
            >
              {formatLedger(pendingFbs)}
            </div>
            <div className="label-micro mt-3">tasdiq + yig'ish</div>
          </div>
        </Panel>

        <Panel label="30 KUN MARJAMI">
          <div className="p-6">
            <div className="ledger-number display-title text-5xl text-[var(--color-accent-ink)]">
              {periodMargin === null ? "—" : `${periodMargin.toFixed(1)}%`}
            </div>
            <div className="label-micro mt-3">
              {formatLedger(periodProfit)} / {formatLedger(periodRevenue)}
            </div>
          </div>
        </Panel>
      </div>

      <Panel label="KUNLIK DAROMAD VA FOYDA" title="30 kun">
        <div className="p-6">
          {summary ? (
            <ProfitChart data={summary.daily} />
          ) : (
            <div className="h-[220px] flex items-center justify-center text-[var(--color-fg-muted)]">
              {t("common.loading")}
            </div>
          )}
        </div>
      </Panel>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Panel label="TOP MAHSULOTLAR · FOYDA" title="30 kun">
          <div className="divide-y divide-[var(--color-border-hair)]">
            {summary?.top_products.slice(0, 8).map((p, idx) => (
              <div
                key={p.product_id ?? idx}
                className="px-5 py-3 flex items-center gap-3"
              >
                <span className="ledger-number text-xs text-[var(--color-fg-dim)] w-6">
                  {(idx + 1).toString().padStart(2, "0")}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="truncate text-sm">{p.title}</div>
                  <div className="ledger-number text-[11px] text-[var(--color-fg-muted)]">
                    {p.units} dona · {formatLedger(p.revenue)}
                  </div>
                </div>
                <div className="ledger-number text-sm text-[var(--color-signal-up)]">
                  {formatLedger(p.profit)}
                </div>
              </div>
            ))}
            {(!summary || summary.top_products.length === 0) && (
              <div className="p-8 text-center text-[var(--color-fg-muted)] text-sm">
                Sotuvlar yo'q. Integratsiyadan sync qiling.
              </div>
            )}
          </div>
        </Panel>

        <Panel label="QISMLAR · 30 KUN" title="P&L">
          <div className="p-5 space-y-2.5">
            <Row label="Daromad (sotuv)" value={formatLedger(periodRevenue)} />
            <Row
              label="Komissiya"
              value={`(${formatLedger(summary?.period.commission ?? 0)})`}
              tone="down"
            />
            <Row
              label="Logistika"
              value={`(${formatLedger(summary?.period.logistics ?? 0)})`}
              tone="down"
            />
            <Row
              label="Tannarx"
              value={`(${formatLedger(summary?.period.purchase_cost ?? 0)})`}
              tone="down"
            />
            <div className="border-t border-[var(--color-border-hair)] pt-2.5">
              <Row
                label="Sof foyda"
                value={formatLedger(periodProfit)}
                tone={periodProfit >= 0 ? "up" : "down"}
                strong
              />
            </div>
            <Row
              label="Qaytarilgan dona"
              value={formatLedger(summary?.period.units_returned ?? 0)}
              muted
            />
          </div>
        </Panel>
      </div>
    </div>
  );
}

function Row({
  label,
  value,
  tone,
  strong,
  muted,
}: {
  label: string;
  value: string;
  tone?: "up" | "down";
  strong?: boolean;
  muted?: boolean;
}) {
  return (
    <div className="flex justify-between items-baseline text-sm">
      <span
        className={cn(
          "text-[var(--color-fg-muted)]",
          muted && "text-[var(--color-fg-dim)]",
        )}
      >
        {label}
      </span>
      <span
        className={cn(
          "ledger-number",
          strong && "text-base font-semibold",
          tone === "up" && "text-[var(--color-signal-up)]",
          tone === "down" && "text-[var(--color-signal-down)]",
        )}
      >
        {value}
      </span>
    </div>
  );
}
