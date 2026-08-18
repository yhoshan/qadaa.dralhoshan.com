/* =============================================
   HeroSection — تجربة هوية الغلاف
   خلفية جلدية عنّابية + ذهب عتيق + خط ثمانية
   الترتيب: عنوان → إحصاءات → بحث
   ============================================= */
import { Search } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import type { Stats } from "@/hooks/useItems";

const WINE = "oklch(0.22 0.065 23)";
const WINE_SOFT = "oklch(0.30 0.075 24)";
const GOLD = "oklch(0.74 0.13 76)";
const GOLD_BORDER = "oklch(0.62 0.11 72 / 0.7)";
const PARCHMENT = "oklch(0.94 0.03 82)";
const MUTED_GOLD = "oklch(0.74 0.045 72)";
const COVER_ART = "/manus-storage/qadaa-cover-board_67b12c31.png";

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
      style={{ background: `linear-gradient(135deg, ${WINE} 0%, oklch(0.17 0.05 22) 48%, ${WINE_SOFT} 100%)` }}
    >
      {/* Subtle warm gradient overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse 80% 70% at 50% 12%, oklch(0.75 0.14 76 / 0.18) 0%, transparent 65%), repeating-linear-gradient(118deg, oklch(1 0 0 / 0.025) 0 1px, transparent 1px 7px)",
        }}
      />

      {/* Content */}
      <div className="relative z-10 container text-center">

        {/* Cover art — مدمجة مع الخلفية لا كلوحة مستقلة */}
        <div className="relative mx-auto mb-3 w-full max-w-[920px] animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
          <img
            src={COVER_ART}
            alt="مكنز القضاء والأنظمة والمحاماة"
            className="block w-full object-cover"
            style={{
              aspectRatio: "1.83 / 1",
              maxHeight: "390px",
              opacity: 0.9,
              filter: "saturate(0.92) contrast(1.05) brightness(0.93)",
              WebkitMaskImage: "radial-gradient(ellipse 87% 86% at 50% 50%, #000 52%, transparent 100%)",
              maskImage: "radial-gradient(ellipse 87% 86% at 50% 50%, #000 52%, transparent 100%)",
            }}
            loading="eager"
          />
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              background: "linear-gradient(180deg, transparent 35%, oklch(0.20 0.06 23 / 0.58) 82%, oklch(0.20 0.06 23) 100%)",
            }}
          />
        </div>

        {/* Semantic title retained for accessibility and search */}
        <h1
          className="sr-only"
          style={{ fontFamily: "Thmanyah Serif Display, Amiri, serif" }}
        >
          مكنز القضاء والأنظمة والمحاماة
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
              background: "linear-gradient(145deg, oklch(0.34 0.075 25), oklch(0.25 0.065 23))",
              borderColor: GOLD_BORDER,
              boxShadow: "inset 0 1px oklch(1 0 0 / 0.07), 0 8px 18px oklch(0 0 0 / 0.18)",
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Thmanyah Sans, Cairo, sans-serif", color: GOLD }}
            >
              {totalItems}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Thmanyah Sans, Cairo, sans-serif", color: MUTED_GOLD }}>
              إجمالي المواد
            </div>
          </div>

          {/* spacer invisible — removed dark card */}

          {/* القضاء */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: "linear-gradient(145deg, oklch(0.34 0.075 25), oklch(0.25 0.065 23))",
              borderColor: GOLD_BORDER,
              boxShadow: "inset 0 1px oklch(1 0 0 / 0.07), 0 8px 18px oklch(0 0 0 / 0.18)",
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Thmanyah Sans, Cairo, sans-serif", color: GOLD }}
            >
              {qadaaCount}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Thmanyah Sans, Cairo, sans-serif", color: MUTED_GOLD }}>
              القضاء
            </div>
          </div>

          {/* الأنظمة */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: "linear-gradient(145deg, oklch(0.34 0.075 25), oklch(0.25 0.065 23))",
              borderColor: GOLD_BORDER,
              boxShadow: "inset 0 1px oklch(1 0 0 / 0.07), 0 8px 18px oklch(0 0 0 / 0.18)",
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Thmanyah Sans, Cairo, sans-serif", color: GOLD }}
            >
              {nizamCount}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Thmanyah Sans, Cairo, sans-serif", color: MUTED_GOLD }}>
              الأنظمة
            </div>
          </div>

          {/* المحاماة */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: "linear-gradient(145deg, oklch(0.34 0.075 25), oklch(0.25 0.065 23))",
              borderColor: GOLD_BORDER,
              boxShadow: "inset 0 1px oklch(1 0 0 / 0.07), 0 8px 18px oklch(0 0 0 / 0.18)",
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Thmanyah Sans, Cairo, sans-serif", color: GOLD }}
            >
              {mohamaCount}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Thmanyah Sans, Cairo, sans-serif", color: MUTED_GOLD }}>
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
                ? "shadow-[0_0_24px_oklch(0.75_0.14_76/0.26)]"
                : ""
            }`}
            style={{
              borderColor: focused ? GOLD : GOLD_BORDER,
              background: "oklch(0.18 0.05 22 / 0.9)",
            }}
          >
            <div className="flex items-center pr-4 pl-2">
              <Search className="w-5 h-5" style={{ color: GOLD }} />
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
                fontFamily: "Thmanyah Sans, Cairo, sans-serif",
                direction: "rtl",
                color: PARCHMENT,
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
                fontFamily: "Thmanyah Sans, Cairo, sans-serif",
                background: "linear-gradient(135deg, oklch(0.66 0.13 70), oklch(0.48 0.12 55))",
                color: "oklch(0.16 0.045 22)",
              }}
            >
              بحث
            </button>
          </div>
          <p className="text-[10px] mt-2 text-center" style={{ fontFamily: "Thmanyah Sans, Cairo, sans-serif", color: MUTED_GOLD }}>
            اضغط{" "}
            <kbd
              className="px-1.5 py-0.5 rounded font-mono"
              style={{
                background: "oklch(0.31 0.07 24)",
                border: `1px solid ${GOLD_BORDER}`,
                color: GOLD,
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
              background: "oklch(0.26 0.06 23 / 0.92)",
              border: `1px solid ${GOLD_BORDER}`,
              color: PARCHMENT,
              fontFamily: "Thmanyah Sans, Cairo, sans-serif",
            }}
          >
            <span style={{ color: GOLD, fontWeight: 600 }}>⚖️ تنبيه: </span>
            هذا الموقع دليل رقمي للمواد القانونية المتاحة على قنوات تيليجرام عامة. جميع الحقوق محفوظة لأصحابها.
          </div>
        </div>

      </div>
    </section>
  );
}
