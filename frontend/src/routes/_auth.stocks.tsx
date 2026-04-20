import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useRef, useState } from "react";

import { reportsApi } from "@/api/reports";
import { cn } from "@/lib/cn";
import { formatLedger } from "@/lib/format";

export const Route = createFileRoute("/_auth/stocks")({
  component: StocksPage,
});

type Filter = "all" | "available" | "low" | "out";

function StocksPage() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const [page, setPage] = useState(0);

  const { data } = useQuery({
    queryKey: ["stocks", search, filter, page],
    queryFn: () =>
      reportsApi.stocks({
        search: search || undefined,
        only_available: filter === "available",
        only_low: filter === "low",
        only_out: filter === "out",
        page,
        size: 200,
      }),
    placeholderData: keepPreviousData,
  });

  const items = data?.items ?? [];
  const total = data?.total ?? 0;

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 pt-8 pb-4 border-b border-[var(--color-border-hair)]">
        <div className="label-micro mb-2">WAREHOUSE</div>
        <div className="flex items-end justify-between gap-4">
          <div>
            <h1 className="display-title text-4xl">Qoldiqlar</h1>
            <p className="text-[var(--color-fg-muted)] text-sm mt-1 ledger-number">
              {formatLedger(total)} SKU
            </p>
          </div>
          <div className="flex gap-2 items-center">
            <input
              type="search"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(0);
              }}
              placeholder="Qidirish (nom yoki shtrix-kod)..."
              className="ak-input w-72"
            />
          </div>
        </div>

        <div className="flex gap-2 mt-4">
          {(
            [
              ["all", "Hammasi"],
              ["available", "Mavjud"],
              ["low", "Kam qoldi"],
              ["out", "Tugagan"],
            ] as [Filter, string][]
          ).map(([key, label]) => (
            <button
              key={key}
              type="button"
              onClick={() => {
                setFilter(key);
                setPage(0);
              }}
              className={cn(
                "ak-btn text-xs",
                filter === key ? "ak-btn-secondary" : "ak-btn-ghost",
              )}
            >
              {label}
            </button>
          ))}
        </div>
      </header>

      <div className="flex-1 overflow-hidden">
        {items.length === 0 ? (
          <div className="p-12 text-center text-[var(--color-fg-muted)]">
            SKU topilmadi. Integratsiyadan "Sync" qiling.
          </div>
        ) : (
          <VirtualTable items={items} />
        )}
      </div>

      {total > 200 && (
        <div className="border-t border-[var(--color-border-hair)] px-4 py-3 flex items-center justify-between text-xs ledger-number">
          <span className="text-[var(--color-fg-muted)]">
            {formatLedger(page * 200 + 1)} –{" "}
            {formatLedger(Math.min((page + 1) * 200, total))} · jami {formatLedger(total)}
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
              disabled={(page + 1) * 200 >= total}
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

function VirtualTable({ items }: { items: ReturnType<typeof formatItems> }) {
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 52,
    overscan: 10,
  });

  return (
    <div ref={parentRef} className="h-full overflow-auto">
      <div className="sticky top-0 z-10 bg-[var(--color-bg-raised)] border-b border-[var(--color-border-hair)] grid grid-cols-[1fr_120px_110px_110px_110px_120px] label-micro py-3 px-4">
        <span>Mahsulot / SKU</span>
        <span className="text-right">FBO</span>
        <span className="text-right">FBS</span>
        <span className="text-right">Jami</span>
        <span className="text-right">Narx</span>
        <span className="text-right">Tannarx</span>
      </div>
      <div style={{ height: virtualizer.getTotalSize(), position: "relative" }}>
        {virtualizer.getVirtualItems().map((v) => {
          const item = items[v.index];
          if (!item) return null;
          const isOut = item.qty_total === 0;
          const isLow = !isOut && item.qty_total <= 10;
          return (
            <div
              key={item.variant_id}
              style={{
                position: "absolute",
                top: v.start,
                left: 0,
                right: 0,
                height: v.size,
              }}
              className={cn(
                "grid grid-cols-[1fr_120px_110px_110px_110px_120px] items-center px-4 gap-2 border-b border-[var(--color-border-hair)] text-sm",
                isOut && "bg-[var(--color-signal-down)]/5",
              )}
            >
              <div className="min-w-0">
                <div className="truncate">{item.product_title}</div>
                <div className="text-[11px] text-[var(--color-fg-muted)] flex items-center gap-2">
                  <span>{item.sku_title}</span>
                  {item.barcode && (
                    <span className="font-mono text-[var(--color-fg-dim)]">
                      {item.barcode}
                    </span>
                  )}
                  {item.blocked && <span className="ak-pill ak-pill-down">Blok</span>}
                </div>
              </div>
              <span
                className={cn(
                  "ledger-number text-right",
                  item.qty_fbo === 0 && "text-[var(--color-signal-down)]",
                )}
              >
                {formatLedger(item.qty_fbo)}
              </span>
              <span
                className={cn(
                  "ledger-number text-right",
                  item.qty_fbs === 0 && "text-[var(--color-fg-dim)]",
                )}
              >
                {formatLedger(item.qty_fbs)}
              </span>
              <span
                className={cn(
                  "ledger-number text-right font-semibold",
                  isOut && "text-[var(--color-signal-down)]",
                  isLow && "text-[var(--color-signal-warn)]",
                )}
              >
                {formatLedger(item.qty_total)}
              </span>
              <span className="ledger-number text-right">
                {item.price ? formatLedger(item.price) : "—"}
              </span>
              <span className="ledger-number text-right text-[var(--color-fg-muted)]">
                {item.purchase_price ? formatLedger(item.purchase_price) : "—"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function formatItems(items: import("@/api/reports").StockRow[]) {
  return items;
}
