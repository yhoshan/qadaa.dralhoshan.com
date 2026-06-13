/* =============================================
   HeroSection — Dark Judicial Majesty
   خلفية: قاعة المحكمة الإسلامية المولّدة بالذكاء الاصطناعي
   ============================================= */
import { Search, Scale, BookOpen, FileText, Gavel } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import type { Stats } from "@/hooks/useItems";

interface HeroSectionProps {
  stats: Stats | null;
  searchValue: string;
  onSearchChange: (v: string) => void;
  onSearchSubmit: () => void;
}

const STAT_CARDS = [
  { icon: BookOpen, label: "إجمالي المواد", key: "total_items", color: "oklch(0.72 0.12 75)" },
  { icon: Scale, label: "لها روابط تحميل", key: "with_download_links", color: "oklch(0.55 0.12 195)" },
  { icon: Gavel, label: "أقسام متخصصة", value: "14", color: "oklch(0.55 0.15 25)" },
  { icon: FileText, label: "مصادر ومكتبات", value: "8+", color: "oklch(0.55 0.12 280)" },
];

export default function HeroSection({ stats, searchValue, onSearchChange, onSearchSubmit }: HeroSectionProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [focused, setFocused] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") onSearchSubmit();
  };

  useEffect(() => {
    // Focus search on / key
    const handler = (e: KeyboardEvent) => {
      if (e.key === "/" && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <section className="relative min-h-[85vh] flex flex-col items-center justify-center overflow-hidden">
      {/* Background Image */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: "url('/manus-storage/qadaa-hero-bg_057bc26c.jpg')" }}
      />
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-[oklch(0.08_0.02_240/0.85)] via-[oklch(0.10_0.02_240/0.75)] to-[oklch(0.12_0.02_240/0.95)]" />
      {/* Islamic pattern overlay */}
      <div className="absolute inset-0 islamic-pattern opacity-30" />
      {/* Gold bottom gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[oklch(0.12_0.02_240)] to-transparent" />

      {/* Content */}
      <div className="relative z-10 container text-center pt-24 pb-16">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[oklch(0.72_0.12_75/0.4)] bg-[oklch(0.72_0.12_75/0.08)] mb-6 animate-fade-in-up">
          <Scale className="w-3.5 h-3.5 text-[oklch(0.82_0.10_75)]" />
          <span className="text-xs text-[oklch(0.82_0.10_75)]" style={{ fontFamily: "Tajawal, sans-serif" }}>
            منصة المكانز العلمية
          </span>
        </div>

        {/* Title */}
        <h1
          className="text-4xl sm:text-5xl md:text-6xl font-bold text-[oklch(0.95_0.01_80)] mb-4 leading-tight animate-fade-in-up"
          style={{ fontFamily: "Amiri, serif", animationDelay: "0.1s" }}
        >
          مكنز القضاء والأنظمة
          <br />
          <span className="text-[oklch(0.82_0.10_75)]">والمحاماة</span>
        </h1>

        {/* Subtitle */}
        <p
          className="text-base sm:text-lg text-[oklch(0.72_0.01_240)] max-w-2xl mx-auto mb-10 animate-fade-in-up"
          style={{ fontFamily: "Cairo, sans-serif", animationDelay: "0.2s" }}
        >
          فهرس علمي شامل يجمع مصادر فقه القضاء والأنظمة والمحاماة الشرعية والقانونية
          <br className="hidden sm:block" />
          في مكان واحد — للقضاة والمحامين والباحثين
        </p>

        {/* Search Box */}
        <div
          className={`relative max-w-2xl mx-auto mb-12 animate-fade-in-up transition-all duration-300 ${
            focused ? "scale-[1.02]" : ""
          }`}
          style={{ animationDelay: "0.3s" }}
        >
          <div
            className={`flex items-center rounded-xl border transition-all duration-300 overflow-hidden ${
              focused
                ? "border-[oklch(0.72_0.12_75/0.8)] shadow-[0_0_24px_oklch(0.72_0.12_75/0.2)]"
                : "border-[oklch(0.30_0.04_240)] shadow-lg"
            } bg-[oklch(0.16_0.025_240/0.95)] backdrop-blur-sm`}
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
              className="flex-1 bg-transparent py-4 text-[oklch(0.92_0.01_80)] placeholder-[oklch(0.45_0.01_240)] text-sm outline-none"
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
          <p className="text-[10px] text-[oklch(0.40_0.01_240)] mt-2 text-center">
            اضغط <kbd className="px-1.5 py-0.5 rounded bg-[oklch(0.20_0.03_240)] border border-[oklch(0.25_0.03_240)] text-[oklch(0.60_0.01_240)] font-mono">/</kbd> للبحث السريع
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-3xl mx-auto animate-fade-in-up" style={{ animationDelay: "0.4s" }}>
          {STAT_CARDS.map((card) => {
            const value = card.key
              ? stats
                ? (stats[card.key as keyof Stats] as number)?.toLocaleString("en-US") ?? "..."
                : "..."
              : card.value;
            const Icon = card.icon;
            return (
              <div
                key={card.label}
                className="bg-[oklch(0.16_0.025_240/0.8)] backdrop-blur-sm border border-[oklch(0.25_0.03_240)] rounded-xl p-4 text-center hover:border-[oklch(0.72_0.12_75/0.3)] transition-colors"
              >
                <Icon className="w-5 h-5 mx-auto mb-2" style={{ color: card.color }} />
                <div
                  className="text-2xl font-bold mb-1"
                  style={{ color: card.color, fontFamily: "Tajawal, sans-serif" }}
                >
                  {value}
                </div>
                <div className="text-xs text-[oklch(0.55_0.01_240)]" style={{ fontFamily: "Cairo, sans-serif" }}>
                  {card.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
