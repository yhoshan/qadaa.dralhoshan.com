/* =============================================
   FilterBar — مكنز القضاء والأنظمة والمحاماة
   ألوان مطابقة لـ osool.dralhoshan.com
   خلفية بيج دافئ + أزرار ذهبية بنية
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
        <label className="block text-xs mb-2" style={{ color: "oklch(0.52 0.06 60)" }}>القسم</label>
        <select
          value={filters.category}
          onChange={(e) => onFiltersChange({ category: e.target.value })}
          style={selectStyle}
        >
          <option value="all">جميع الأقسام</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Material Type */}
      <div>
        <label className="block text-xs mb-2" style={{ color: "oklch(0.52 0.06 60)" }}>نوع المادة</label>
        <select
          value={filters.material_type}
          onChange={(e) => onFiltersChange({ material_type: e.target.value })}
          style={selectStyle}
        >
          <option value="all">جميع الأنواع</option>
          {materialTypes.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      {/* File Type */}
      <div>
        <label className="block text-xs mb-2" style={{ color: "oklch(0.52 0.06 60)" }}>نوع الملف</label>
        <div className="flex flex-wrap gap-2">
          {["all", ...fileTypes].map((ft) => (
            <button
              key={ft}
              onClick={() => onFiltersChange({ file_type: ft })}
              className="px-3 py-1 rounded-full text-xs border transition-all"
              style={{
                background: filters.file_type === ft ? "rgb(139, 105, 20)" : "oklch(0.93 0.03 80)",
                color: filters.file_type === ft ? "white" : "oklch(0.38 0.10 65)",
                borderColor: filters.file_type === ft ? "rgb(139, 105, 20)" : "oklch(0.88 0.04 78)",
              }}
            >
              {ft === "all" ? "الكل" : ft}
            </button>
          ))}
        </div>
      </div>

      {/* Source */}
      <div>
        <label className="block text-xs mb-2" style={{ color: "oklch(0.52 0.06 60)" }}>المصدر</label>
        <select
          value={filters.source}
          onChange={(e) => onFiltersChange({ source: e.target.value })}
          style={selectStyle}
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
            className="w-10 h-5 rounded-full transition-colors relative"
            style={{ background: filters.has_download ? "rgb(139, 105, 20)" : "oklch(0.88 0.04 78)" }}
          >
            <div
              className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${
                filters.has_download ? "right-0.5" : "left-0.5"
              }`}
            />
          </div>
          <span className="text-sm" style={{ color: "oklch(0.38 0.10 65)" }}>
            <Download className="w-3.5 h-3.5 inline ml-1" />
            لها روابط تحميل فقط
          </span>
        </label>
      </div>

      {/* Sort */}
      <div>
        <label className="block text-xs mb-2" style={{ color: "oklch(0.52 0.06 60)" }}>الترتيب</label>
        <select
          value={filters.sort}
          onChange={(e) => onFiltersChange({ sort: e.target.value as SortOption })}
          style={selectStyle}
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
        className="w-full py-2 rounded-lg text-sm flex items-center justify-center gap-2 transition-colors hover:opacity-80"
        style={{
          border: "1px solid oklch(0.88 0.04 78)",
          color: "oklch(0.52 0.06 60)",
          background: "oklch(0.93 0.03 80)",
        }}
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
            {["all", ...props.sources.slice(0, 7)].map((src) => (
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

            {/* Mobile filter drawer */}
            <Drawer open={drawerOpen} onOpenChange={setDrawerOpen}>
              <DrawerTrigger asChild>
                <button
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs transition-all"
                  style={{
                    fontFamily: "Cairo, sans-serif",
                    background: hasActiveFilters ? "oklch(0.93 0.03 80)" : "oklch(0.93 0.03 80)",
                    borderColor: hasActiveFilters ? "rgb(139, 105, 20)" : "oklch(0.88 0.04 78)",
                    color: hasActiveFilters ? "rgb(139, 105, 20)" : "oklch(0.52 0.06 60)",
                  }}
                >
                  <Filter className="w-3.5 h-3.5" />
                  <span>فلاتر إضافية</span>
                  {hasActiveFilters && (
                    <span
                      className="w-4 h-4 rounded-full text-[10px] flex items-center justify-center font-bold"
                      style={{ background: "rgb(139, 105, 20)", color: "white" }}
                    >
                      !
                    </span>
                  )}
                </button>
              </DrawerTrigger>
              <DrawerContent
                style={{
                  background: "oklch(0.98 0.01 85)",
                  borderColor: "oklch(0.88 0.04 78)",
                }}
              >
                <DrawerHeader>
                  <DrawerTitle style={{ fontFamily: "Amiri, serif", color: "oklch(0.18 0.04 50)" }}>
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
