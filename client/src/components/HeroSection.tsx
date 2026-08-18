/* =============================================
   HeroSection — ألوان مطابقة لـ osool.dralhoshan.com
   خلفية بيج دافئ + ذهبي بني + بطاقات بيضاء
   الترتيب: عنوان → إحصاءات → بحث
   ============================================= */
import { Search } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import type { Stats } from "@/hooks/useItems";

const GREEN = "#006C35";
const SNOW = "#F7FBFF";
const GREEN_BORDER = "rgb(0 108 53 / 0.25)";

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
      style={{ background: SNOW }}
    >
      {/* Subtle warm gradient overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse 90% 70% at 50% 20%, rgb(0 108 53 / 0.05) 0%, transparent 70%)",
        }}
      />

      {/* Content */}
      <div className="relative z-10 container text-center">

        {/* عنوان نصي بخط ثمانية وفق الترتيب المرجعي */}
        <header className="animate-fade-in-up mb-8" style={{ animationDelay: "0.1s" }}>
          <h1
            className="mx-auto font-bold leading-tight"
            style={{
              fontFamily: "Thmanyah Serif Display",
              color: GREEN,
            }}
          >
            <span className="block text-2xl sm:text-3xl">مكنز</span>
            <span className="mt-1 block text-4xl sm:text-5xl md:text-6xl">القضاء والأنظمة والمحاماة</span>
          </h1>
          <p
            className="mx-auto mt-3 w-fit max-w-3xl rounded-md px-4 py-1.5 text-sm leading-7 sm:text-base"
            style={{
              fontFamily: "Thmanyah Serif Text",
              fontWeight: 500,
              color: SNOW,
            }}
          >
            فهرس يجمع غالب العناوين والروابط التي تخدم القضاء والأنظمة والمحاماة
          </p>
        </header>

        {/* ── Stats Cards — 4 مربعات: إجمالي + القضاء + الأنظمة + المحاماة ── */}
        <div
          className="flex flex-wrap justify-center gap-3 max-w-2xl mx-auto mb-8 animate-fade-in-up"
          style={{ animationDelay: "0.2s" }}
        >
          {/* إجمالي المواد — أولاً بنفس حجم ولون بقية المربعات */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: SNOW,
              borderColor: GREEN_BORDER,
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Tajawal, sans-serif", color: GREEN }}
            >
              {totalItems}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Cairo, sans-serif", color: GREEN }}>
              إجمالي المواد
            </div>
          </div>

          {/* spacer invisible — removed dark card */}

          {/* القضاء */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: SNOW,
              borderColor: GREEN_BORDER,
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Tajawal, sans-serif", color: GREEN }}
            >
              {qadaaCount}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Cairo, sans-serif", color: GREEN }}>
              القضاء
            </div>
          </div>

          {/* الأنظمة */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: SNOW,
              borderColor: GREEN_BORDER,
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Tajawal, sans-serif", color: GREEN }}
            >
              {nizamCount}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Cairo, sans-serif", color: GREEN }}>
              الأنظمة
            </div>
          </div>

          {/* المحاماة */}
          <div
            className="rounded-xl px-6 py-4 text-center border transition-all hover:shadow-md hover:scale-[1.02] min-w-[130px]"
            style={{
              background: SNOW,
              borderColor: GREEN_BORDER,
            }}
          >
            <div
              className="text-2xl sm:text-3xl font-bold"
              style={{ fontFamily: "Tajawal, sans-serif", color: GREEN }}
            >
              {mohamaCount}
            </div>
            <div className="text-xs mt-1" style={{ fontFamily: "Cairo, sans-serif", color: GREEN }}>
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
                ? "shadow-[0_0_20px_rgb(0_108_53/0.2)]"
                : ""
            }`}
            style={{
              borderColor: focused ? GREEN : GREEN_BORDER,
              background: SNOW,
            }}
          >
            <div className="flex items-center pr-4 pl-2">
              <Search className="w-5 h-5" style={{ color: GREEN }} />
            </div>
            <input
              ref={inputRef}
              type="text"
              value={searchValue}
              onChange={(e) => onSearchChange(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              className="flex-1 bg-transparent py-4 text-sm outline-none"
              style={{
                fontFamily: "Cairo, sans-serif",
                direction: "rtl",
                color: GREEN,
              }}
            />
            {searchValue && (
              <button
                onClick={() => onSearchChange("")}
                className="px-3 text-lg transition-colors"
                style={{ color: GREEN }}
              >
                ×
              </button>
            )}
            <button
              onClick={onSearchSubmit}
              className="px-6 py-4 font-bold text-sm transition-colors hover:opacity-90"
              style={{
                fontFamily: "Cairo, sans-serif",
                background: GREEN,
                color: SNOW,
              }}
            >
              بحث
            </button>
          </div>
        </div>

      </div>
    </section>
  );
}
