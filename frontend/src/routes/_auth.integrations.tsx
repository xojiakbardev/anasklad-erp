import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { catalogApi } from "@/api/catalog";
import { financeApi } from "@/api/finance";
import { type Integration, integrationsApi } from "@/api/integrations";
import { ordersApi } from "@/api/orders";
import { IkatStripe } from "@/components/IkatStripe";
import { Panel } from "@/components/Panel";
import { ApiError } from "@/lib/api";
import { cn } from "@/lib/cn";
import { formatRelativeTime } from "@/lib/format";

export const Route = createFileRoute("/_auth/integrations")({
  component: IntegrationsPage,
});

function IntegrationsPage() {
  const { t } = useTranslation();
  const [wizardOpen, setWizardOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ["integrations"],
    queryFn: integrationsApi.list,
  });

  return (
    <div className="p-8 space-y-6">
      <header className="flex items-end justify-between gap-4">
        <div>
          <div className="label-micro mb-2">{t("integrations.title")}</div>
          <h1 className="display-title text-4xl">{t("integrations.title")}</h1>
          <p className="text-[var(--color-fg-muted)] mt-2 max-w-2xl">
            {t("integrations.subtitle")}
          </p>
        </div>
        <button
          type="button"
          onClick={() => setWizardOpen(true)}
          className="ak-btn ak-btn-primary"
        >
          + {t("integrations.add_uzum")}
        </button>
      </header>

      {isLoading ? (
        <Panel>
          <div className="p-12 text-center text-[var(--color-fg-muted)]">
            {t("common.loading")}
          </div>
        </Panel>
      ) : !data || data.length === 0 ? (
        <Panel showIkat>
          <div className="p-12 text-center">
            <h3 className="display-title text-2xl mb-2">{t("integrations.no_integrations")}</h3>
            <p className="text-[var(--color-fg-muted)] mb-6 max-w-md mx-auto">
              {t("integrations.no_integrations_hint")}
            </p>
            <button
              type="button"
              onClick={() => setWizardOpen(true)}
              className="ak-btn ak-btn-primary"
            >
              + {t("integrations.add_uzum")}
            </button>
          </div>
        </Panel>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {data.map((it) => <IntegrationCard key={it.id} integration={it} />)}
        </div>
      )}

      <AnimatePresence>
        {wizardOpen && <UzumWizard onClose={() => setWizardOpen(false)} />}
      </AnimatePresence>
    </div>
  );
}

