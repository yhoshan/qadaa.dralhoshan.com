/* =============================================
   FilterBar — مكنز القضاء والأنظمة والمحاماة
   ألوان مطابقة لـ osool.dralhoshan.com
   خلفية بيج دافئ + أزرار ذهبية بنية
   ============================================= */
import { ArrowUpDown, X } from "lucide-react";
import type { FilterState, SortOption } from "@/hooks/useItems";

interface FilterBarProps {
  filters: FilterState;
  onFiltersChange: (f: Partial<FilterState>) => void;
  categories: string[];
  materialTypes: string[];
  fileTypes: string[];
  sources: string[];
  totalResults: number;
  totalItems: number;
}

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: "default", label: "الافتراضي" },
  { value: "alpha", label: "أبجدي" },
  { value: "category", label: "حسب القسم" },
  { value: "author", label: "حسب المؤلف" },
  { value: "newest", label: "الأحدث" },
  { value: "oldest", label: "الأقدم" },
];

// ألوان الأقسام — مطابقة لـ osool.dralhoshan.com
const CATEGORY_COLORS: Record<string, string> = {
  "الجنايات والحدود": "badge-crimes",
  "القضاء والأنظمة العامة": "badge-judiciary",
  "الأنظمة والتشريعات": "badge-systems",
  "الإثبات والشهادة": "badge-evidence",
  "القضاء الشرعي": "badge-judiciary",
  "الفرائض والمواريث": "badge-inheritance",
  "الأحوال الشخصية": "badge-personal",
  "أبحاث ودراسات قضائية": "badge-research",
  "المحاكم والمرافعات": "badge-courts",
  "الحسبة والمظالم": "badge-hisba",
  "المحاماة والتحكيم": "badge-advocacy",
  "المبادئ والقرارات القضائية": "badge-judiciary",
  "أنظمة العمل": "badge-systems",
  "القضاء الإداري": "badge-systems",
  "الأنظمة التجارية": "badge-systems",
  "وثيقة قضائية": "badge-courts",
};

export function getCategoryBadgeClass(category: string): string {
  return CATEGORY_COLORS[category] || "badge-general";
}

// Shared select style
const selectStyle = {
  background: "oklch(1 0 0)",
  border: "1px solid oklch(0.88 0.04 78)",
  borderRadius: "0.5rem",
  padding: "0.375rem 0.75rem",
  fontSize: "0.75rem",
  color: "oklch(0.18 0.04 50)",
  outline: "none",
  fontFamily: "Cairo, sans-serif",
  width: "100%",
};

