import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { KANBAN_COLUMNS, type FbsStatus, type Order, ordersApi } from "@/api/orders";
import { IkatStripe } from "@/components/IkatStripe";
import { cn } from "@/lib/cn";
import { formatDateTime, formatLedger, formatRelativeTime } from "@/lib/format";

export const Route = createFileRoute("/_auth/orders")({
  component: OrdersPage,
});

const STATUS_LABEL: Record<FbsStatus, string> = {
  CREATED: "Yangi",
  PACKING: "Yig'ilmoqda",
  PENDING_DELIVERY: "Kutilmoqda",
  DELIVERING: "Yo'lda",
  DELIVERED: "Yetkazildi",
  ACCEPTED_AT_DP: "DP'da",
  DELIVERED_TO_CUSTOMER_DELIVERY_POINT: "PVZ'da",
  COMPLETED: "Yopildi",
  CANCELED: "Bekor",
  PENDING_CANCELLATION: "Bekor kutmoqda",
  RETURNED: "Qaytarildi",
};

function OrdersPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [view, setView] = useState<"kanban" | "list">("kanban");

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 pt-8 pb-4 border-b border-[var(--color-border-hair)] flex items-end justify-between gap-4">
        <div>
          <div className="label-micro mb-2">FBS PIPELINE</div>
          <h1 className="display-title text-4xl">Buyurtmalar</h1>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setView("kanban")}
            className={cn("ak-btn text-xs", view === "kanban" ? "ak-btn-secondary" : "ak-btn-ghost")}
          >
            ■ ■ ■
          </button>
          <button
            type="button"
            onClick={() => setView("list")}
            className={cn("ak-btn text-xs", view === "list" ? "ak-btn-secondary" : "ak-btn-ghost")}
          >
            ☰ Ro'yxat
          </button>
        </div>
      </header>

      <div className={cn("flex-1 overflow-hidden", selectedId ? "grid grid-cols-[1fr_520px]" : "")}>
        <div className="overflow-hidden">
          {view === "kanban" ? (
            <KanbanView onSelect={setSelectedId} selectedId={selectedId} />
          ) : (
            <ListView onSelect={setSelectedId} selectedId={selectedId} />
          )}
        </div>

        <AnimatePresence>
          {selectedId && (
            <motion.div
              initial={{ x: 40, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 40, opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="border-l border-[var(--color-border-hair)]"
            >
              <OrderDrawer orderId={selectedId} onClose={() => setSelectedId(null)} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function KanbanView({
  onSelect,
  selectedId,
}: {
  onSelect: (id: string) => void;
  selectedId: string | null;
}) {
  const { data } = useQuery({
    queryKey: ["orders", "kanban"],
    queryFn: async () => {
      const results = await Promise.all(
        KANBAN_COLUMNS.map((s) => ordersApi.list({ status: s, size: 50 })),
      );
      return KANBAN_COLUMNS.reduce(
        (acc, s, i) => {
          const r = results[i];
          if (r) acc[s] = r;
          return acc;
        },
        {} as Record<FbsStatus, { items: Order[]; total: number }>,
      );
    },
    refetchInterval: 60_000,
    placeholderData: keepPreviousData,
  });

  return (
    <div className="h-full overflow-auto">
      <div className="min-w-[1200px] grid grid-cols-5 gap-0 h-full">
        {KANBAN_COLUMNS.map((status) => {
          const col = data?.[status];
          return (
            <div
              key={status}
              className="border-r border-[var(--color-border-hair)] flex flex-col overflow-hidden"
            >
              <div className="px-4 py-3 border-b border-[var(--color-border-hair)] bg-[var(--color-bg-raised)]">
                <div className="flex items-baseline justify-between">
                  <span className="label-micro">{STATUS_LABEL[status]}</span>
                  <span className="ledger-number text-sm text-[var(--color-accent-gold)]">
                    {formatLedger(col?.total ?? 0)}
                  </span>
                </div>
              </div>
              <div className="flex-1 overflow-auto p-3 space-y-2">
                {(col?.items ?? []).map((o) => (
                  <OrderCard
                    key={o.id}
                    order={o}
                    active={selectedId === o.id}
                    onSelect={() => onSelect(o.id)}
                  />
                ))}
                {col && col.items.length === 0 && (
                  <div className="text-center text-xs text-[var(--color-fg-dim)] py-8">
                    bo'sh
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function OrderCard({
  order,
  active,
  onSelect,
}: {
  order: Order;
  active: boolean;
  onSelect: () => void;
}) {
  const urgent =
    order.accept_until &&
    new Date(order.accept_until).getTime() - Date.now() < 30 * 60 * 1000;

  return (
    <button
      type="button"
      onClick={onSelect}
      className={cn(
        "relative w-full text-left p-3 rounded-sm border border-[var(--color-border-hair)] bg-[var(--color-bg-raised)] hover:bg-[var(--color-bg-elevated)] transition-colors cursor-pointer",
        active && "bg-[var(--color-bg-elevated)] border-[var(--color-accent-gold)]",
      )}
    >
      {active && <IkatStripe className="absolute left-0 top-1 bottom-1" />}
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="ledger-number text-sm font-medium">#{order.external_id}</span>
        {urgent && <span className="ak-pill ak-pill-warn">URGENT</span>}
      </div>
      <div className="ledger-number text-lg text-[var(--color-accent-gold)] mb-1">
        {order.price ? formatLedger(order.price) : "—"}
      </div>
      <div className="label-micro text-[9px]">
        {formatRelativeTime(order.date_created)}
      </div>
      {order.accept_until && (
        <div className="text-[10px] text-[var(--color-fg-muted)] mt-1 font-mono">
          ⏱ {formatDateTime(order.accept_until)}
        </div>
      )}
    </button>
  );
}

function ListView({
  onSelect,
  selectedId,
}: {
  onSelect: (id: string) => void;
  selectedId: string | null;
}) {
  const [page, setPage] = useState(0);
  const { data } = useQuery({
    queryKey: ["orders", "list", page],
    queryFn: () => ordersApi.list({ page, size: 100 }),
    placeholderData: keepPreviousData,
  });

  const items = data?.items ?? [];

  return (
    <div className="h-full overflow-auto">
      <div className="sticky top-0 z-10 bg-[var(--color-bg-raised)] border-b border-[var(--color-border-hair)] grid grid-cols-[100px_1fr_140px_120px_160px_160px] label-micro py-3 px-4">
        <span>ID</span>
        <span>Holati</span>
        <span className="text-right">Narx</span>
        <span className="text-right">Schema</span>
        <span className="text-right">Yaratilgan</span>
        <span className="text-right">Yetkazish</span>
      </div>
      {items.map((o) => (
        <button
          type="button"
          key={o.id}
          onClick={() => onSelect(o.id)}
          className={cn(
            "relative w-full grid grid-cols-[100px_1fr_140px_120px_160px_160px] items-center px-4 py-2 gap-2 text-left border-b border-[var(--color-border-hair)] hover:bg-[var(--color-bg-elevated)] transition-colors cursor-pointer",
            selectedId === o.id && "bg-[var(--color-bg-elevated)]",
          )}
        >
          {selectedId === o.id && <IkatStripe className="absolute left-0 top-1 bottom-1" />}
          <span className="ledger-number text-sm">#{o.external_id}</span>
          <span>
            <span
              className={cn(
                "ak-pill",
                o.status === "CREATED" && "ak-pill-info",
                o.status === "COMPLETED" && "ak-pill-up",
                o.status === "CANCELED" && "ak-pill-down",
                !["CREATED", "COMPLETED", "CANCELED"].includes(o.status) && "ak-pill-muted",
              )}
            >
              {STATUS_LABEL[o.status]}
            </span>
          </span>
          <span className="ledger-number text-right">
            {o.price ? formatLedger(o.price) : "—"}
          </span>
          <span className="ledger-number text-right text-xs text-[var(--color-fg-muted)]">
            {o.scheme || "—"}
          </span>
          <span className="ledger-number text-right text-xs text-[var(--color-fg-muted)]">
            {formatDateTime(o.date_created)}
          </span>
          <span className="ledger-number text-right text-xs text-[var(--color-fg-muted)]">
            {formatDateTime(o.deliver_until)}
          </span>
        </button>
      ))}
      {(data?.total ?? 0) > 100 && (
        <div className="border-t border-[var(--color-border-hair)] px-4 py-3 flex items-center justify-between text-xs ledger-number sticky bottom-0 bg-[var(--color-bg-raised)]">
          <span className="text-[var(--color-fg-muted)]">
            {formatLedger(page * 100 + 1)} –{" "}
            {formatLedger(Math.min((page + 1) * 100, data?.total ?? 0))} · jami{" "}
            {formatLedger(data?.total ?? 0)}
          </span>
          <div className="flex gap-1">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="ak-btn ak-btn-ghost text-xs py-1 px-3"
            >
              ◀
            </button>
            <button
              type="button"
              onClick={() => setPage((p) => p + 1)}
              disabled={(page + 1) * 100 >= (data?.total ?? 0)}
              className="ak-btn ak-btn-ghost text-xs py-1 px-3"
            >
              ▶
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function OrderDrawer({ orderId, onClose }: { orderId: string; onClose: () => void }) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => ordersApi.get(orderId),
  });

  const confirmMut = useMutation({
    mutationFn: () => ordersApi.confirm(orderId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["order", orderId] });
      qc.invalidateQueries({ queryKey: ["orders"] });
    },
  });

  const cancelMut = useMutation({
    mutationFn: (reason: string) => ordersApi.cancel(orderId, reason),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["order", orderId] });
      qc.invalidateQueries({ queryKey: ["orders"] });
    },
  });

  if (!data) {
    return (
      <aside className="relative h-full overflow-auto bg-[var(--color-bg-raised)] p-6">
        <IkatStripe className="absolute left-0 top-0 bottom-0" />
        <div className="pl-6 text-[var(--color-fg-muted)]">{t("common.loading")}</div>
      </aside>
    );
  }

  const totalProfit = data.items.reduce((s, i) => s + (i.seller_profit ?? 0), 0);
  const totalCommission = data.items.reduce((s, i) => s + (i.commission ?? 0), 0);
  const totalLogistics = data.items.reduce((s, i) => s + (i.logistic_delivery_fee ?? 0), 0);
  const canConfirm = data.status === "CREATED";
  const canCancel = ["CREATED", "PACKING", "PENDING_DELIVERY"].includes(data.status);

  return (
    <aside className="relative h-full overflow-auto bg-[var(--color-bg-raised)]">
      <IkatStripe className="absolute left-0 top-0 bottom-0" />
      <div className="pl-6 pr-5 py-5">
        <div className="flex items-start justify-between gap-2 mb-5">
          <div>
            <div className="label-micro mb-1">BUYURTMA</div>
            <h2 className="display-title text-2xl ledger-number">#{data.external_id}</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-[var(--color-fg-muted)] hover:text-[var(--color-fg-primary)] text-lg cursor-pointer"
          >
            ✕
          </button>
        </div>

        <div className="flex items-center gap-2 mb-5">
          <span className="ak-pill ak-pill-info">{STATUS_LABEL[data.status]}</span>
          {data.scheme && <span className="ak-pill ak-pill-muted">{data.scheme}</span>}
        </div>

        <div className="grid grid-cols-2 gap-3 mb-5">
          <TimerBox label="Qabul qilish" iso={data.accept_until} />
          <TimerBox label="Yetkazish" iso={data.deliver_until} />
        </div>

        <div className="border border-[var(--color-border-hair)] rounded-sm p-4 mb-5 space-y-2">
          <Row label="Sotuv narxi" value={formatLedger(data.price ?? 0)} strong />
          <Row label="Komissiya" value={`(${formatLedger(totalCommission)})`} tone="down" />
          <Row label="Logistika" value={`(${formatLedger(totalLogistics)})`} tone="down" />
          <div className="border-t border-[var(--color-border-hair)] pt-2">
            <Row
              label="Sof foyda"
              value={formatLedger(totalProfit)}
              tone={totalProfit >= 0 ? "up" : "down"}
              strong
            />
          </div>
        </div>

        <div className="flex gap-2 mb-5">
          {canConfirm && (
            <button
              type="button"
              onClick={() => confirmMut.mutate()}
              disabled={confirmMut.isPending}
              className="ak-btn ak-btn-primary flex-1"
            >
              {confirmMut.isPending ? "..." : "✓ Tasdiqlash"}
            </button>
          )}
          {data.status === "PACKING" && (
            <a
              href={ordersApi.labelUrl(data.id, "LARGE")}
              target="_blank"
              rel="noreferrer"
              className="ak-btn ak-btn-secondary flex-1 no-underline"
            >
              🖨 Etiketka
            </a>
          )}
          {canCancel && (
            <button
              type="button"
              onClick={() => {
                const reason = prompt(
                  "Sabab (OUT_OF_STOCK / OUT_OF_PACKAGE / OUT_OF_TIME / OTHER):",
                  "OUT_OF_STOCK",
                );
                if (reason) cancelMut.mutate(reason);
              }}
              disabled={cancelMut.isPending}
              className="ak-btn ak-btn-danger"
            >
              Bekor
            </button>
          )}
        </div>

        <div className="label-micro mb-2">MAHSULOTLAR · {data.items.length}</div>
        <div className="space-y-2">
          {data.items.map((it) => (
            <div
              key={it.id}
              className="border border-[var(--color-border-hair)] rounded-sm p-3 text-sm"
            >
              <div className="flex justify-between gap-2 mb-1">
                <div className="min-w-0">
                  <div className="font-medium truncate">{it.product_title || "—"}</div>
                  <div className="text-xs text-[var(--color-fg-muted)]">{it.sku_title}</div>
                </div>
                <span className="ledger-number text-[var(--color-accent-gold)]">
                  ×{it.amount}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs ledger-number">
                <span>Narx: {formatLedger(it.seller_price)}</span>
                <span className="text-right text-[var(--color-signal-up)]">
                  Foyda: {formatLedger(it.seller_profit)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}

function TimerBox({ label, iso }: { label: string; iso: string | null }) {
  if (!iso) return null;
  const diff = new Date(iso).getTime() - Date.now();
  const urgent = diff > 0 && diff < 30 * 60 * 1000;
  const overdue = diff < 0;
  return (
    <div
      className={cn(
        "border rounded-sm p-2",
        urgent
          ? "border-[var(--color-signal-warn)] bg-[var(--color-signal-warn)]/5"
          : overdue
            ? "border-[var(--color-signal-down)] bg-[var(--color-signal-down)]/5"
            : "border-[var(--color-border-hair)]",
      )}
    >
      <div className="label-micro text-[9px]">{label}</div>
      <div className="ledger-number text-sm">{formatDateTime(iso)}</div>
      <div
        className={cn(
          "text-[10px] mt-0.5",
          urgent && "text-[var(--color-signal-warn)]",
          overdue && "text-[var(--color-signal-down)]",
          !urgent && !overdue && "text-[var(--color-fg-muted)]",
        )}
      >
        {overdue ? "muddati o'tgan" : formatRelativeTime(iso).replace(" oldin", " qoldi")}
      </div>
    </div>
  );
}

function Row({
  label,
  value,
  tone,
  strong,
}: {
  label: string;
  value: string;
  tone?: "up" | "down";
  strong?: boolean;
}) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-[var(--color-fg-muted)]">{label}</span>
      <span
        className={cn(
          "ledger-number",
          strong && "font-semibold",
          tone === "up" && "text-[var(--color-signal-up)]",
          tone === "down" && "text-[var(--color-signal-down)]",
        )}
      >
        {value}
      </span>
    </div>
  );
}
