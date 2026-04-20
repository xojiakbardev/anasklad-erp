import { cn } from "@/lib/cn";

/**
 * The signature motif — a 6px vertical stripe with ikat-like bands.
 * Used on:
 *  - active navigation items
 *  - section headers
 *  - focused panels
 *
 * Position via absolute + inset/left utility classes on the parent.
 */
export function IkatStripe({ className }: { className?: string }) {
  return <div className={cn("ikat-stripe", className)} aria-hidden="true" />;
}
