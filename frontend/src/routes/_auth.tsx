import { createFileRoute, redirect } from "@tanstack/react-router";

import { AppShell } from "@/components/AppShell";
import { authStore } from "@/stores/auth";

export const Route = createFileRoute("/_auth")({
  beforeLoad: () => {
    if (!authStore.getState().accessToken) {
      throw redirect({ to: "/login" });
    }
  },
  component: AppShell,
});
