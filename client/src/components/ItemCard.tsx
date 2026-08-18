/* =============================================
   ItemCard — مكنز القضاء والأنظمة والمحاماة
   تجربة هوية الغلاف: بطاقات عنّابية + ذهب عتيق + خط ثمانية
   ============================================= */
import {
  FileText, ExternalLink, Copy, Star,
  User, BookOpen, Hash, FileType, HardDrive
} from "lucide-react";
import type { Item } from "@/hooks/useItems";
import { getCategoryBadgeClass } from "./FilterBar";
import { toast } from "sonner";

interface ItemCardProps {
  item: Item;
  index: number;
}

const FILE_TYPE_ICONS: Record<string, string> = {
  PDF: "📄",
  MP3: "🎵",
  MP4: "🎬",
  Word: "📝",
  ZIP: "📦",
  Excel: "📊",
};

export default function ItemCard({ item, index }: ItemCardProps) {
  const badgeClass = getCategoryBadgeClass(item.category);

  const copyLink = () => {
    const link = item.link_telegram || item.link_direct || item.link_drive || "";
    if (link) {
      navigator.clipboard.writeText(link);
      toast.success("تم نسخ الرابط");
    } else {
      toast.error("لا يوجد رابط متاح");
    }
  };

  return (
    <div
      className="group relative rounded-xl border transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
      style={{
        fontFamily: "Thmanyah Sans, Cairo, sans-serif",
        background: "linear-gradient(145deg, oklch(0.30 0.075 24), oklch(0.23 0.06 23))",
        borderColor: item.is_featured ? "oklch(0.77 0.14 76)" : "oklch(0.58 0.10 70 / 0.7)",
        boxShadow: item.is_featured ? "0 0 18px oklch(0.75 0.14 76 / 0.22)" : "inset 0 1px oklch(1 0 0 / 0.05), 0 8px 18px oklch(0 0 0 / 0.16)",
      }}
    >
      {/* Featured badge */}
      {item.is_featured && (
        <div
          className="absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center shadow-md"
          style={{ background: "oklch(0.74 0.13 76)" }}
        >
          <Star className="w-3 h-3 fill-current" style={{ color: "oklch(0.17 0.05 22)" }} />
        </div>
      )}

      <div className="p-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2 mb-3">
          {/* Serial number */}
          <span
            className="flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center text-[10px]"
            style={{
              fontFamily: "Thmanyah Sans, Cairo, sans-serif",
              background: "oklch(0.21 0.055 22)",
              border: "1px solid oklch(0.58 0.10 70 / 0.7)",
              color: "oklch(0.78 0.08 76)",
            }}
          >
            {index}
          </span>

          {/* Badges */}
          <div className="flex flex-wrap gap-1 flex-1">
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] border ${badgeClass}`}>
              <Hash className="w-2.5 h-2.5" />
              {item.category.length > 18 ? item.category.slice(0, 18) + "..." : item.category}
            </span>
            {item.material_type && (
              <span
                className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px]"
                style={{
                  background: "oklch(0.36 0.07 25)",
                  color: "oklch(0.85 0.10 76)",
                }}
              >
                {item.material_type}
              </span>
            )}
          </div>

          {/* File type */}
          <span className="flex-shrink-0 text-base" title={item.file_type}>
            {FILE_TYPE_ICONS[item.file_type] || "📄"}
          </span>
        </div>

        {/* Title */}
        <h3
          className="text-sm font-bold mb-2 leading-relaxed line-clamp-2 transition-colors"
          style={{
            fontFamily: "Thmanyah Serif Display, Amiri, serif",
            color: "oklch(0.94 0.03 82)",
          }}
        >
          {item.title}
        </h3>

        {/* Meta info */}
        <div className="space-y-1 mb-3">
          {item.author && (
            <div className="flex items-center gap-1.5 text-xs" style={{ color: "oklch(0.78 0.04 74)" }}>
              <User className="w-3 h-3 flex-shrink-0" />
              <span className="truncate">{item.author}</span>
            </div>
          )}
          {item.investigator && (
            <div className="flex items-center gap-1.5 text-xs" style={{ color: "oklch(0.74 0.04 72)" }}>
              <BookOpen className="w-3 h-3 flex-shrink-0" />
              <span className="truncate">تحقيق: {item.investigator}</span>
            </div>
          )}
          <div className="flex items-center gap-3 text-xs" style={{ color: "oklch(0.72 0.04 70)" }}>
            {item.file_size && (
              <span className="flex items-center gap-1">
                <HardDrive className="w-3 h-3" />
                {item.file_size}
              </span>
            )}
            {item.pages_count && (
              <span className="flex items-center gap-1">
                <FileType className="w-3 h-3" />
                {item.pages_count} صفحة
              </span>
            )}
            {item.source && (
              <span className="flex items-center gap-1 truncate max-w-[120px]">
                <FileText className="w-3 h-3 flex-shrink-0" />
                {item.source.length > 20 ? item.source.slice(0, 20) + "..." : item.source}
              </span>
            )}
          </div>
        </div>

        {/* Divider */}
        <div
          className="mb-3"
          style={{
            height: "1px",
            background: "linear-gradient(90deg, transparent, oklch(0.63 0.11 72 / 0.7), transparent)",
          }}
        />

        {/* Action buttons */}
        <div className="flex items-center gap-1.5">
          {item.link_telegram && (
            <a
              href={item.link_telegram}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all hover:opacity-85 active:scale-95"
              style={{
                background: "linear-gradient(135deg, oklch(0.42 0.08 78), oklch(0.35 0.10 78))",
                color: "oklch(0.97 0.04 78)",
                border: "1px solid oklch(0.55 0.12 78)",
              }}
            >
              <ExternalLink className="w-3.5 h-3.5" />
              فتح في تيليجرام
            </a>
          )}
          {item.link_direct && (
            <a
              href={item.link_direct}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all hover:opacity-85 active:scale-95"
              style={{
                background: "linear-gradient(135deg, oklch(0.42 0.08 78), oklch(0.35 0.10 78))",
                color: "oklch(0.97 0.04 78)",
                border: "1px solid oklch(0.55 0.12 78)",
              }}
            >
              <ExternalLink className="w-3.5 h-3.5" />
              فتح الرابط
            </a>
          )}
          {item.link_drive && !item.link_direct && !item.link_telegram && (
            <a
              href={item.link_drive}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all hover:opacity-85 active:scale-95"
              style={{
                background: "linear-gradient(135deg, oklch(0.42 0.08 78), oklch(0.35 0.10 78))",
                color: "oklch(0.97 0.04 78)",
                border: "1px solid oklch(0.55 0.12 78)",
              }}
            >
              <ExternalLink className="w-3.5 h-3.5" />
              فتح الرابط
            </a>
          )}
          {/* Details button */}
          <button
            onClick={copyLink}
            className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs transition-colors"
            style={{
              background: "oklch(0.93 0.04 310)",
              color: "oklch(0.35 0.14 310)",
              border: "1px solid oklch(0.88 0.04 78)",
            }}
            title="نسخ الرابط"
          >
            <Copy className="w-3 h-3" />
            نسخ
          </button>
        </div>
      </div>
    </div>
  );
}