export default function FilterBar(props: FilterBarProps) {
  const { filters, onFiltersChange, totalResults, totalItems } = props;

  const hasActiveFilters =
    filters.category !== "all" ||
    filters.material_type !== "all" ||
    filters.file_type !== "all" ||
    filters.source !== "all" ||
    filters.has_download;

  return (
    <div
      className="sticky top-16 z-40 backdrop-blur-xl border-b"
      style={{
        background: "oklch(0.98 0.01 85 / 0.97)",
        borderColor: "oklch(0.88 0.04 78)",
      }}
    >
      <div className="container">
        <div className="flex items-center justify-between py-3 gap-3">
          {/* Results count */}
          <div className="text-sm" style={{ fontFamily: "Cairo, sans-serif", color: "oklch(0.52 0.06 60)" }}>
            <span className="font-bold" style={{ color: "oklch(0.48 0.12 68)" }}>
              {totalResults.toLocaleString("en-US")}
            </span>
            <span className="mx-1">من</span>
            <span>{totalItems.toLocaleString("en-US")}</span>
            <span className="mr-1">مادة</span>
          </div>

          {/* Quick source tabs - desktop */}
          <div className="hidden lg:flex items-center gap-1 overflow-x-auto flex-1 mx-4">
            {["all", ...props.sources.slice(0, 8)].map((src) => (
              <button
                key={src}
                onClick={() => onFiltersChange({ source: src })}
                className="px-3 py-1.5 rounded-lg text-xs whitespace-nowrap transition-all"
                style={{
                  fontFamily: "Cairo, sans-serif",
                  background: filters.source === src ? "rgb(139, 105, 20)" : "transparent",
                  color: filters.source === src ? "white" : "oklch(0.52 0.06 60)",
                  fontWeight: filters.source === src ? "bold" : "normal",
                }}
              >
                {src === "all" ? "جميع المصادر" : src}
              </button>
            ))}
          </div>

          {/* Sort + Filter buttons */}
          <div className="flex items-center gap-2">
            {/* Sort - desktop */}
            <div
              className="hidden sm:flex items-center gap-1.5 rounded-lg px-3 py-1.5"
              style={{
                background: "oklch(0.93 0.03 80)",
                border: "1px solid oklch(0.88 0.04 78)",
              }}
            >
              <ArrowUpDown className="w-3.5 h-3.5" style={{ color: "oklch(0.52 0.06 60)" }} />
              <select
                value={filters.sort}
                onChange={(e) => onFiltersChange({ sort: e.target.value as SortOption })}
                className="bg-transparent text-xs outline-none"
                style={{ fontFamily: "Cairo, sans-serif", color: "oklch(0.38 0.10 65)" }}
              >
                {SORT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>

          </div>
        </div>

        {/* Desktop sidebar filters row */}
        <div className="hidden lg:flex items-center gap-3 pb-3">
          <select
            value={filters.material_type}
            onChange={(e) => onFiltersChange({ material_type: e.target.value })}
            className="rounded-lg px-3 py-1.5 text-xs outline-none"
            style={{
              fontFamily: "Cairo, sans-serif",
              background: "oklch(1 0 0)",
              border: "1px solid oklch(0.88 0.04 78)",
              color: "oklch(0.38 0.10 65)",
            }}
          >
            <option value="all">نوع المادة: الكل</option>
            {props.materialTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>

          <select
            value={filters.file_type}
            onChange={(e) => onFiltersChange({ file_type: e.target.value })}
            className="rounded-lg px-3 py-1.5 text-xs outline-none"
            style={{
              fontFamily: "Cairo, sans-serif",
              background: "oklch(1 0 0)",
              border: "1px solid oklch(0.88 0.04 78)",
              color: "oklch(0.38 0.10 65)",
            }}
          >
            <option value="all">نوع الملف: الكل</option>
            {props.fileTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>

          <select
            value={filters.source}
            onChange={(e) => onFiltersChange({ source: e.target.value })}
            className="rounded-lg px-3 py-1.5 text-xs outline-none"
            style={{
              fontFamily: "Cairo, sans-serif",
              background: "oklch(1 0 0)",
              border: "1px solid oklch(0.88 0.04 78)",
              color: "oklch(0.38 0.10 65)",
              maxWidth: "160px",
            }}
          >
            <option value="all">المصدر: الكل</option>
            {props.sources.slice(0, 20).map((s) => (
              <option key={s} value={s}>{s.length > 30 ? s.slice(0, 30) + "…" : s}</option>
            ))}
          </select>

          <label className="flex items-center gap-2 cursor-pointer">
            <div
              onClick={() => onFiltersChange({ has_download: !filters.has_download })}
              className="w-8 h-4 rounded-full transition-colors relative"
              style={{ background: filters.has_download ? "rgb(139, 105, 20)" : "oklch(0.88 0.04 78)" }}
            >
              <div
                className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all ${
                  filters.has_download ? "right-0.5" : "left-0.5"
                }`}
              />
            </div>
            <span className="text-xs" style={{ fontFamily: "Cairo, sans-serif", color: "oklch(0.52 0.06 60)" }}>
              لها روابط فتح
            </span>
          </label>

          {hasActiveFilters && (
            <button
              onClick={() =>
                onFiltersChange({
                  category: "all",
                  material_type: "all",
                  file_type: "all",
                  source: "all",
                  has_download: false,
                })
              }
              className="flex items-center gap-1 text-xs transition-colors hover:opacity-70"
              style={{ fontFamily: "Cairo, sans-serif", color: "oklch(0.48 0.12 68)" }}
            >
              <X className="w-3 h-3" />
              مسح الفلاتر
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
