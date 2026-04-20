import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { authApi } from "@/api/auth";
import { IkatStripe } from "@/components/IkatStripe";
import { Logo } from "@/components/Logo";
import { ApiError } from "@/lib/api";
import { authStore, useAuth } from "@/stores/auth";

export const Route = createFileRoute("/login")({
  beforeLoad: () => {
    if (authStore.getState().accessToken) {
      throw redirect({ to: "/" });
    }
  },
  component: LoginPage,
});

function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const setSession = useAuth((s) => s.setSession);

  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [tenantName, setTenantName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result =
        mode === "login"
          ? await authApi.login(email, password)
          : await authApi.register({
              email,
              password,
              full_name: fullName || null,
              tenant_name: tenantName,
            });
      setSession({
        user: {
          id: result.user.id,
          email: result.user.email,
          full_name: result.user.full_name,
          tenant_id: result.user.tenant_id,
        },
        accessToken: result.tokens.access_token,
        refreshToken: result.tokens.refresh_token,
        accessExpiresAt: result.tokens.access_expires_at,
      });
      await navigate({ to: "/" });
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      else setError(t("errors.network"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
      {/* Left: brand panel */}
      <div className="relative hidden lg:flex flex-col justify-between p-12 bg-[var(--color-bg-raised)] border-r border-[var(--color-border-hair)] overflow-hidden">
        <IkatStripe className="absolute left-0 top-0 bottom-0" />
        <Logo />

        <div className="relative z-10 max-w-md">
          <div className="label-micro mb-4">{t("login.subtitle")}</div>
          <h1 className="display-title text-5xl mb-6 text-[var(--color-fg-primary)]">
            Ipak yo'li quradigan terminal.
          </h1>
          <p className="text-[var(--color-fg-muted)] leading-relaxed">
            Uzum Market seller'lar uchun zamonaviy ERP — real sof foyda,
            FBO/FBS qoldiqlari, buyurtmalar va moliya bir joyda.
          </p>

          {/* Signature ledger number */}
          <div className="mt-16 border-t border-[var(--color-border-hair)] pt-8">
            <div className="label-micro mb-2">Bugungi foyda</div>
            <div className="ledger-number display-title text-6xl text-[var(--color-accent-gold)]">
              12'487'500
            </div>
            <div className="label-micro mt-2 text-[var(--color-signal-up)]">
              ▲ 14.2% · kechagi kun
            </div>
          </div>
        </div>

        <div className="label-micro">© {new Date().getFullYear()} Anasklad</div>
      </div>

      {/* Right: form */}
      <div className="flex items-center justify-center p-6 lg:p-12">
        <form onSubmit={onSubmit} className="w-full max-w-sm space-y-5">
          <div className="lg:hidden mb-8">
            <Logo />
          </div>

          <div>
            <div className="label-micro mb-1">
              {mode === "login" ? t("login.welcome") : t("register.subtitle")}
            </div>
            <h2 className="display-title text-3xl">
              {mode === "login" ? t("login.signin_cta") : t("register.register_cta")}
            </h2>
          </div>

          {mode === "register" && (
            <>
              <Field label={t("common.full_name")}>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="ak-input"
                  autoComplete="name"
                />
              </Field>
              <Field label={t("common.company")}>
                <input
                  type="text"
                  value={tenantName}
                  onChange={(e) => setTenantName(e.target.value)}
                  required
                  className="ak-input"
                  placeholder="Masalan: Aziz Trade LLC"
                />
              </Field>
            </>
          )}

          <Field label={t("common.email")}>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="ak-input"
              autoComplete="email"
              placeholder="you@example.com"
            />
          </Field>

          <Field label={t("common.password")}>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="ak-input"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
            />
          </Field>

          {error && (
            <div className="ak-pill ak-pill-down w-full justify-center py-2">{error}</div>
          )}

          <button type="submit" disabled={loading} className="ak-btn ak-btn-primary w-full">
            {loading
              ? t("common.loading")
              : mode === "login"
                ? t("login.signin_cta")
                : t("register.register_cta")}
          </button>

          <div className="text-center text-sm text-[var(--color-fg-muted)]">
            {mode === "login" ? (
              <>
                {t("login.no_account")}{" "}
                <button
                  type="button"
                  onClick={() => setMode("register")}
                  className="text-[var(--color-accent-gold)] hover:underline cursor-pointer"
                >
                  {t("login.create_account")}
                </button>
              </>
            ) : (
              <>
                {t("register.have_account")}{" "}
                <button
                  type="button"
                  onClick={() => setMode("login")}
                  className="text-[var(--color-accent-gold)] hover:underline cursor-pointer"
                >
                  {t("register.signin")}
                </button>
              </>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block space-y-1.5">
      <span className="label-micro">{label}</span>
      {children}
    </label>
  );
}
