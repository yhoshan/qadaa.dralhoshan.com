/* =============================================
   JournalsSection — يحافظ على ألوان قسم المواد الحالية
   ويضيف فلتر بلد الإصدار محلياً للمجلات الرسمية فقط.
   ============================================= */
import { BookOpen, ExternalLink, ChevronLeft } from "lucide-react";
import { useMemo, useState } from "react";
import { OFFICIAL_JOURNALS } from "@/data/officialJournals";

const GOLD = "rgb(139, 105, 20)";
const GOLD_LIGHT = "oklch(0.88 0.06 78)";
const WARM_BG = "oklch(0.96 0.015 80)";
const CARD_BG = "oklch(0.99 0.005 80)";
const BORDER = "oklch(0.85 0.05 75)";
const TEXT_DARK = "oklch(0.18 0.04 50)";
const TEXT_MUTED = "oklch(0.52 0.06 60)";

interface JournalsSectionProps {
  onFilterBySource?: (source: string) => void;
  onFilterByCategory?: (category: string) => void;
}

type JournalCard = {
  name: string;
  country?: string;
  description: string;
  count?: string;
  countLabel?: string;
  color: string;
  filterType?: "source" | "title";
  filterValue?: string;
  officialLink?: string;
};

const BASE_JOURNALS: JournalCard[] = [
  {
    name: "مجلة العدل السعودية",
    description: "315 مادة قضائية ونظامية من مجلة العدل الصادرة عن وزارة العدل السعودية",
    count: "315",
    color: "oklch(0.48 0.12 68)",
    filterType: "source",
    filterValue: "موقع بحوث - مجلة العدل - وزارة العدل (السعودية)",
  },
  {
    name: "مجلة قضاء السعودية",
    description: "212 مادة قانونية وقضائية من مجلة قضاء السعودية المتخصصة",
    count: "212",
    color: "oklch(0.60 0.13 250)",
    filterType: "source",
    filterValue: "موقع بحوث - مجلة قضاء (السعودية)",
  },
  {
    name: "مجلة المحاماة",
    description: "أعداد مجلة المحاماة المصرية منذ 1920 حتى 2018 — أقدم مجلة قانونية عربية",
    count: "400+",
    color: "oklch(0.72 0.12 45)",
    filterType: "title",
    filterValue: "مجلة المحاماة",
  },
  {
    name: "مجلة الحقوق",
    description: "مجلة الحقوق الكويتية والأردنية والمصرية — مجلات أكاديمية محكّمة",
    count: "140+",
    color: "oklch(0.65 0.14 160)",
    filterType: "title",
    filterValue: "مجلة الحقوق",
  },
  {
    name: "مجلة العدل",
    description: "مجلة العدل اللبنانية وغيرها من مجلات العدالة القضائية",
    count: "25+",
    color: "oklch(0.62 0.13 250)",
    filterType: "title",
    filterValue: "مجلة العدل",
  },
  {
    name: "مجلة القانون والاقتصاد",
    description: "مجلة القانون والاقتصاد المصرية — دراسات قانونية وتشريعية متخصصة",
    count: "15+",
    color: "oklch(0.68 0.15 30)",
    filterType: "title",
    filterValue: "مجلة القانون",
  },
  {
    name: "مجلة الدراسات القانونية",
    description: "مجلة الدراسات القانونية والقضائية — أبحاث ودراسات محكّمة",
    count: "35+",
    color: "oklch(0.60 0.14 300)",
    filterType: "title",
    filterValue: "مجلة الدراسات القانونية",
  },
  {
    name: "مجلة القضاء والتشريع",
    description: "مجلة القضاء والتشريع التونسية — مرجع قانوني متخصص في التشريع المقارن",
    count: "18+",
    color: "oklch(0.66 0.13 200)",
    filterType: "title",
    filterValue: "مجلة القضاء والتشريع",
  },
];

const JOURNALS: JournalCard[] = [...BASE_JOURNALS, ...OFFICIAL_JOURNALS];

