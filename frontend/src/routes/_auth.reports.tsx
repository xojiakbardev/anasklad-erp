import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";

import { reportsApi } from "@/api/reports";
import { cn } from "@/lib/cn";
import { formatLedger } from "@/lib/format";

export const Route = createFileRoute("/_auth/reports")({
  component: ReportsPage,
});

type Tab = "abc" | "turnover" | "low_stock";

function ReportsPage() {
  const [tab, setTab] = useState<Tab>("abc");
  const [days, setDays] = useState(30);

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 pt-8 pb-4 border-b border-[var(--color-border-hair)]">
        <div className="label-micro mb-2">ANALYTICS</div>
        <div className="flex items-end justify-between gap-4">
          <h1 className="display-title text-4xl">Hisobotlar</h1>
          <div className="flex gap-2 items-center">
            <span className="label-micro">DAVR:</span>
            {[7, 30, 90].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDays(d)}
                className={cn("ak-btn text-xs", days === d ? "ak-btn-secondary" : "ak-btn-ghost")}
              >
                {d} kun
              </button>
            ))}
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <button
            type="button"
            onClick={() => setTab("abc")}
            className={cn("ak-btn text-xs", tab === "abc" ? "ak-btn-secondary" : "ak-btn-ghost")}
          >
            ABC-analiz
          </button>
          <button
            type="button"
            onClick={() => setTab("turnover")}
            className={cn("ak-btn text-xs", tab === "turnover" ? "ak-btn-secondary" : "ak-btn-ghost")}
          >
            Aylanma
          </button>
          <button
            type="button"
            onClick={() => setTab("low_stock")}
            className={cn("ak-btn text-xs", tab === "low_stock" ? "ak-btn-secondary" : "ak-btn-ghost")}
          >
            Kam qoldiq
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-auto">
        {tab === "abc" && <AbcTab days={days} />}
        {tab === "turnover" && <TurnoverTab days={days} />}
        {tab === "low_stock" && <LowStockTab />}
      </div>
    </div>
  );
}

function AbcTab({ days }: { days: number }) {
  const { data } = useQuery({
    queryKey: ["reports", "abc", days],
    queryFn: () => reportsApi.abc(days),
  });

  const counts = { A: 0, B: 0, C: 0, N: 0 };
  for (const row of data ?? []) counts[row.rank]++;

  return (
    <div>
      {/* Rank summary */}
      <div className="grid grid-cols-4 border-b border-[var(--color-border-hair)]">
        {(["A", "B", "C", "N"] as const).map((rank) => (
          <div
            key={rank}
            className="p-5 border-r border-[var(--color-border-hair)] last:border-r-0"
          >
            <div className="label-micro mb-1">RANK · {rank}</div>
            <div
              className={cn(
                "display-title text-4xl ledger-number",
                rank === "A" && "text-[var(--color-accent-gold)]",
                rank === "B" && "text-[var(--color-accent-ink)]",
                rank === "C" && "text-[var(--color-fg-primary)]",
                rank === "N" && "text-[var(--color-fg-dim)]",
              )}
            >
              {counts[rank]}
            </div>
            <div className="text-[11px] text-[var(--color-fg-muted)] mt-1">
              {rank === "A" && "Eng yaxshi 80% daromad"}
              {rank === "B" && "Keyingi 15%"}
              {rank === "C" && "Oxirgi 5%"}
              {rank === "N" && "Sotuvsiz"}
            </div>
          </div>
        ))}
      </div>

      <div className="sticky top-0 z-10 bg-[var(--color-bg-raised)] border-b border-[var(--color-border-hair)] grid grid-cols-[60px_1fr_100px_130px_130px_100px_100px] label-micro py-3 px-4">
        <span>Rank</span>
        <span>Mahsulot</span>
        <span className="text-right">Dona</span>
        <span className="text-right">Daromad</span>
        <span className="text-right">Foyda</span>
        <span className="text-right">Ulush</span>
        <span className="text-right">Kumulyativ</span>
      </div>
      {(data ?? []).map((r) => (
        <div
          key={r.product_id + String(r.external_id)}
          className="grid grid-cols-[60px_1fr_100px_130px_130px_100px_100px] items-center px-4 py-2 gap-2 border-b border-[var(--color-border-hair)] text-sm"
        >
          <span>
            <span
              className={cn(
                "ak-pill",
                r.rank === "A" && "ak-pill-up",
                r.rank === "B" && "ak-pill-info",
                r.rank === "C" && "ak-pill-muted",
                r.rank === "N" && "ak-pill-down",
              )}
            >
              {r.rank}
            </span>
          </span>
          <span className="truncate">{r.title}</span>
          <span className="ledger-number text-right">{formatLedger(r.units_sold)}</span>
          <span className="ledger-number text-right">{formatLedger(r.revenue)}</span>
          <span
            className={cn(
              "ledger-number text-right",
              r.profit >= 0 ? "text-[var(--color-signal-up)]" : "text-[var(--color-signal-down)]",
            )}
          >
            {formatLedger(r.profit)}
          </span>
          <span className="ledger-number text-right text-[var(--color-fg-muted)]">
            {(r.share * 100).toFixed(1)}%
          </span>
          <span className="ledger-number text-right text-[var(--color-fg-muted)]">
            {(r.cumulative_share * 100).toFixed(1)}%
          </span>
        </div>
      ))}
      {(!data || data.length === 0) && (
        <div className="p-12 text-center text-[var(--color-fg-muted)]">
          Sotuvlar yo'q. Avval finance sync qiling.
        </div>
      )}
    </div>
  );
}

