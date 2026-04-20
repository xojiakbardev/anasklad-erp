/**
 * Ledger-style number formatting.
 * - Tabular spacing, hairline prime (') separator
 * - Negatives as parentheses
 */
export function formatLedger(value: number | null | undefined, opts?: { suffix?: string }): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const abs = Math.abs(value);
  const parts = Math.round(abs).toString().split("");
  for (let i = parts.length - 3; i > 0; i -= 3) parts.splice(i, 0, "\u2019");
  const s = parts.join("");
  const core = value < 0 ? `(${s})` : s;
  return opts?.suffix ? `${core} ${opts.suffix}` : core;
}

export function formatSum(value: number | null | undefined): string {
  return formatLedger(value, { suffix: "so'm" });
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function formatRelativeTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  const min = Math.round(diff / 60_000);
  if (min < 1) return "hozir";
  if (min < 60) return `${min} daq oldin`;
  const h = Math.round(min / 60);
  if (h < 24) return `${h} soat oldin`;
  const d = Math.round(h / 24);
  return `${d} kun oldin`;
}
