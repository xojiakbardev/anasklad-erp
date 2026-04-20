import { cn } from "@/lib/cn";

export function Logo({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center gap-2 select-none", className)}>
      <LogoMark className="w-7 h-7" />
      <div className="flex flex-col leading-none">
        <span className="font-display text-[15px] font-semibold tracking-tight">
          Anasklad
        </span>
        <span className="label-micro mt-1">ERP</span>
      </div>
    </div>
  );
}

export function LogoMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      {/* Compressed ikat ornament mark */}
      <rect x="2" y="2" width="28" height="28" rx="4" fill="#161412" stroke="#2A2622" />
      <path d="M 6 8 L 10 12 L 6 16 L 10 20 L 6 24" stroke="#D9A85A" strokeWidth="1.5" fill="none" strokeLinecap="square" />
      <path d="M 14 6 L 14 26" stroke="#A73935" strokeWidth="1.5" />
      <path d="M 18 8 L 22 12 L 18 16 L 22 20 L 18 24" stroke="#4BA3C3" strokeWidth="1.5" fill="none" strokeLinecap="square" />
      <path d="M 26 10 L 26 22" stroke="#E8D7A8" strokeWidth="1.5" />
    </svg>
  );
}
