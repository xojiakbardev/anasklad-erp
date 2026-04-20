# Anasklad-ERP — Design Brief

> Visual identity, design system, and UI patterns. Paired with `ARCHITECTURE.md` (backend) and `PLAN.md` (delivery).

**Aesthetic direction: "Terminal of the Silk Road"**

A Bloomberg-terminal density meets Uzbek craftsmanship. This is not another pastel SaaS dashboard. It is a precision instrument for merchants — dense, numeric-first, with a signature ornamental detail that anchors cultural identity without kitsch.

---

## 1. Conceptual Commitment

Sellers spend 4–6 hours a day inside this tool. Every pixel should feel like a professional instrument — the confidence of a financial terminal — but warmer than Bloomberg, with one unmistakable cultural fingerprint (the ikat stripe, described below). Dark mode is the default and the only mode that ships in v1.

The product should feel like:
- **Bloomberg Terminal** — numeric density, monospaced figures, amber-on-black legibility
- **Linear** — surgical precision, restraint, typographic confidence
- **MoySklad / 1C** — tabular-dense, decision-making surface
- **Uzbek ornament (ikat)** — one restrained motif, used as a signature

## 2. Color Palette

Not flat blacks. Warm-tinted charcoal that reads as "quality" rather than "cheap dashboard."

```
--bg-deep      #0E0D0B   ← page background (warm near-black, not #000)
--bg-raised    #161412   ← panels
--bg-elevated  #1E1B18   ← modals, popovers
--bg-sunken    #090807   ← input fields (deeper than bg)

--border-hair  #2A2622   ← 1px dividers
--border-sub   #3A342E   ← section separators
--border-focus #D9A85A   ← active states

--fg-primary   #F2EADC   ← body text (warm cream, not #fff)
--fg-muted     #A89F8F
--fg-dim       #6E6658

--accent-gold  #D9A85A   ← primary brand, CTAs, focused states
--accent-deep  #8A6A2E   ← pressed/hover gold
--accent-ink   #4BA3C3   ← links, secondary accent (teal, nod to Samarkand tile)

--signal-up    #7AAE4C   ← profit, positive delta (muted, not candy green)
--signal-down  #C05151   ← loss, negative delta (terracotta, not pure red)
--signal-warn  #E0A43A   ← warnings, low stock
--signal-info  #4BA3C3

--ikat-red     #A73935   ← reserved for ornament stripe only, never text
--ikat-indigo  #2D4564
--ikat-cream   #E8D7A8
```

**Rule:** gold is the product's voice. Everywhere else is restraint. No purple gradients, no neons, no glassmorphism.

## 3. Typography

Must support **Cyrillic + Latin + Uzbek (lotin)** equally well.

- **Display:** `Fraunces` (variable serif, expressive, rare in dashboards). Used for page titles, large KPIs, and one signature h1 per screen. Opsz at high sizes (144), low at body size.
- **Body / UI:** `Inter Display` variant (not plain Inter — the Display optical size cuts the "AI-slop" look). Used at 13/14px. Weight 400/500/600.
- **Numeric / Data:** `JetBrains Mono` with tabular figures forced (`font-variant-numeric: tabular-nums slashed-zero`). Every sum, quantity, SKU, and price is monospace. This is non-negotiable — it's the terminal DNA.
- **Labels / micro:** `Inter Display` at 10–11px, tracking +40, uppercase.

## 4. Scale System

```
Radius:   0 → 2 → 4 → 8     ← cap at 8. No rounded pills anywhere.
Spacing:  2 4 6 8 12 16 24 32 48 64
Shadows:  none for structure. Use borders + bg contrast.
          One "elevated" shadow: 0 12px 32px rgba(0,0,0,0.5) — modals only.
Borders:  1px hairlines default. 2px only for focus/active.
```

No translucent glass. No soft fluffy shadows. Elevation comes from border + bg shift, not blur.

## 5. Component Aesthetics

