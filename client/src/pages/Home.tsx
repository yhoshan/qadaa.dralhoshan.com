/* =============================================
   Home Page — مكنز القضاء والأنظمة والمحاماة
   ألوان مطابقة لـ osool.dralhoshan.com
   خلفية بيج دافئ + ذهبي بني + بطاقات بيضاء
   ============================================= */
import { useState, useMemo, useCallback, useRef } from "react";
import { useItems, useFilteredItems, type FilterState } from "@/hooks/useItems";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import FilterBar from "@/components/FilterBar";
import ItemCard from "@/components/ItemCard";
import Footer from "@/components/Footer";
import { Loader2, FileDown, AlertCircle, ChevronRight, ChevronLeft } from "lucide-react";
import { toast } from "sonner";

const PAGE_SIZE = 24;

const DEFAULT_FILTERS: FilterState = {
  search: "",
  category: "all",
  material_type: "all",
  file_type: "all",
  source: "all",
  has_download: false,
  sort: "default",
};

const WARM_BG = "oklch(0.98 0.01 85)";
const CARD_BG = "oklch(0.93 0.03 80)";
const BORDER_COLOR = "oklch(0.88 0.04 78)";
const TEXT_MUTED = "oklch(0.52 0.06 60)";
const GOLD = "rgb(139, 105, 20)";
const TEXT_DARK = "oklch(0.18 0.04 50)";

