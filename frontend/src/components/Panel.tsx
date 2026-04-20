import type { ReactNode } from "react";

import { IkatStripe } from "@/components/IkatStripe";
import { cn } from "@/lib/cn";

interface PanelProps {
  title?: string;
  label?: string;
  children: ReactNode;
  className?: string;
  showIkat?: boolean;
  actions?: ReactNode;
}

export function Panel({ title, label, children, className, showIkat = false, actions }: PanelProps) {
  return (
    <section className={cn("ak-panel overflow-hidden", className)}>
      {showIkat && <IkatStripe className="absolute left-0 top-0 bottom-0" />}
      {(title || label || actions) && (
        <header className="flex items-start justify-between gap-4 border-b border-[var(--color-border-hair)] px-5 py-4">
          <div className="min-w-0">
            {label && <div className="label-micro mb-1">{label}</div>}
            {title && <h2 className="display-title text-xl">{title}</h2>}
          </div>
          {actions && <div className="flex items-center gap-2 flex-shrink-0">{actions}</div>}
        </header>
      )}
      <div className={cn(showIkat && "pl-[calc(6px+1rem)]")}>{children}</div>
    </section>
  );
}
