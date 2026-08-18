import { useState, useEffect, useMemo } from "react";

export interface Item {
  id: string;
  title: string;
  author: string;
  investigator: string;
  publisher: string;
  year: string;
  link_telegram: string;
  link_drive: string;
  link_direct: string;
  source: string;
  category: string;
  material_type: string;
  file_type: string;
  file_size: string;
  pages_count: string;
  is_featured: boolean;
  download_links_count: number;
}

export interface Stats {
  total_items: number;
  categories: Record<string, number>;
  sources: Record<string, number>;
  file_types: Record<string, number>;
  featured_count: number;
  with_download_links: number;
  qadaa_count?: number;
  nizam_count?: number;
  mohama_count?: number;
}

// تطبيع النص العربي لإلغاء تأثير الهمزات
export function normalizeArabic(text: string): string {
  return text
    .replace(/[أإآا]/g, "ا")
    .replace(/[\u064B-\u065F]/g, "") // إزالة التشكيل
    .replace(/ة/g, "ه")
    .replace(/ى/g, "ي")
    .toLowerCase()
    .trim();
}

export function useItems() {
  const [items, setItems] = useState<Item[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch(`/items.json?v=qadaa17079-clean-20260818`).then((r) => r.json()),
      fetch(`/stats.json?v=qadaa17079-clean-20260818`).then((r) => r.json()),
    ])
      .then(([itemsData, statsData]) => {
        setItems(itemsData);
        setStats(statsData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return { items, stats, loading, error };
}

export type SortOption =
  | "default"
  | "newest"
  | "oldest"
  | "alpha"
  | "category"
  | "author";

export interface FilterState {
  search: string;
  category: string;
  material_type: string;
  file_type: string;
  source: string;
  has_download: boolean;
  sort: SortOption;
}

export function useFilteredItems(items: Item[], filters: FilterState) {
  return useMemo(() => {
    let result = [...items];

    // البحث مع تطبيع الهمزات
    if (filters.search.trim()) {
      const q = normalizeArabic(filters.search);
      result = result.filter((item) => {
        const searchable = normalizeArabic(
          [item.title, item.author, item.investigator, item.category, item.source].join(" ")
        );
        return searchable.includes(q);
      });
    }

    // فلتر القسم
    if (filters.category && filters.category !== "all") {
      result = result.filter((item) => item.category === filters.category);
    }

    // فلتر نوع المادة
    if (filters.material_type && filters.material_type !== "all") {
      result = result.filter((item) => item.material_type === filters.material_type);
    }

    // فلتر نوع الملف
    if (filters.file_type && filters.file_type !== "all") {
      result = result.filter((item) => item.file_type === filters.file_type);
    }

    // فلتر المصدر
    if (filters.source && filters.source !== "all") {
      result = result.filter((item) => item.source.includes(filters.source));
    }

    // فلتر الروابط فقط
    if (filters.has_download) {
      result = result.filter((item) => item.download_links_count > 0);
    }

    // الترتيب
    switch (filters.sort) {
      case "alpha":
        result.sort((a, b) => a.title.localeCompare(b.title, "ar"));
        break;
      case "category":
        result.sort((a, b) => a.category.localeCompare(b.category, "ar"));
        break;
      case "author":
        result.sort((a, b) => (a.author || "ي").localeCompare(b.author || "ي", "ar"));
        break;
      case "newest":
        result.sort((a, b) => (b.year || "").localeCompare(a.year || ""));
        break;
      case "oldest":
        result.sort((a, b) => (a.year || "").localeCompare(b.year || ""));
        break;
      default:
        // المميزة أولاً
        result.sort((a, b) => (b.is_featured ? 1 : 0) - (a.is_featured ? 1 : 0));
    }

    return result;
  }, [items, filters]);
}