function IntegrationCard({ integration }: { integration: Integration }) {
  const { t } = useTranslation();
  const qc = useQueryClient();

  const testMut = useMutation({
    mutationFn: () => integrationsApi.test(integration.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["integrations"] }),
  });

  const syncMut = useMutation({
    mutationFn: async () => {
      const [cat, ord, fin] = await Promise.all([
        catalogApi.syncIntegration(integration.id),
        ordersApi.sync(integration.id),
        financeApi.sync(integration.id),
      ]);
      return {
        products: cat.products_upserted,
        variants: cat.variants_upserted,
        orders: ord.orders_upserted,
        sales: fin.sales_upserted,
        expenses: fin.expenses_upserted,
      };
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["integrations"] });
      qc.invalidateQueries({ queryKey: ["products"] });
      qc.invalidateQueries({ queryKey: ["orders"] });
      qc.invalidateQueries({ queryKey: ["sales"] });
      qc.invalidateQueries({ queryKey: ["expenses"] });
      qc.invalidateQueries({ queryKey: ["finance"] });
    },
  });

  const deleteMut = useMutation({
    mutationFn: () => integrationsApi.remove(integration.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["integrations"] }),
  });

  const status =
    integration.status === "active"
      ? "up"
      : integration.status === "error"
        ? "down"
        : "muted";

  return (
    <Panel
      showIkat={integration.status === "active"}
      label={integration.source.toUpperCase()}
      title={integration.label}
      actions={
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => syncMut.mutate()}
            disabled={syncMut.isPending}
            className="ak-btn ak-btn-secondary text-xs"
          >
            {syncMut.isPending ? "Sync..." : "Sync"}
          </button>
          <button
            type="button"
            onClick={() => testMut.mutate()}
            disabled={testMut.isPending}
            className="ak-btn ak-btn-ghost text-xs"
          >
            {testMut.isPending ? "..." : t("common.test")}
          </button>
          <button
            type="button"
            onClick={() => {
              if (confirm(t("integrations.delete_confirm"))) deleteMut.mutate();
            }}
            disabled={deleteMut.isPending}
            className="ak-btn ak-btn-danger text-xs"
          >
            {t("common.delete")}
          </button>
        </div>
      }
    >
      <div className="p-5 space-y-4">
        <div className="flex items-center gap-3">
          <span className={cn("ak-pill", `ak-pill-${status}`)}>
            {t(`integrations.status_${integration.status}`)}
          </span>
          <span className="label-micro">
            {t("integrations.last_checked")}:&nbsp;
            <span className="text-[var(--color-fg-primary)] normal-case tracking-normal">
              {formatRelativeTime(integration.last_checked_at)}
            </span>
          </span>
        </div>

        {syncMut.data && (
          <div className="border border-[var(--color-signal-up)]/40 bg-[var(--color-signal-up)]/5 px-3 py-2 text-xs text-[var(--color-signal-up)] rounded-sm font-mono">
            ✓ {syncMut.data.products} mahsulot · {syncMut.data.variants} SKU · {syncMut.data.orders} buyurtma · {syncMut.data.sales} sotuv · {syncMut.data.expenses} xarajat
          </div>
        )}

        {integration.last_error && (
          <div className="border border-[var(--color-signal-down)]/40 bg-[var(--color-signal-down)]/5 px-3 py-2 text-sm text-[var(--color-signal-down)] rounded-sm font-mono">
            {integration.last_error}
          </div>
        )}

        <div>
          <div className="label-micro mb-2">
            {t("integrations.connected_shops")} · {integration.shops.length}
          </div>
          <div className="divide-y divide-[var(--color-border-hair)]">
            {integration.shops.map((shop) => (
              <div
                key={shop.id}
                className="flex items-center justify-between py-2.5 text-sm"
              >
                <span className="font-medium">{shop.name}</span>
                <span className="ledger-number text-xs text-[var(--color-fg-muted)]">
                  ID · {shop.external_id}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Panel>
  );
}

function UzumWizard({ onClose }: { onClose: () => void }) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [token, setToken] = useState("");
  const [label, setLabel] = useState("Asosiy do'kon");

  const connect = useMutation({
    mutationFn: () => integrationsApi.connectUzum(token, label),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["integrations"] });
      onClose();
    },
  });

  const errorMsg =
    connect.error instanceof ApiError ? connect.error.message : null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        transition={{ duration: 0.15 }}
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-md bg-[var(--color-bg-elevated)] border border-[var(--color-border-sub)] rounded-sm overflow-hidden"
      >
        <IkatStripe className="absolute left-0 top-0 bottom-0" />
        <div className="pl-8 p-6 space-y-5">
          <div>
            <div className="label-micro mb-1">UZUM MARKET</div>
            <h2 className="display-title text-2xl">{t("integrations.add_uzum")}</h2>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              connect.mutate();
            }}
            className="space-y-4"
          >
            <label className="block space-y-1.5">
              <span className="label-micro">{t("integrations.label")}</span>
              <input
                type="text"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                required
                maxLength={128}
                className="ak-input"
                placeholder={t("integrations.label_hint")}
              />
            </label>

            <label className="block space-y-1.5">
              <span className="label-micro">{t("integrations.token")}</span>
              <textarea
                value={token}
                onChange={(e) => setToken(e.target.value)}
                required
                minLength={16}
                rows={3}
                className="ak-input font-mono text-xs"
                placeholder="eyJhbGc..."
              />
              <p className="text-xs text-[var(--color-fg-muted)] mt-1">
                {t("integrations.token_hint")}
              </p>
            </label>

            {errorMsg && (
              <div className="ak-pill ak-pill-down w-full justify-center py-2">
                {errorMsg}
              </div>
            )}

            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="ak-btn ak-btn-ghost flex-1"
              >
                {t("common.cancel")}
              </button>
              <button
                type="submit"
                disabled={connect.isPending}
                className="ak-btn ak-btn-primary flex-1"
              >
                {connect.isPending ? t("common.loading") : t("integrations.connect")}
              </button>
            </div>
          </form>
        </div>
      </motion.div>
    </motion.div>
  );
}
