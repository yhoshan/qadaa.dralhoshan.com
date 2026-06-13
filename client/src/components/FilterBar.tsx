/* =============================================
   FilterBar — مكنز القضاء والأنظمة والمحاماة
   Dark Judicial Majesty Design
   ============================================= */
import { Filter, ArrowUpDown, Download, X } from "lucide-react";
import type { FilterState, SortOption } from "@/hooks/useItems";
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerTrigger } from "@/components/ui/drawer";
import { useState } from "react";

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

// ألوان الأقسام
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

function FilterContent({
  filters,
  onFiltersChange,
  categories,
  materialTypes,
  fileTypes,
  sources,
}: Omit<FilterBarProps, "totalResults" | "totalItems">) {
  return (
    <div className="space-y-5" style={{ fontFamily: "Cairo, sans-serif" }}>
      {/* Category */}
      <div>
        <label className="block text-xs text-[oklch(0.60_0.01_240)] mb-2">القسم</label>
        <select
          value={filters.category}
          onChange={(e) => onFiltersChange({ category: e.target.value })}
          className="w-full bg-[oklch(0.18_0.025_240)] border border-[oklch(0.25_0.03_240)] rounded-lg px-3 py-2 text-sm text-[oklch(0.85_0.01_80)] outline-none focus:border-[oklch(0.72_0.12_75/0.5)]"
        >
          <option value="all">جميع الأقسام</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Material Type */}
      <div>
        <label className="block text-xs text-[oklch(0.60_0.01_240)] mb-2">نوع المادة</label>
        <select
          value={filters.material_type}
          onChange={(e) => onFiltersChange({ material_type: e.target.value })}
          className="w-full bg-[oklch(0.18_0.025_240)] border border-[oklch(0.25_0.03_240)] rounded-lg px-3 py-2 text-sm text-[oklch(0.85_0.01_80)] outline-none focus:border-[oklch(0.72_0.12_75/0.5)]"
        >
          <option value="all">جميع الأنواع</option>
          {materialTypes.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      {/* File Type */}
      <div>
        <label className="block text-xs text-[oklch(0.60_0.01_240)] mb-2">نوع الملف</label>
        <div className="flex flex-wrap gap-2">
          {["all", ...fileTypes].map((ft) => (
            <button
              key={ft}
              onClick={() => onFiltersChange({ file_type: ft })}
              className={`px-3 py-1 rounded-full text-xs border transition-all ${
                filters.file_type === ft
                  ? "bg-[oklch(0.72_0.12_75)] text-[oklch(0.12_0.02_240)] border-[oklch(0.72_0.12_75)]"
                  : "bg-transparent text-[oklch(0.65_0.01_240)] border-[oklch(0.25_0.03_240)] hover:border-[oklch(0.72_0.12_75/0.4)]"
              }`}
            >
              {ft === "all" ? "الكل" : ft}
            </button>
          ))}
        </div>
      </div>

      {/* Source */}
      <div>
        <label className="block text-xs text-[oklch(0.60_0.01_240)] mb-2">المصدر</label>
        <select
          value={filters.source}
          onChange={(e) => onFiltersChange({ source: e.target.value })}
          className="w-full bg-[oklch(0.18_0.025_240)] border border-[oklch(0.25_0.03_240)] rounded-lg px-3 py-2 text-sm text-[oklch(0.85_0.01_80)] outline-none focus:border-[oklch(0.72_0.12_75/0.5)]"
        >
          <option value="all">جميع المصادر</option>
          {sources.slice(0, 20).map((s) => (
            <option key={s} value={s}>{s.length > 40 ? s.slice(0, 40) + "..." : s}</option>
          ))}
        </select>
      </div>

      {/* Has Download */}
      <div>
        <label className="flex items-center gap-3 cursor-pointer">
          <div
            onClick={() => onFiltersChange({ has_download: !filters.has_download })}
            className={`w-10 h-5 rounded-full transition-colors relative ${
              filters.has_download ? "bg-[oklch(0.72_0.12_75)]" : "bg-[oklch(0.25_0.03_240)]"
            }`}
          >
            <div
              className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${
                filters.has_download ? "right-0.5" : "left-0.5"
              }`}
            />
          </div>
          <span className="text-sm text-[oklch(0.75_0.01_240)]">
            <Download className="w-3.5 h-3.5 inline ml-1" />
            لها روابط تحميل فقط
          </span>
        </label>
      </div>

      {/* Sort */}
      <div>
        <label className="block text-xs text-[oklch(0.60_0.01_240)] mb-2">الترتيب</label>
        <select
          value={filters.sort}
          onChange={(e) => onFiltersChange({ sort: e.target.value as SortOption })}
          className="w-full bg-[oklch(0.18_0.025_240)] border border-[oklch(0.25_0.03_240)] rounded-lg px-3 py-2 text-sm text-[oklch(0.85_0.01_80)] outline-none focus:border-[oklch(0.72_0.12_75/0.5)]"
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* Reset */}
      <button
        onClick={() =>
          onFiltersChange({
            category: "all",
            material_type: "all",
            file_type: "all",
            source: "all",
            has_download: false,
            sort: "default",
          })
        }
        className="w-full py-2 rounded-lg border border-[oklch(0.25_0.03_240)] text-[oklch(0.60_0.01_240)] text-sm hover:border-[oklch(0.72_0.12_75/0.3)] hover:text-[oklch(0.72_0.12_75)] transition-colors flex items-center justify-center gap-2"
      >
        <X className="w-3.5 h-3.5" />
        إعادة تعيين الفلاتر
      </button>
    </div>
  );
}

export default function FilterBar(props: FilterBarProps) {
  const { filters, onFiltersChange, totalResults, totalItems } = props;
  const [drawerOpen, setDrawerOpen] = useState(false);

  const hasActiveFilters =
    filters.category !== "all" ||
    filters.material_type !== "all" ||
    filters.file_type !== "all" ||
    filters.source !== "all" ||
    filters.has_download;

  return (
    <div className="sticky top-16 z-40 bg-[oklch(0.14_0.025_240/0.97)] backdrop-blur-xl border-b border-[oklch(0.22_0.03_240)]">
      <div className="container">
        <div className="flex items-center justify-between py-3 gap-3">
          {/* Results count */}
          <div className="text-sm text-[oklch(0.60_0.01_240)]" style={{ fontFamily: "Cairo, sans-serif" }}>
            <span className="text-[oklch(0.82_0.10_75)] font-bold">{totalResults.toLocaleString("en-US")}</span>
            <span className="mx-1">من</span>
            <span>{totalItems.toLocaleString("en-US")}</span>
            <span className="mr-1">مادة</span>
          </div>

          {/* Quick category tabs - desktop */}
          <div className="hidden lg:flex items-center gap-1 overflow-x-auto flex-1 mx-4">
            {["all", ...props.categories.slice(0, 7)].map((cat) => (
              <button
                key={cat}
                onClick={() => onFiltersChange({ category: cat })}
                className={`px-3 py-1.5 rounded-lg text-xs whitespace-nowrap transition-all ${
                  filters.category === cat
                    ? "bg-[oklch(0.72_0.12_75)] text-[oklch(0.12_0.02_240)] font-bold"
                    : "text-[oklch(0.60_0.01_240)] hover:text-[oklch(0.85_0.01_80)] hover:bg-[oklch(0.20_0.03_240)]"
                }`}
                style={{ fontFamily: "Cairo, sans-serif" }}
              >
                {cat === "all" ? "الكل" : cat}
              </button>
            ))}
          </div>

          {/* Sort + Filter buttons */}
          <div className="flex items-center gap-2">
            {/* Sort - desktop */}
            <div className="hidden sm:flex items-center gap-1.5 bg-[oklch(0.18_0.025_240)] border border-[oklch(0.25_0.03_240)] rounded-lg px-3 py-1.5">
              <ArrowUpDown className="w-3.5 h-3.5 text-[oklch(0.55_0.01_240)]" />
              <select
                value={filters.sort}
                onChange={(e) => onFiltersChange({ sort: e.target.value as SortOption })}
                className="bg-transparent text-xs text-[oklch(0.75_0.01_240)] outline-none"
                style={{ fontFamily: "Cairo, sans-serif" }}
              >
                {SORT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>

            {/* Mobile filter drawer */}
            <Drawer open={drawerOpen} onOpenChange={setDrawerOpen}>
              <DrawerTrigger asChild>
                <button
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs transition-all ${
                    hasActiveFilters
                      ? "bg-[oklch(0.72_0.12_75/0.15)] border-[oklch(0.72_0.12_75/0.5)] text-[oklch(0.82_0.10_75)]"
                      : "bg-[oklch(0.18_0.025_240)] border-[oklch(0.25_0.03_240)] text-[oklch(0.65_0.01_240)]"
                  }`}
                  style={{ fontFamily: "Cairo, sans-serif" }}
                >
                  <Filter className="w-3.5 h-3.5" />
                  <span>فلترة</span>
                  {hasActiveFilters && (
                    <span className="w-4 h-4 rounded-full bg-[oklch(0.72_0.12_75)] text-[oklch(0.12_0.02_240)] text-[10px] flex items-center justify-center font-bold">
                      !
                    </span>
                  )}
                </button>
              </DrawerTrigger>
              <DrawerContent className="bg-[oklch(0.14_0.025_240)] border-[oklch(0.22_0.03_240)]">
                <DrawerHeader>
                  <DrawerTitle className="text-[oklch(0.92_0.01_80)]" style={{ fontFamily: "Amiri, serif" }}>
                    تصفية النتائج
                  </DrawerTitle>
                </DrawerHeader>
                <div className="px-4 pb-6 overflow-y-auto max-h-[70vh]">
                  <FilterContent {...props} />
                </div>
              </DrawerContent>
            </Drawer>
          </div>
        </div>

        {/* Desktop sidebar filters row */}
        <div className="hidden lg:flex items-center gap-3 pb-3">
          <select
            value={filters.material_type}
            onChange={(e) => onFiltersChange({ material_type: e.target.value })}
            className="bg-[oklch(0.18_0.025_240)] border border-[oklch(0.25_0.03_240)] rounded-lg px-3 py-1.5 text-xs text-[oklch(0.75_0.01_240)] outline-none"
            style={{ fontFamily: "Cairo, sans-serif" }}
          >
            <option value="all">نوع المادة: الكل</option>
            {props.materialTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>

          <select
            value={filters.file_type}
            onChange={(e) => onFiltersChange({ file_type: e.target.value })}
            className="bg-[oklch(0.18_0.025_240)] border border-[oklch(0.25_0.03_240)] rounded-lg px-3 py-1.5 text-xs text-[oklch(0.75_0.01_240)] outline-none"
            style={{ fontFamily: "Cairo, sans-serif" }}
          >
            <option value="all">نوع الملف: الكل</option>
            {props.fileTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>

          <label className="flex items-center gap-2 cursor-pointer">
            <div
              onClick={() => onFiltersChange({ has_download: !filters.has_download })}
              className={`w-8 h-4 rounded-full transition-colors relative ${
                filters.has_download ? "bg-[oklch(0.72_0.12_75)]" : "bg-[oklch(0.25_0.03_240)]"
              }`}
            >
              <div
                className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all ${
                  filters.has_download ? "right-0.5" : "left-0.5"
                }`}
              />
            </div>
            <span className="text-xs text-[oklch(0.60_0.01_240)]" style={{ fontFamily: "Cairo, sans-serif" }}>
              لها روابط تحميل
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
              className="flex items-center gap-1 text-xs text-[oklch(0.55_0.01_240)] hover:text-[oklch(0.72_0.12_75)] transition-colors"
              style={{ fontFamily: "Cairo, sans-serif" }}
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
