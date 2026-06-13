/* =============================================
   HeroSection — Dark Judicial Majesty (v2)
   بدون صورة خلفية — خلفية داكنة نظيفة
   الترتيب: عنوان → إحصاءات → بحث
   ============================================= */
import { Search } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import type { Stats } from "@/hooks/useItems";

interface HeroSectionProps {
  stats: Stats | null;
  searchValue: string;
  onSearchChange: (v: string) => void;
  onSearchSubmit: () => void;
}

export default function HeroSection({ stats, searchValue, onSearchChange, onSearchSubmit }: HeroSectionProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [focused, setFocused] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") onSearchSubmit();
  };

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "/" && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const totalItems = stats?.total_items?.toLocaleString("en-US") ?? "...";
  const withDownload = stats?.with_download_links?.toLocaleString("en-US") ?? "...";

  return (
    <section className="relative flex flex-col items-center justify-center overflow-hidden pt-28 pb-10"
      style={{ background: "oklch(0.12 0.02 240)" }}
    >
      {/* Islamic pattern overlay — very subtle */}
      <div className="absolute inset-0 islamic-pattern opacity-10 pointer-events-none" />
      {/* Subtle radial glow from center */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse 80% 60% at 50% 30%, oklch(0.72 0.12 75 / 0.06) 0%, transparent 70%)",
        }}
      />

      {/* Content */}
      <div className="relative z-10 container text-center">

        {/* Title — مكنز في سطر، الباقي تحتها */}
        <h1
          className="font-bold text-[oklch(0.95_0.01_80)] leading-tight animate-fade-in-up mb-8"
          style={{ fontFamily: "Amiri, serif", animationDelay: "0.1s" }}
        >
          <span className="block text-5xl sm:text-6xl md:text-7xl text-[oklch(0.82_0.10_75)]">مكنز</span>
          <span className="block text-3xl sm:text-4xl md:text-5xl mt-1">القضاء والأنظمة والمحاماة</span>
        </h1>

        {/* ── Stats Cards — 4 مربعات متجاورة ── */}
        <div
          className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-2xl mx-auto mb-8 animate-fade-in-up"
          style={{ animationDelay: "0.2s" }}
        >
          {/* Card 1 — إجمالي المواد */}
          <div className="rounded-xl p-4 text-center border border-[oklch(0.72_0.12_75/0.5)] bg-[oklch(0.72_0.12_75/0.12)] hover:bg-[oklch(0.72_0.12_75/0.18)] transition-colors">
            <div
              className="text-2xl sm:text-3xl font-bold text-[oklch(0.92_0.01_80)]"
              style={{ fontFamily: "Tajawal, sans-serif" }}
            >
              {totalItems}
            </div>
            <div className="text-xs text-[oklch(0.65_0.01_240)] mt-1" style={{ fontFamily: "Cairo, sans-serif" }}>
              إجمالي المواد
            </div>
          </div>

          {/* Card 2 — لها روابط تحميل */}
          <div className="rounded-xl p-4 text-center border border-[oklch(0.55_0.12_195/0.5)] bg-[oklch(0.55_0.12_195/0.10)] hover:bg-[oklch(0.55_0.12_195/0.16)] transition-colors">
            <div
              className="text-2xl sm:text-3xl font-bold text-[oklch(0.92_0.01_80)]"
              style={{ fontFamily: "Tajawal, sans-serif" }}
            >
              {withDownload}
            </div>
            <div className="text-xs text-[oklch(0.65_0.01_240)] mt-1" style={{ fontFamily: "Cairo, sans-serif" }}>
              لها روابط تحميل
            </div>
          </div>

          {/* Card 3 — أقسام متخصصة */}
          <div className="rounded-xl p-4 text-center border border-[oklch(0.55_0.15_25/0.5)] bg-[oklch(0.55_0.15_25/0.10)] hover:bg-[oklch(0.55_0.15_25/0.16)] transition-colors">
            <div
              className="text-2xl sm:text-3xl font-bold text-[oklch(0.92_0.01_80)]"
              style={{ fontFamily: "Tajawal, sans-serif" }}
            >
              14
            </div>
            <div className="text-xs text-[oklch(0.65_0.01_240)] mt-1" style={{ fontFamily: "Cairo, sans-serif" }}>
              أقسام متخصصة
            </div>
          </div>

          {/* Card 4 — مصادر ومكتبات */}
          <div className="rounded-xl p-4 text-center border border-[oklch(0.55_0.12_280/0.5)] bg-[oklch(0.55_0.12_280/0.10)] hover:bg-[oklch(0.55_0.12_280/0.16)] transition-colors">
            <div
              className="text-2xl sm:text-3xl font-bold text-[oklch(0.92_0.01_80)]"
              style={{ fontFamily: "Tajawal, sans-serif" }}
            >
              8+
            </div>
            <div className="text-xs text-[oklch(0.65_0.01_240)] mt-1" style={{ fontFamily: "Cairo, sans-serif" }}>
              مصادر ومكتبات
            </div>
          </div>
        </div>

        {/* ── Search Box ── */}
        <div
          className={`relative max-w-2xl mx-auto animate-fade-in-up transition-all duration-300 ${focused ? "scale-[1.01]" : ""}`}
          style={{ animationDelay: "0.3s" }}
        >
          <div
            className={`flex items-center rounded-xl border transition-all duration-300 overflow-hidden ${
              focused
                ? "border-[oklch(0.72_0.12_75/0.8)] shadow-[0_0_24px_oklch(0.72_0.12_75/0.2)]"
                : "border-[oklch(0.28_0.04_240)]"
            } bg-[oklch(0.16_0.025_240)]`}
          >
            <div className="flex items-center pr-4 pl-2">
              <Search className="w-5 h-5 text-[oklch(0.72_0.12_75)]" />
            </div>
            <input
              ref={inputRef}
              type="text"
              value={searchValue}
              onChange={(e) => onSearchChange(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              placeholder="ابحث في عناوين الكتب، المؤلفين، الأقسام... (الهمزات لا تؤثر في البحث)"
              className="flex-1 bg-transparent py-4 text-[oklch(0.92_0.01_80)] placeholder-[oklch(0.40_0.01_240)] text-sm outline-none"
              style={{ fontFamily: "Cairo, sans-serif", direction: "rtl" }}
            />
            {searchValue && (
              <button
                onClick={() => onSearchChange("")}
                className="px-3 text-[oklch(0.50_0.01_240)] hover:text-[oklch(0.72_0.12_75)] transition-colors text-lg"
              >
                ×
              </button>
            )}
            <button
              onClick={onSearchSubmit}
              className="px-6 py-4 bg-[oklch(0.72_0.12_75)] text-[oklch(0.12_0.02_240)] font-bold text-sm hover:bg-[oklch(0.78_0.12_75)] transition-colors"
              style={{ fontFamily: "Cairo, sans-serif" }}
            >
              بحث
            </button>
          </div>
          <p className="text-[10px] text-[oklch(0.38_0.01_240)] mt-2 text-center" style={{ fontFamily: "Tajawal, sans-serif" }}>
            اضغط{" "}
            <kbd className="px-1.5 py-0.5 rounded bg-[oklch(0.20_0.03_240)] border border-[oklch(0.25_0.03_240)] text-[oklch(0.55_0.01_240)] font-mono">/</kbd>
            {" "}للبحث السريع
          </p>
        </div>

      </div>
    </section>
  );
}
