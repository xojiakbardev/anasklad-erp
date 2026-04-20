import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";

import { financeApi } from "@/api/finance";
import { cn } from "@/lib/cn";
import { formatDateTime, formatLedger } from "@/lib/format";

export const Route = createFileRoute("/_auth/finance")({
  component: FinancePage,
});

function FinancePage() {
  const [tab, setTab] = useState<"sales" | "expenses">("sales");

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 pt-8 pb-4 border-b border-[var(--color-border-hair)] flex items-end justify-between gap-4">
        <div>
          <div className="label-micro mb-2">FINANCE</div>
          <h1 className="display-title text-4xl">Moliya</h1>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setTab("sales")}
            className={cn("ak-btn text-xs", tab === "sales" ? "ak-btn-secondary" : "ak-btn-ghost")}
          >
            Sotuvlar
          </button>
          <button
            type="button"
            onClick={() => setTab("expenses")}
            className={cn("ak-btn text-xs", tab === "expenses" ? "ak-btn-secondary" : "ak-btn-ghost")}
          >
            Xarajatlar
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-hidden">
        {tab === "sales" ? <SalesTab /> : <ExpensesTab />}
      </div>
    </div>
  );
}

function SalesTab() {
  const [page, setPage] = useState(0);
  const { data } = useQuery({
    queryKey: ["sales", page],
    queryFn: () => financeApi.listSales(page, 100),
    placeholderData: keepPreviousData,
  });

  const items = data?.items ?? [];

  return (
    <div className="h-full overflow-auto">
      <div className="sticky top-0 z-10 bg-[var(--color-bg-raised)] border-b border-[var(--color-border-hair)] grid grid-cols-[140px_1fr_90px_120px_110px_110px_120px] label-micro py-3 px-4">
        <span>Sana</span>
        <span>Mahsulot</span>
        <span className="text-right">Dona</span>
        <span className="text-right">Narx</span>
        <span className="text-right">Komissiya</span>
        <span className="text-right">Logistika</span>
        <span className="text-right">Sof foyda</span>
      </div>
      {items.length === 0 && (
        <div className="p-12 text-center text-[var(--color-fg-muted)]">
          Sotuvlar topilmadi. Integratsiyadan "Sync" qiling.
        </div>
      )}
      {items.map((s) => (
        <div
          key={s.id}
          className="grid grid-cols-[140px_1fr_90px_120px_110px_110px_120px] items-center px-4 py-2 gap-2 border-b border-[var(--color-border-hair)] hover:bg-[var(--color-bg-elevated)]"
        >
          <span className="ledger-number text-xs text-[var(--color-fg-muted)]">
            {formatDateTime(s.sold_at)}
          </span>
          <div className="min-w-0">
            <div className="truncate text-sm">{s.product_title || "—"}</div>
            <div className="text-[11px] text-[var(--color-fg-muted)] truncate">
              {s.sku_title || ""}
              {s.return_cause && (
                <span className="ml-2 text-[var(--color-signal-warn)]">· {s.return_cause}</span>
              )}
            </div>
          </div>
          <span className="ledger-number text-right">{s.amount}</span>
          <span className="ledger-number text-right">{formatLedger(s.seller_price)}</span>
          <span className="ledger-number text-right text-[var(--color-signal-down)]">
            {s.commission ? `(${formatLedger(s.commission)})` : "—"}
          </span>
          <span className="ledger-number text-right text-[var(--color-signal-down)]">
            {s.logistic_delivery_fee ? `(${formatLedger(s.logistic_delivery_fee)})` : "—"}
          </span>
          <span
            className={cn(
              "ledger-number text-right font-semibold",
              (s.seller_profit ?? 0) >= 0
                ? "text-[var(--color-signal-up)]"
                : "text-[var(--color-signal-down)]",
            )}
          >
            {formatLedger(s.seller_profit)}
          </span>
        </div>
      ))}
      <PagerBar page={page} total={data?.total ?? 0} size={100} onPage={setPage} />
    </div>
  );
}

function ExpensesTab() {
  const [page, setPage] = useState(0);
  const { data } = useQuery({
    queryKey: ["expenses", page],
    queryFn: () => financeApi.listExpenses(page, 100),
    placeholderData: keepPreviousData,
  });

  const items = data?.items ?? [];

  return (
    <div className="h-full overflow-auto">
      <div className="sticky top-0 z-10 bg-[var(--color-bg-raised)] border-b border-[var(--color-border-hair)] grid grid-cols-[140px_1fr_140px_120px_120px] label-micro py-3 px-4">
        <span>Sana</span>
        <span>Nomi</span>
        <span>Turi</span>
        <span className="text-right">Dona</span>
        <span className="text-right">Summa</span>
      </div>
      {items.length === 0 && (
        <div className="p-12 text-center text-[var(--color-fg-muted)]">
          Xarajatlar topilmadi.
        </div>
      )}
      {items.map((e) => (
        <div
          key={e.id}
          className="grid grid-cols-[140px_1fr_140px_120px_120px] items-center px-4 py-2 gap-2 border-b border-[var(--color-border-hair)] hover:bg-[var(--color-bg-elevated)]"
        >
          <span className="ledger-number text-xs text-[var(--color-fg-muted)]">
            {formatDateTime(e.date_service)}
          </span>
          <div className="min-w-0">
            <div className="truncate text-sm">{e.name || "—"}</div>
            <div className="text-[11px] text-[var(--color-fg-muted)]">{e.source_kind}</div>
          </div>
          <span>
            <span
              className={cn(
                "ak-pill",
                e.type === "INCOME" ? "ak-pill-up" : "ak-pill-down",
              )}
            >
              {e.type === "INCOME" ? "Kirim" : "Chiqim"}
            </span>
          </span>
          <span className="ledger-number text-right">{e.amount || "—"}</span>
          <span
            className={cn(
              "ledger-number text-right font-semibold",
              e.type === "INCOME"
                ? "text-[var(--color-signal-up)]"
                : "text-[var(--color-signal-down)]",
            )}
          >
            {e.type === "OUTCOME" && e.payment_price
              ? `(${formatLedger(e.payment_price)})`
              : formatLedger(e.payment_price)}
          </span>
        </div>
      ))}
      <PagerBar page={page} total={data?.total ?? 0} size={100} onPage={setPage} />
    </div>
  );
}

function PagerBar({
  page,
  total,
  size,
  onPage,
}: {
  page: number;
  total: number;
  size: number;
  onPage: (n: number) => void;
}) {
  if (total <= size) return null;
  return (
    <div className="sticky bottom-0 border-t border-[var(--color-border-hair)] bg-[var(--color-bg-raised)] px-4 py-3 flex items-center justify-between text-xs ledger-number">
      <span className="text-[var(--color-fg-muted)]">
        {formatLedger(page * size + 1)} – {formatLedger(Math.min((page + 1) * size, total))} · jami{" "}
        {formatLedger(total)}
      </span>
      <div className="flex gap-1">
        <button
          type="button"
          onClick={() => onPage(Math.max(0, page - 1))}
          disabled={page === 0}
          className="ak-btn ak-btn-ghost text-xs py-1 px-3"
        >
          ◀
        </button>
        <button
          type="button"
          onClick={() => onPage(page + 1)}
          disabled={(page + 1) * size >= total}
          className="ak-btn ak-btn-ghost text-xs py-1 px-3"
        >
          ▶
        </button>
      </div>
    </div>
  );
}
