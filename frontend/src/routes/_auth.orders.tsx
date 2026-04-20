import { createFileRoute } from "@tanstack/react-router";

import { Panel } from "@/components/Panel";

export const Route = createFileRoute("/_auth/orders")({
  component: () => (
    <div className="p-8">
      <Panel label="SPRINT 4" title="Buyurtmalar kanban">
        <div className="p-6 text-sm text-[var(--color-fg-muted)]">
          Sprint 4 da FBS kanban qurilad.
        </div>
      </Panel>
    </div>
  ),
});