- **Buttons:** Square-edged (radius 4). Primary = gold fill on dark. Secondary = 1px gold border, transparent fill. Ghost = text with underline on hover. Press state = deep-gold flash (80ms).
- **Tables:** Dense. 32px row height default, 28px compact. Zebra off by default, on via toggle. Sticky header with hairline separator. Right-align all numeric columns. Column resize with gold indicator. Row hover = subtle bg lift (`bg-raised`).
- **Cards / Panels:** Flat. 1px hairline border, no inner shadow. Section label at top-left in uppercase 10px tracked label. Title below in Fraunces.
- **Inputs:** Sunken bg (darker than page), 1px hairline. Focus = 2px gold border, no glow. Labels *above* inputs in caps micro-label. No placeholder-as-label tricks.
- **Charts:** Monochromatic gold ramp for categorical data (5 tints of gold). Dual-axis P&L chart uses gold (revenue) + teal (profit line). No area fills with opacity ramps — use clean lines + dotted grid. Axis labels in mono.
- **Status pills:** Rectangular, 2px radius, 10px uppercase label, 1px border in signal color, 8%-opacity fill. No rounded pills.

## 6. Layout Patterns

- **Split-pane master-detail** for Products, Orders, Stocks (left list, right detail — no page navigation roundtrips).
- **Command palette (⌘K)** as primary navigation. Sellers use keyboard. Must support Cyrillic input.
- **Sticky data toolbar** above every table: filters, saved views, search, density toggle, column config. Looks like a trader toolbar, not a CRUD toolbar.
- **Right drawer** (40vw) for inline edits. Never a modal for data edits.
- **Persistent bottom status bar** — connection health per shop, last sync timestamp, Uzum rate-limit budget remaining. Like a terminal's status line.

## 7. Signature UI Ideas (the two "memorable" moments)

### A. The Ikat Stripe
A **6px-wide vertical stripe** runs down the left edge of every active panel, active nav item, and section header. It is a procedurally generated ikat pattern — short randomized bars in `--ikat-red`, `--ikat-indigo`, `--ikat-cream` — resembling hand-dyed warp threads. Generated at build time as SVG, re-seeded per screen so no two pages look identical. Never decorative filler — always marks "where your attention is." This single motif becomes the product's fingerprint: once a user sees it, every screenshot is recognizably Anasklad.

### B. The Ledger Number
Every financial figure is typeset with deliberate care:
- Tabular monospace, never proportional
- Triple-digit separator = hairline `'` (prime), not comma
- Negatives = parentheses `(1'234'500)` in signal-down, NOT `-1,234,500`
- Delta chips beside numbers show the change: `▲ 12.4%` gold for positive, `▼` terracotta for negative
- Largest KPI on the dashboard is 96px Fraunces with tabular-mono figures — a single line of accountant poetry. This is what someone screenshots for a tweet.

## 8. Motion

Restraint. One orchestrated load per screen (staggered 40ms rows on table mount). Transitions 120ms ease-out. No bouncy springs. No scroll parallax. One exception: when a sync job completes, a **single gold hairline sweeps left-to-right** across the affected panel top edge (600ms). That's the entire motion language.

## 9. Localization Readiness

- All layouts accommodate 1.6x string expansion (Russian tends to run longer than English).
- Date format: `DD.MM.YYYY` (Uzbek/Russian convention), time 24h.
- Number formatting uses Uzbek locale (`fr-FR`-style spacing: `1 234 500 so'm`).
- Currency suffix `so'm` always in lowercase, tracking-normal, never abbreviated.

## 10. What to NEVER do

- No purple gradients. No glassmorphism. No rounded-full pills. No emoji-as-decoration. No Inter (use Inter Display). No soft "Notion-ish" pastels. No hero illustrations. No Lottie animations. No toasts that slide from top — use bottom-right with the hairline sweep. No light mode in v1.

---

**One-line identity:** *"The terminal the Silk Road would have built."*