export default function Home() {
  const { items, stats, loading, error } = useItems();
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [page, setPage] = useState(1);
  const resultsRef = useRef<HTMLDivElement>(null);

  const filteredItems = useFilteredItems(items, filters);

  const totalPages = Math.ceil(filteredItems.length / PAGE_SIZE);
  const currentItems = filteredItems.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  // Unique filter options
  const categories = useMemo(
    () => Array.from(new Set(items.map((i) => i.category))).filter(Boolean).sort((a, b) => a.localeCompare(b, "ar")),
    [items]
  );
  const materialTypes = useMemo(
    () => Array.from(new Set(items.map((i) => i.material_type))).filter(Boolean),
    [items]
  );
  const fileTypes = useMemo(
    () => Array.from(new Set(items.map((i) => i.file_type))).filter(Boolean),
    [items]
  );
  const sources = useMemo(
    () => Array.from(new Set(items.map((i) => i.source))).filter(Boolean),
    [items]
  );

  const handleFiltersChange = useCallback((partial: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...partial }));
    setPage(1);
  }, []);

  const handleSearchSubmit = useCallback(() => {
    setPage(1);
    resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  // Export to CSV (Excel-compatible)
  const exportToExcel = () => {
    const headers = ["#", "العنوان", "المؤلف", "المحقق", "القسم", "نوع المادة", "نوع الملف", "الحجم", "الصفحات", "المصدر", "رابط تيليجرام", "رابط مباشر"];
    const rows = filteredItems.map((item, i) => [
      i + 1,
      item.title,
      item.author,
      item.investigator,
      item.category,
      item.material_type,
      item.file_type,
      item.file_size,
      item.pages_count,
      item.source,
      item.link_telegram,
      item.link_direct,
    ]);

    const csvContent = [headers, ...rows]
      .map((row) => row.map((cell) => `"${String(cell || "").replace(/"/g, '""')}"`).join(","))
      .join("\n");

    const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "مكنز-القضاء-والأنظمة.csv";
    a.click();
    URL.revokeObjectURL(url);
    toast.success(`تم تصدير ${filteredItems.length.toLocaleString("en-US")} مادة`);
  };

  // Copy current filter URL
  const copyFilterUrl = () => {
    const params = new URLSearchParams();
    if (filters.search) params.set("q", filters.search);
    if (filters.category !== "all") params.set("cat", filters.category);
    if (filters.material_type !== "all") params.set("type", filters.material_type);
    if (filters.file_type !== "all") params.set("file", filters.file_type);
    if (filters.has_download) params.set("dl", "1");
    const url = `${window.location.origin}?${params.toString()}`;
    navigator.clipboard.writeText(url);
    toast.success("تم نسخ رابط الفلتر الحالي");
  };

  // Pagination component
  const Pagination = () => {
    if (totalPages <= 1) return null;
    const pageNums: number[] = [];
    const maxVisible = 5;
    let start = Math.max(1, page - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    if (end - start < maxVisible - 1) start = Math.max(1, end - maxVisible + 1);
    for (let i = start; i <= end; i++) pageNums.push(i);

    const btnBase: React.CSSProperties = {
      background: CARD_BG,
      border: `1px solid ${BORDER_COLOR}`,
      color: TEXT_MUTED,
      borderRadius: "0.5rem",
      width: "2.25rem",
      height: "2.25rem",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: "0.875rem",
      cursor: "pointer",
      transition: "opacity 0.15s",
    };
    const btnActive: React.CSSProperties = {
      ...btnBase,
      background: GOLD,
      border: `1px solid ${GOLD}`,
      color: "white",
      fontWeight: "bold",
    };

    return (
      <div className="flex items-center justify-center gap-1 mt-8" style={{ fontFamily: "Tajawal, sans-serif" }}>
        <button
          onClick={() => handlePageChange(page - 1)}
          disabled={page === 1}
          style={{ ...btnBase, opacity: page === 1 ? 0.3 : 1 }}
        >
          <ChevronRight className="w-4 h-4" />
        </button>

        {start > 1 && (
          <>
            <button onClick={() => handlePageChange(1)} style={btnBase}>1</button>
            {start > 2 && <span style={{ color: TEXT_MUTED }}>...</span>}
          </>
        )}

        {pageNums.map((p) => (
          <button
            key={p}
            onClick={() => handlePageChange(p)}
            style={p === page ? btnActive : btnBase}
          >
            {p}
          </button>
        ))}

        {end < totalPages && (
          <>
            {end < totalPages - 1 && <span style={{ color: TEXT_MUTED }}>...</span>}
            <button onClick={() => handlePageChange(totalPages)} style={btnBase}>{totalPages}</button>
          </>
        )}

        <button
          onClick={() => handlePageChange(page + 1)}
          disabled={page === totalPages}
          style={{ ...btnBase, opacity: page === totalPages ? 0.3 : 1 }}
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
      </div>
    );
  };

  return (
    <div className="min-h-screen" style={{ background: WARM_BG }}>
      <Navbar />

      {/* Hero */}
      <HeroSection
        stats={stats}
        searchValue={filters.search}
        onSearchChange={(v) => handleFiltersChange({ search: v })}
        onSearchSubmit={handleSearchSubmit}
      />

      {/* Filter Bar */}
      {!loading && (
        <FilterBar
          filters={filters}
          onFiltersChange={handleFiltersChange}
          categories={categories}
          materialTypes={materialTypes}
          fileTypes={fileTypes}
          sources={sources}
          totalResults={filteredItems.length}
          totalItems={items.length}
        />
      )}

      {/* Results Section */}
      <main ref={resultsRef} className="container py-8">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <Loader2 className="w-10 h-10 animate-spin" style={{ color: GOLD }} />
            <p style={{ fontFamily: "Cairo, sans-serif", color: TEXT_MUTED }}>
              جارٍ تحميل المكنز...
            </p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <AlertCircle className="w-10 h-10" style={{ color: "oklch(0.55 0.22 25)" }} />
            <p style={{ fontFamily: "Cairo, sans-serif", color: TEXT_MUTED }}>
              حدث خطأ في تحميل البيانات
            </p>
          </div>
        ) : (
          <>
            {/* Toolbar */}
            <div className="flex items-center justify-between mb-6 gap-3 flex-wrap">
              <div className="flex items-center gap-2">
                <h2
                  className="text-lg font-bold"
                  style={{ fontFamily: "Amiri, serif", color: TEXT_DARK }}
                >
                  {filters.category !== "all" ? filters.category : "جميع المواد"}
                </h2>
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{
                    fontFamily: "Tajawal, sans-serif",
                    background: CARD_BG,
                    border: `1px solid ${BORDER_COLOR}`,
                    color: TEXT_MUTED,
                  }}
                >
                  {filteredItems.length.toLocaleString("en-US")} مادة
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={copyFilterUrl}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all hover:opacity-80"
                  style={{
                    fontFamily: "Cairo, sans-serif",
                    background: CARD_BG,
                    border: `1px solid ${BORDER_COLOR}`,
                    color: TEXT_MUTED,
                  }}
                >
                  <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                  </svg>
                  نسخ رابط الفلتر
                </button>
                <button
                  onClick={exportToExcel}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all hover:opacity-80"
                  style={{
                    fontFamily: "Cairo, sans-serif",
                    background: GOLD,
                    color: "white",
                  }}
                >
                  <FileDown className="w-3.5 h-3.5" />
                  تصدير Excel
                </button>
              </div>
            </div>

            {/* Cards Grid */}
            {currentItems.length === 0 ? (
              <div className="text-center py-20">
                <p className="text-lg mb-2" style={{ fontFamily: "Amiri, serif", color: TEXT_MUTED }}>
                  لم يُعثر على نتائج
                </p>
                <p className="text-sm" style={{ fontFamily: "Cairo, sans-serif", color: "oklch(0.65 0.03 60)" }}>
                  جرّب البحث بكلمات مختلفة أو تغيير الفلاتر
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {currentItems.map((item, idx) => (
                  <div
                    key={item.id}
                    className="animate-fade-in-up"
                    style={{ animationDelay: `${Math.min(idx * 30, 300)}ms` }}
                  >
                    <ItemCard
                      item={item}
                      index={(page - 1) * PAGE_SIZE + idx + 1}
                    />
                  </div>
                ))}
              </div>
            )}

            {/* Pagination */}
            <Pagination />

            {/* Page info */}
            {totalPages > 1 && (
              <p
                className="text-center text-xs mt-4"
                style={{ fontFamily: "Tajawal, sans-serif", color: TEXT_MUTED }}
              >
                صفحة {page} من {totalPages.toLocaleString("en-US")}
                {" — "}
                عرض {((page - 1) * PAGE_SIZE + 1).toLocaleString("en-US")} إلى{" "}
                {Math.min(page * PAGE_SIZE, filteredItems.length).toLocaleString("en-US")}
              </p>
            )}
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}
