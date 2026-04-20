import { useSyncExternalStore } from "react";

import { type Language, getSavedLanguage, setLanguage } from "@/i18n";
import { cn } from "@/lib/cn";

function subscribe(cb: () => void) {
  window.addEventListener("storage", cb);
  return () => window.removeEventListener("storage", cb);
}

export function LanguageToggle({ className }: { className?: string }) {
  const current = useSyncExternalStore(subscribe, getSavedLanguage, getSavedLanguage);

  const select = (lang: Language) => {
    setLanguage(lang);
    // Force re-render for consumers not listening to i18n changes
    window.dispatchEvent(new StorageEvent("storage", { key: "anasklad.lang" }));
  };

  return (
    <div className={cn("inline-flex border border-[var(--color-border-hair)] rounded-sm overflow-hidden", className)}>
      {(["uz", "ru"] as Language[]).map((lang) => (
        <button
          key={lang}
          type="button"
          onClick={() => select(lang)}
          className={cn(
            "px-2 py-1 text-[10px] tracking-widest uppercase font-semibold transition-colors cursor-pointer",
            current === lang
              ? "bg-[var(--color-accent-gold)] text-[var(--color-bg-deep)]"
              : "text-[var(--color-fg-muted)] hover:bg-[var(--color-bg-elevated)]",
          )}
        >
          {lang}
        </button>
      ))}
    </div>
  );
}
