import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useVirtualizer } from "@tanstack/react-virtual";
import { AnimatePresence, motion } from "framer-motion";
import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { type ProductRow, catalogApi } from "@/api/catalog";
import { IkatStripe } from "@/components/IkatStripe";
import { cn } from "@/lib/cn";
import { formatDateTime, formatLedger } from "@/lib/format";

export const Route = createFileRoute("/_auth/products")({
  component: ProductsPage,
});

const PAGE_SIZE = 100;

function ProductsPage() {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [page, setPage] = useState(0);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ["products", { search, page }],
    queryFn: () => catalogApi.listProducts({ search: search || undefined, page, size: PAGE_SIZE }),
    placeholderData: keepPreviousData,
  });

  const items = data?.items ?? [];
  const total = data?.total ?? 0;

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 pt-8 pb-4 border-b border-[var(--color-border-hair)]">
        <div className="label-micro mb-2">CATALOG</div>
        <div className="flex items-end justify-between gap-4">
          <div>
            <h1 className="display-title text-4xl">{t("nav.products")}</h1>
            <p className="text-[var(--color-fg-muted)] mt-1 text-sm ledger-number">
              {formatLedger(total)} ta mahsulot{isFetching && " · yangilanmoqda..."}
            </p>
          </div>
          <input
            type="search"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            placeholder="Qidirish..."
            className="ak-input w-64"
          />
        </div>
      </header>

      <div
        className={cn(
          "flex-1 grid gap-0 overflow-hidden",
          selectedId ? "grid-cols-[1fr_480px]" : "grid-cols-1",
        )}
      >
        <div className="overflow-hidden flex flex-col border-r border-[var(--color-border-hair)]">
          {isLoading ? (
            <div className="p-12 text-center text-[var(--color-fg-muted)]">
              {t("common.loading")}
            </div>
          ) : items.length === 0 ? (
            <EmptyState />
          ) : (
            <VirtualTable items={items} selectedId={selectedId} onSelect={setSelectedId} />
          )}

          {total > PAGE_SIZE && (
            <div className="border-t border-[var(--color-border-hair)] px-4 py-3 flex items-center justify-between text-xs ledger-number">
              <span className="text-[var(--color-fg-muted)]">
                {formatLedger(page * PAGE_SIZE + 1)} –{" "}
                {formatLedger(Math.min((page + 1) * PAGE_SIZE, total))} · jami {formatLedger(total)}
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
                  disabled={(page + 1) * PAGE_SIZE >= total}
                  className="ak-btn ak-btn-ghost text-xs py-1 px-3"
                >
                  ▶
                </button>
              </div>
            </div>
          )}
        </div>

        <AnimatePresence>
          {selectedId && (
            <motion.div
              initial={{ x: 40, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 40, opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              <DetailDrawer productId={selectedId} onClose={() => setSelectedId(null)} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex-1 flex items-center justify-center p-12">
      <div className="max-w-md text-center">
        <h3 className="display-title text-2xl mb-2">Hali mahsulotlar yo'q</h3>
        <p className="text-[var(--color-fg-muted)]">
          Integratsiyalar sahifasida Uzum do'konini ulang va "Sync" tugmasini bosing.
        </p>
      </div>
    </div>
  );
}

function VirtualTable({
  items,
  selectedId,
  onSelect,
}: {
  items: ProductRow[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 56,
    overscan: 10,
  });

  return (
    <div ref={parentRef} className="flex-1 overflow-auto">
      <div className="sticky top-0 z-10 bg-[var(--color-bg-raised)] border-b border-[var(--color-border-hair)] grid grid-cols-[56px_1fr_120px_120px_120px_120px_140px] label-micro py-3 px-4">
        <span />
        <span>Mahsulot</span>
        <span className="text-right">SKU</span>
        <span className="text-right">FBO</span>
        <span className="text-right">FBS</span>
        <span className="text-right">Narx (so'm)</span>
        <span className="text-right">Yangilangan</span>
      </div>

      <div style={{ height: virtualizer.getTotalSize(), position: "relative" }}>
        {virtualizer.getVirtualItems().map((v) => {
          const item = items[v.index];
          if (!item) return null;
          const isActive = selectedId === item.product_id;
          return (
            <button
              type="button"
              key={item.product_id}
              onClick={() => onSelect(item.product_id)}
              style={{
                position: "absolute",
                top: v.start,
                left: 0,
                right: 0,
                height: v.size,
              }}
              className={cn(
                "relative w-full grid grid-cols-[56px_1fr_120px_120px_120px_120px_140px] items-center px-4 gap-2 text-left border-b border-[var(--color-border-hair)] transition-colors cursor-pointer",
                isActive
                  ? "bg-[var(--color-bg-elevated)] text-[var(--color-fg-primary)]"
                  : "hover:bg-[var(--color-bg-elevated)]",
              )}
            >
              {isActive && <IkatStripe className="absolute left-0 top-1 bottom-1" />}
              <div className="w-10 h-10 rounded-sm bg-[var(--color-bg-sunken)] border border-[var(--color-border-hair)] overflow-hidden flex items-center justify-center">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt=""
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  <span className="text-[var(--color-fg-dim)] text-[10px]">—</span>
                )}
              </div>
              <div className="min-w-0">
                <div className="truncate font-medium">{item.title}</div>
                <div className="ledger-number text-[11px] text-[var(--color-fg-muted)]">
                  #{item.external_id}
                  {item.category && <span className="ml-2">· {item.category}</span>}
                </div>
              </div>
              <span className="ledger-number text-right">{formatLedger(item.sku_count)}</span>
              <span
                className={cn(
                  "ledger-number text-right",
                  item.qty_fbo_total === 0 && "text-[var(--color-signal-down)]",
                )}
              >
                {formatLedger(item.qty_fbo_total)}
              </span>
              <span
                className={cn(
                  "ledger-number text-right",
                  item.qty_fbs_total === 0 && "text-[var(--color-fg-dim)]",
                )}
              >
                {formatLedger(item.qty_fbs_total)}
              </span>
              <span className="ledger-number text-right">
                {item.min_price === null
                  ? "—"
                  : item.min_price === item.max_price
                    ? formatLedger(item.min_price)
                    : `${formatLedger(item.min_price)}…${formatLedger(item.max_price)}`}
              </span>
              <span className="ledger-number text-right text-[var(--color-fg-muted)] text-xs">
                {formatDateTime(item.updated_at)}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function DetailDrawer({
  productId,
  onClose,
}: {
  productId: string;
  onClose: () => void;
}) {
  const { data } = useQuery({
    queryKey: ["variants", productId],
    queryFn: () => catalogApi.listVariants(productId),
  });

  return (
    <aside className="relative h-full overflow-auto bg-[var(--color-bg-raised)]">
      <IkatStripe className="absolute left-0 top-0 bottom-0" />
      <div className="pl-6 pr-5 py-5">
        <div className="flex items-start justify-between gap-2 mb-4">
          <div className="label-micro">SKU RO'YXATI</div>
          <button
            type="button"
            onClick={onClose}
            className="text-[var(--color-fg-muted)] hover:text-[var(--color-fg-primary)] text-lg leading-none cursor-pointer"
            aria-label="close"
          >
            ✕
          </button>
        </div>

        {!data ? (
          <div className="text-[var(--color-fg-muted)] text-sm">Yuklanmoqda...</div>
        ) : data.length === 0 ? (
          <div className="text-[var(--color-fg-muted)] text-sm">SKU topilmadi</div>
        ) : (
          <div className="space-y-3">
            {data.map((v) => (
              <div
                key={v.id}
                className="border border-[var(--color-border-hair)] rounded-sm p-3"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="min-w-0">
                    <div className="font-medium truncate">{v.title || "—"}</div>
                    {v.characteristics && (
                      <div className="text-xs text-[var(--color-fg-muted)] mt-0.5">
                        {v.characteristics}
                      </div>
                    )}
                  </div>
                  {v.archived && <span className="ak-pill ak-pill-muted">Arxiv</span>}
                  {v.blocked && <span className="ak-pill ak-pill-down">Blok</span>}
                </div>

                <div className="grid grid-cols-4 gap-2 text-xs">
                  <Stat label="FBO" value={formatLedger(v.qty_fbo)} />
                  <Stat label="FBS" value={formatLedger(v.qty_fbs)} />
                  <Stat label="Sotildi" value={formatLedger(v.qty_sold_total)} />
                  <Stat label="Qaytdi" value={formatLedger(v.qty_returned_total)} />
                </div>

                <div className="grid grid-cols-2 gap-2 mt-2 text-xs border-t border-[var(--color-border-hair)] pt-2">
                  <Stat label="Narx" value={v.price ? formatLedger(v.price) : "—"} />
                  <Stat
                    label="Tannarx"
                    value={v.purchase_price ? formatLedger(v.purchase_price) : "—"}
                  />
                </div>

                {(v.barcode || v.ikpu) && (
                  <div className="mt-2 text-[10px] font-mono text-[var(--color-fg-dim)] space-y-0.5">
                    {v.barcode && <div>BC: {v.barcode}</div>}
                    {v.ikpu && <div>IKPU: {v.ikpu}</div>}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="label-micro text-[9px]">{label}</div>
      <div className="ledger-number">{value}</div>
    </div>
  );
}
