import { createFileRoute } from "@tanstack/react-router";

import { Panel } from "@/components/Panel";

export const Route = createFileRoute("/_auth/stocks")({
  component: () => (
    <div className="p-8">
      <Panel label="SPRINT 3" title="Qoldiqlar">
        <div className="p-6 text-sm text-[var(--color-fg-muted)]">
          FBO + FBS qoldiqlari Sprint 3 da.
        </div>
      </Panel>
    </div>
  ),
});
