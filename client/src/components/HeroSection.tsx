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
  const qadaaCount = stats?.qadaa_count?.toLocaleString("en-US") ?? "...";
  const nizamCount = stats?.nizam_count?.toLocaleString("en-US") ?? "...";
  const mohamaCount = stats?.mohama_count?.toLocaleString("en-US") ?? "...";

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

        {/* ── Stats Cards — 4 مربعات: إجمالي + القضاء + الأنظمة + المحاماة ── */}
        <div
          className="flex flex-wrap justify-center gap-3 max-w-2xl mx-auto mb-8 animate-fade-in-up"
          style={{ animationDelay: "0.2s" }}
        >
          {/* إجمالي المواد — أولاً بنفس حجم ولون بقية المربعات */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: "oklch(0.93 0.03 80)",
              borderColor: "oklch(0.88 0.04 78)",
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Tajawal, sans-serif", color: "oklch(0.18 0.04 50)" }}
            >
              {totalItems}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Cairo, sans-serif", color: "oklch(0.52 0.06 60)" }}>
              إجمالي المواد
            </div>
          </div>

          {/* spacer invisible — removed dark card */}

          {/* القضاء */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: "oklch(0.93 0.03 80)",
              borderColor: "oklch(0.88 0.04 78)",
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Tajawal, sans-serif", color: "oklch(0.18 0.04 50)" }}
            >
              {qadaaCount}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Cairo, sans-serif", color: "oklch(0.52 0.06 60)" }}>
              القضاء
            </div>
          </div>

          {/* الأنظمة */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: "oklch(0.93 0.03 80)",
              borderColor: "oklch(0.88 0.04 78)",
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Tajawal, sans-serif", color: "oklch(0.18 0.04 50)" }}
            >
              {nizamCount}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Cairo, sans-serif", color: "oklch(0.52 0.06 60)" }}>
              الأنظمة
            </div>
          </div>

          {/* المحاماة */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: "oklch(0.93 0.03 80)",
              borderColor: "oklch(0.88 0.04 78)",
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Tajawal, sans-serif", color: "oklch(0.18 0.04 50)" }}
            >
              {mohamaCount}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Cairo, sans-serif", color: "oklch(0.52 0.06 60)" }}>
              المحاماة
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
              placeholder="ابحث في عناوين الكتب، المؤلفين، الأقسام..."
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

          {/* Legal disclaimer */}
          <div
            className="mt-4 mx-auto max-w-xl px-4 py-2.5 rounded-lg text-center text-xs leading-relaxed"
            style={{
              background: "oklch(0.93 0.03 80)",
              border: "1px solid oklch(0.85 0.05 78)",
              color: "oklch(0.40 0.06 55)",
              fontFamily: "Cairo, sans-serif",
            }}
          >
            <span style={{ color: "oklch(0.48 0.12 68)", fontWeight: 600 }}>⚖️ تنبيه: </span>
            هذا الموقع دليل رقمي للمواد القانونية المتاحة على قنوات تيليجرام عامة. جميع الحقوق محفوظة لأصحابها.
            {" "}
            <a
              href="/disclaimer"
              style={{ color: "rgb(139, 105, 20)", fontWeight: 600, textDecoration: "underline" }}
            >
              اقرأ إخلاء المسؤولية
            </a>
          </div>
        </div>

      </div>
    </section>
  );
}