function TurnoverTab({ days }: { days: number }) {
  const { data } = useQuery({
    queryKey: ["reports", "turnover", days],
    queryFn: () => reportsApi.turnover(days, 200),
  });

  return (
    <div>
      <div className="sticky top-0 z-10 bg-[var(--color-bg-raised)] border-b border-[var(--color-border-hair)] grid grid-cols-[1fr_100px_100px_110px_140px] label-micro py-3 px-4">
        <span>Mahsulot / SKU</span>
        <span className="text-right">FBO+FBS</span>
        <span className="text-right">Kunlik o'rt.</span>
        <span className="text-right">Kun qoldi</span>
        <span className="text-right">Tavsiya</span>
      </div>
      {(data ?? []).map((r) => {
        const total = r.qty_fbo + r.qty_fbs;
        const days_remaining = r.days_of_stock;
        let advice: { text: string; tone: "up" | "down" | "warn" | "muted" } = {
          text: "—",
          tone: "muted",
        };
        if (r.avg_daily_sales === 0 && total > 0) {
          advice = { text: "Turib qoldi", tone: "down" };
        } else if (days_remaining !== null) {
          if (days_remaining < 7) advice = { text: "Yangilang", tone: "warn" };
          else if (days_remaining < 30) advice = { text: "Kuzating", tone: "muted" };
          else advice = { text: "Yetarli", tone: "up" };
        }
        return (
          <div
            key={r.variant_id}
            className="grid grid-cols-[1fr_100px_100px_110px_140px] items-center px-4 py-2 gap-2 border-b border-[var(--color-border-hair)] text-sm"
          >
            <div className="min-w-0">
              <div className="truncate">{r.product_title}</div>
              <div className="text-[11px] text-[var(--color-fg-muted)] truncate">
                {r.sku_title}
              </div>
            </div>
            <span className="ledger-number text-right">{formatLedger(total)}</span>
            <span className="ledger-number text-right">
              {r.avg_daily_sales.toFixed(2)}
            </span>
            <span
              className={cn(
                "ledger-number text-right",
                days_remaining !== null && days_remaining < 7 && "text-[var(--color-signal-warn)]",
              )}
            >
              {days_remaining === null ? "∞" : days_remaining.toFixed(0)}
            </span>
            <span className="text-right">
              <span className={cn("ak-pill", `ak-pill-${advice.tone}`)}>{advice.text}</span>
            </span>
          </div>
        );
      })}
      {(!data || data.length === 0) && (
        <div className="p-12 text-center text-[var(--color-fg-muted)]">
          Ma'lumot yo'q
        </div>
      )}
    </div>
  );
}

function LowStockTab() {
  const { data } = useQuery({
    queryKey: ["reports", "low_stock"],
    queryFn: () => reportsApi.lowStock(5, 5),
  });

  return (
    <div>
      <div className="sticky top-0 z-10 bg-[var(--color-bg-raised)] border-b border-[var(--color-border-hair)] grid grid-cols-[1fr_100px_100px_110px] label-micro py-3 px-4">
        <span>Mahsulot / SKU</span>
        <span className="text-right">FBO</span>
        <span className="text-right">FBS</span>
        <span className="text-right">Jami</span>
      </div>
      {(data ?? []).map((r) => {
        const isOut = r.qty_total === 0;
        return (
          <div
            key={r.variant_id}
            className={cn(
              "grid grid-cols-[1fr_100px_100px_110px] items-center px-4 py-2 gap-2 border-b border-[var(--color-border-hair)] text-sm",
              isOut && "bg-[var(--color-signal-down)]/5",
            )}
          >
            <div className="min-w-0">
              <div className="truncate">{r.product_title}</div>
              <div className="text-[11px] text-[var(--color-fg-muted)] truncate">
                {r.sku_title} {r.barcode && `· ${r.barcode}`}
              </div>
            </div>
            <span
              className={cn(
                "ledger-number text-right",
                r.qty_fbo === 0 && "text-[var(--color-signal-down)]",
              )}
            >
              {r.qty_fbo}
            </span>
            <span
              className={cn(
                "ledger-number text-right",
                r.qty_fbs === 0 && "text-[var(--color-fg-dim)]",
              )}
            >
              {r.qty_fbs}
            </span>
            <span
              className={cn(
                "ledger-number text-right font-semibold",
                isOut ? "text-[var(--color-signal-down)]" : "text-[var(--color-signal-warn)]",
              )}
            >
              {r.qty_total}
            </span>
          </div>
        );
      })}
      {(!data || data.length === 0) && (
        <div className="p-12 text-center text-[var(--color-signal-up)]">
          ✓ Qoldiqlar yaxshi! Kritik holat yo'q.
        </div>
      )}
    </div>
  );
}
