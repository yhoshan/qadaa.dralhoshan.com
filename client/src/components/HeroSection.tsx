/* =============================================
   HeroSection — ألوان مطابقة لـ osool.dralhoshan.com
   خلفية بيج دافئ + ذهبي بني + بطاقات بيضاء
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
    <section
      className="relative flex flex-col items-center justify-center overflow-hidden pt-28 pb-10"
      style={{ background: "oklch(0.98 0.01 85)" }}
    >
      {/* Subtle warm gradient overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse 90% 70% at 50% 20%, oklch(0.48 0.12 68 / 0.05) 0%, transparent 70%)",
        }}
      />

      {/* Content */}
      <div className="relative z-10 container text-center">

        {/* Title — مكنز في سطر، الباقي تحتها */}
        <h1
          className="font-bold leading-tight animate-fade-in-up mb-8"
          style={{ fontFamily: "Amiri, serif", animationDelay: "0.1s" }}
        >
          <span
            className="block text-5xl sm:text-6xl md:text-7xl"
            style={{ color: "oklch(0.48 0.12 68)" }}
          >
            مكنز
          </span>
          <span
            className="block text-3xl sm:text-4xl md:text-5xl mt-1"
            style={{ color: "oklch(0.48 0.12 68)", fontFamily: "Amiri, serif" }}
          >
            القضاء والأنظمة والمحاماة
          </span>
        </h1>

        {/* ── Stats Cards — 4 مربعات متجاورة — مطابقة لـ osool ── */}
        <div
          className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-2xl mx-auto mb-8 animate-fade-in-up"
          style={{ animationDelay: "0.2s" }}
        >
          {[{num: totalItems, label: "إجمالي المواد"}, {num: withDownload, label: "لها روابط تحميل"}, {num: "14", label: "أقسام متخصصة"}, {num: "8+", label: "مصادر ومكتبات"}].map((card) => (
            <div
              key={card.label}
              className="rounded-xl p-4 text-center border transition-all hover:shadow-md hover:scale-[1.02]"
              style={{
                background: "oklch(0.93 0.03 80)",
                borderColor: "oklch(0.88 0.04 78)",
              }}
            >
              <div
                className="text-2xl sm:text-3xl font-bold"
                style={{ fontFamily: "Tajawal, sans-serif", color: "oklch(0.18 0.04 50)" }}
              >
                {card.num}
              </div>
              <div className="text-xs mt-1" style={{ fontFamily: "Cairo, sans-serif", color: "oklch(0.52 0.06 60)" }}>
                {card.label}
              </div>
            </div>
          ))}
        </div>

        {/* ── Search Box ── */}
        <div
          className={`relative max-w-2xl mx-auto animate-fade-in-up transition-all duration-300 ${focused ? "scale-[1.01]" : ""}`}
          style={{ animationDelay: "0.3s" }}
        >
          <div
            className={`flex items-center rounded-xl border transition-all duration-300 overflow-hidden ${
              focused
                ? "shadow-[0_0_20px_oklch(0.48_0.12_68/0.2)]"
                : ""
            }`}
            style={{
              borderColor: focused ? "oklch(0.48 0.12 68)" : "oklch(0.88 0.04 78)",
              background: "oklch(1 0 0)",
            }}
          >
            <div className="flex items-center pr-4 pl-2">
              <Search className="w-5 h-5" style={{ color: "oklch(0.48 0.12 68)" }} />
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
              className="flex-1 bg-transparent py-4 text-sm outline-none"
              style={{
                fontFamily: "Cairo, sans-serif",
                direction: "rtl",
                color: "oklch(0.18 0.04 50)",
              }}
            />
            {searchValue && (
              <button
                onClick={() => onSearchChange("")}
                className="px-3 text-lg transition-colors"
                style={{ color: "oklch(0.52 0.06 60)" }}
              >
                ×
              </button>
            )}
            <button
              onClick={onSearchSubmit}
              className="px-6 py-4 font-bold text-sm transition-colors hover:opacity-90"
              style={{
                fontFamily: "Cairo, sans-serif",
                background: "rgb(139, 105, 20)",
                color: "white",
              }}
            >
              بحث
            </button>
          </div>
          <p className="text-[10px] mt-2 text-center" style={{ fontFamily: "Tajawal, sans-serif", color: "oklch(0.60 0.04 60)" }}>
            اضغط{" "}
            <kbd
              className="px-1.5 py-0.5 rounded font-mono"
              style={{
                background: "oklch(0.93 0.03 80)",
                border: "1px solid oklch(0.88 0.04 78)",
                color: "oklch(0.48 0.12 68)",
              }}
            >
              /
            </kbd>
            {" "}للبحث السريع
          </p>
        </div>

      </div>
    </section>
  );
}
