import { createFileRoute } from "@tanstack/react-router";

import { Panel } from "@/components/Panel";

export const Route = createFileRoute("/_auth/products")({
  component: () => (
    <div className="p-8">
      <Panel label="SPRINT 3" title="Mahsulotlar sahifasi">
        <div className="p-6 text-sm text-[var(--color-fg-muted)]">
          Sprint 3 da Uzum'dan mahsulotlar sinxronlashdan so'ng to'ldiriladi.
        </div>
      </Panel>
    </div>
  ),
});
