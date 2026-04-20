import { createFileRoute } from "@tanstack/react-router";

import { Panel } from "@/components/Panel";

export const Route = createFileRoute("/_auth/finance")({
  component: () => (
    <div className="p-8">
      <Panel label="SPRINT 5" title="Moliya">
        <div className="p-6 text-sm text-[var(--color-fg-muted)]">
          Sof foyda, komissiya, xarajatlar — Sprint 5 da.
        </div>
      </Panel>
    </div>
  ),
});