export default function JournalsSection({ onFilterBySource, onFilterByCategory }: JournalsSectionProps) {
  const [selectedCountry, setSelectedCountry] = useState("all");
  const countries = useMemo(
    () => Array.from(new Set(OFFICIAL_JOURNALS.map((journal) => journal.country))).sort((a, b) => {
      if (a === "السعودية") return -1;
      if (b === "السعودية") return 1;
      if (a === "دولية") return 1;
      if (b === "دولية") return -1;
      return a.localeCompare(b, "ar");
    }),
    []
  );
  const visibleJournals: JournalCard[] = selectedCountry === "all"
    ? JOURNALS
    : OFFICIAL_JOURNALS.filter((journal) => journal.country === selectedCountry);

  return (
    <section
      dir="rtl"
      className="journals-theme"
      style={{
        background: `linear-gradient(180deg, ${WARM_BG} 0%, oklch(0.94 0.02 78) 100%)`,
        borderTop: `1px solid ${BORDER}`,
        borderBottom: `1px solid ${BORDER}`,
        padding: "3rem 0",
      }}
    >
      <div className="container">
        {/* Header */}
        <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div
              className="journals-heading-icon"
              style={{
                background: `linear-gradient(135deg, ${GOLD}, oklch(0.72 0.14 55))`,
                borderRadius: "12px",
                padding: "10px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2
                style={{
                  fontFamily: "Amiri, serif",
                  fontSize: "clamp(1.4rem, 3vw, 1.9rem)",
                  fontWeight: 700,
                  color: TEXT_DARK,
                  lineHeight: 1.3,
                }}
              >
                المجلات المتخصصة
              </h2>
            </div>
          </div>
          <button
            onClick={() => onFilterByCategory?.("المجلات القانونية")}
            style={{
              fontFamily: "Cairo, sans-serif",
              fontSize: "0.85rem",
              color: GOLD,
              background: "transparent",
              border: `1px solid ${GOLD_LIGHT}`,
              borderRadius: "8px",
              padding: "6px 16px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "4px",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = GOLD_LIGHT;
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = "transparent";
            }}
          >
            عرض الكل
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>

        <div className="mb-6" style={{ fontFamily: "Cairo, sans-serif" }}>
          <label className="flex items-center gap-2" style={{ color: TEXT_MUTED }}>
            <span className="text-xs font-semibold">بلد الإصدار:</span>
            <select
              value={selectedCountry}
              onChange={(event) => setSelectedCountry(event.target.value)}
              aria-label="فلتر بلد إصدار المجلات"
              className="text-xs outline-none transition-colors"
              style={{
                fontFamily: "Cairo, sans-serif",
                minWidth: "190px",
                background: CARD_BG,
                color: TEXT_DARK,
                border: `1px solid ${BORDER}`,
                borderRadius: "8px",
                padding: "7px 12px",
              }}
            >
              <option value="all">الكل</option>
              {countries.map((country) => (
                <option key={country} value={country}>
                  {country === "دولية" ? "المجلات الدولية باللغة الإنجليزية" : country}
                </option>
              ))}
            </select>
          </label>
        </div>

        {/* Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
            gap: "1rem",
          }}
        >
          {visibleJournals.map((journal) => (
            <button
              key={`${journal.country || "base"}-${journal.name}`}
              className="journal-card"
              onClick={() => {
                if (journal.officialLink) {
                  window.open(journal.officialLink, "_blank", "noopener,noreferrer");
                  return;
                }
                if (journal.filterType === "title") onFilterBySource?.(journal.filterValue || "");
                else onFilterBySource?.(journal.filterValue || "");
              }}
              style={{
                background: CARD_BG,
                border: `1px solid ${BORDER}`,
                borderRadius: "12px",
                padding: "1.25rem",
                cursor: "pointer",
                textAlign: "right",
                transition: "all 0.2s cubic-bezier(0.23, 1, 0.32, 1)",
                display: "flex",
                flexDirection: "column",
                gap: "0.6rem",
                boxShadow: "0 1px 4px oklch(0 0 0 / 0.06)",
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget as HTMLButtonElement;
                el.style.transform = "translateY(-3px)";
                el.style.boxShadow = "0 6px 20px oklch(0 0 0 / 0.10)";
                el.style.borderColor = GOLD_LIGHT;
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget as HTMLButtonElement;
                el.style.transform = "translateY(0)";
                el.style.boxShadow = "0 1px 4px oklch(0 0 0 / 0.06)";
                el.style.borderColor = BORDER;
              }}
            >
              {/* Top row */}
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <div style={{ flex: 1 }}>
                  <h3
                    style={{
                      fontFamily: "Amiri, serif",
                      fontSize: "1.05rem",
                      fontWeight: 700,
                      color: TEXT_DARK,
                      lineHeight: 1.3,
                    }}
                  >
                    {journal.name}
                  </h3>
                  <span
                    style={{
                      fontFamily: "Cairo, sans-serif",
                      fontSize: "0.75rem",
                      color: GOLD,
                      fontWeight: 600,
                    }}
                  >
                    {journal.countLabel || `${journal.count} عدد`}
                  </span>
                </div>
                <ExternalLink
                  className="w-4 h-4 flex-shrink-0"
                  style={{ color: TEXT_MUTED, opacity: 0.6 }}
                />
              </div>

              {/* Description */}
              <p
                style={{
                  fontFamily: "Cairo, sans-serif",
                  fontSize: "0.82rem",
                  color: TEXT_MUTED,
                  lineHeight: 1.6,
                  textAlign: "right",
                }}
              >
                {journal.description}
              </p>

              {/* Bottom bar */}
              <div
                className="journal-accent"
                style={{
                  height: "3px",
                  borderRadius: "2px",
                  background: `linear-gradient(to left, ${journal.color}40, ${journal.color})`,
                  marginTop: "4px",
                }}
              />
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
