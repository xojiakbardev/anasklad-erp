import type { DailyPoint } from "@/api/finance";
import { formatLedger } from "@/lib/format";

interface Props {
  data: DailyPoint[];
  height?: number;
}

/**
 * Minimal SVG line chart.
 * Gold = revenue, teal = profit.
 * Hairline grid, no area fills — stays true to the terminal aesthetic.
 */
export function ProfitChart({ data, height = 220 }: Props) {
  if (data.length < 2) {
    return (
      <div className="h-[220px] flex items-center justify-center text-[var(--color-fg-muted)] text-sm">
        Yetarli ma'lumot yo'q — kamida 2 kun sotuv kerak
      </div>
    );
  }

  const width = 600;
  const padding = { top: 10, right: 16, bottom: 28, left: 48 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  const maxRevenue = Math.max(...data.map((d) => d.revenue), 1);

  const xStep = innerW / (data.length - 1);
  const yFor = (v: number) => innerH - (v / maxRevenue) * innerH;

  const revenuePath = data
    .map(
      (d, i) =>
        `${i === 0 ? "M" : "L"} ${padding.left + i * xStep} ${padding.top + yFor(d.revenue)}`,
    )
    .join(" ");

  const profitPath = data
    .map(
      (d, i) =>
        `${i === 0 ? "M" : "L"} ${padding.left + i * xStep} ${padding.top + yFor(Math.max(d.profit, 0))}`,
    )
    .join(" ");

  const yTicks = [0, 0.5, 1].map((p) => ({
    value: Math.round(maxRevenue * p),
    y: padding.top + innerH - p * innerH,
  }));

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="w-full h-auto"
      preserveAspectRatio="none"
    >
      {/* Grid */}
      {yTicks.map((t) => (
        <g key={t.y}>
          <line
            x1={padding.left}
            x2={width - padding.right}
            y1={t.y}
            y2={t.y}
            stroke="var(--color-border-hair)"
            strokeDasharray="2 4"
          />
          <text
            x={padding.left - 6}
            y={t.y + 4}
            textAnchor="end"
            className="fill-[var(--color-fg-dim)]"
            style={{ fontSize: "10px", fontFamily: "JetBrains Mono" }}
          >
            {formatLedger(t.value)}
          </text>
        </g>
      ))}

      {/* X axis labels — first + middle + last only */}
      {[0, Math.floor(data.length / 2), data.length - 1].map((i) => {
        const d = data[i];
        if (!d) return null;
        const date = new Date(d.day);
        return (
          <text
            key={i}
            x={padding.left + i * xStep}
            y={height - 8}
            textAnchor={i === 0 ? "start" : i === data.length - 1 ? "end" : "middle"}
            className="fill-[var(--color-fg-dim)]"
            style={{ fontSize: "10px", fontFamily: "JetBrains Mono" }}
          >
            {date.getDate()}.{(date.getMonth() + 1).toString().padStart(2, "0")}
          </text>
        );
      })}

      {/* Revenue line (gold) */}
      <path
        d={revenuePath}
        fill="none"
        stroke="var(--color-accent-gold)"
        strokeWidth="1.5"
        strokeLinecap="square"
      />

      {/* Profit line (teal) */}
      <path
        d={profitPath}
        fill="none"
        stroke="var(--color-accent-ink)"
        strokeWidth="1.5"
        strokeLinecap="square"
        strokeDasharray="0"
      />

      {/* Legend */}
      <g transform={`translate(${padding.left}, ${padding.top + 4})`}>
        <line x1={0} x2={12} y1={0} y2={0} stroke="var(--color-accent-gold)" strokeWidth="1.5" />
        <text x={16} y={4} className="fill-[var(--color-fg-muted)]" style={{ fontSize: "10px" }}>
          Daromad
        </text>
        <line x1={80} x2={92} y1={0} y2={0} stroke="var(--color-accent-ink)" strokeWidth="1.5" />
        <text x={96} y={4} className="fill-[var(--color-fg-muted)]" style={{ fontSize: "10px" }}>
          Foyda
        </text>
      </g>
    </svg>
  );
}
