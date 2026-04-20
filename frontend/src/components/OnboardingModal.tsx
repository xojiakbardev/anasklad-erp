import { useNavigate } from "@tanstack/react-router";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { IkatStripe } from "@/components/IkatStripe";

const STORAGE_KEY = "anasklad.onboarding_seen";

export function useOnboarding() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem(STORAGE_KEY)) setOpen(true);
  }, []);

  const close = () => {
    localStorage.setItem(STORAGE_KEY, "1");
    setOpen(false);
  };

  return { open, close };
}

interface Step {
  titleKey: string;
  bodyKey: string;
}

const STEPS: Step[] = [
  { titleKey: "onboarding.step1_title", bodyKey: "onboarding.step1_body" },
  { titleKey: "onboarding.step2_title", bodyKey: "onboarding.step2_body" },
  { titleKey: "onboarding.step3_title", bodyKey: "onboarding.step3_body" },
  { titleKey: "onboarding.step4_title", bodyKey: "onboarding.step4_body" },
];

export function OnboardingModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { t } = useTranslation();
  const [step, setStep] = useState(0);
  const navigate = useNavigate();

  if (!open) return null;

  const isLast = step === STEPS.length - 1;
  const current = STEPS[step];
  if (!current) return null;

  const goNext = () => {
    if (isLast) {
      onClose();
      void navigate({ to: "/integrations" });
    } else {
      setStep((s) => s + 1);
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.98 }}
          transition={{ duration: 0.15 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-lg bg-[var(--color-bg-elevated)] border border-[var(--color-border-sub)] rounded-sm overflow-hidden"
        >
          <IkatStripe className="absolute left-0 top-0 bottom-0" />
          <div className="pl-10 pr-7 py-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex gap-1.5">
                {STEPS.map((_, i) => (
                  <div
                    key={i}
                    className={
                      "h-0.5 w-8 transition-colors " +
                      (i === step
                        ? "bg-[var(--color-accent-gold)]"
                        : i < step
                          ? "bg-[var(--color-accent-deep)]"
                          : "bg-[var(--color-border-hair)]")
                    }
                  />
                ))}
              </div>
              <button
                type="button"
                onClick={onClose}
                className="text-[var(--color-fg-muted)] hover:text-[var(--color-fg-primary)] text-lg cursor-pointer"
                aria-label="close"
              >
                ✕
              </button>
            </div>

            <div className="label-micro mb-2">STEP {step + 1} / {STEPS.length}</div>
            <h2 className="display-title text-3xl mb-4">{t(current.titleKey)}</h2>
            <p className="text-[var(--color-fg-muted)] leading-relaxed mb-8">
              {t(current.bodyKey)}
            </p>

            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={onClose}
                className="label-micro hover:text-[var(--color-fg-primary)] cursor-pointer"
              >
                {t("common.skip")}
              </button>
              <div className="flex gap-2">
                {step > 0 && (
                  <button
                    type="button"
                    onClick={() => setStep((s) => s - 1)}
                    className="ak-btn ak-btn-ghost"
                  >
                    ◀ {t("common.back")}
                  </button>
                )}
                <button type="button" onClick={goNext} className="ak-btn ak-btn-primary">
                  {isLast ? t("onboarding.to_integrations") : t("common.next") + " ▶"}
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
