/* =============================================
   ItemCard — مكنز القضاء والأنظمة والمحاماة
   ألوان مطابقة لـ osool.dralhoshan.com
   بطاقات بيضاء + حدود بيج + أزرار ذهبية/بنية
   ============================================= */
import {
  FileText, Download, ExternalLink, Copy, Star,
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
        fontFamily: "Cairo, sans-serif",
        background: item.is_featured ? "oklch(1 0 0)" : "oklch(1 0 0)",
        borderColor: item.is_featured ? "rgb(139, 105, 20)" : "oklch(0.88 0.04 78)",
        boxShadow: item.is_featured ? "0 0 10px oklch(0.48 0.12 68 / 0.12)" : undefined,
      }}
    >
      {/* Featured badge */}
      {item.is_featured && (
        <div
          className="absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center shadow-md"
          style={{ background: "rgb(139, 105, 20)" }}
        >
          <Star className="w-3 h-3 fill-current" style={{ color: "white" }} />
        </div>
      )}

      <div className="p-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2 mb-3">
          {/* Serial number */}
          <span
            className="flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center text-[10px]"
            style={{
              fontFamily: "Tajawal, sans-serif",
              background: "oklch(0.93 0.03 80)",
              border: "1px solid oklch(0.88 0.04 78)",
              color: "oklch(0.52 0.06 60)",
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
                  background: "oklch(0.93 0.03 80)",
                  color: "oklch(0.38 0.10 65)",
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
            fontFamily: "Amiri, serif",
            color: "oklch(0.18 0.04 50)",
          }}
        >
          {item.title}
        </h3>

        {/* Meta info */}
        <div className="space-y-1 mb-3">
          {item.author && (
            <div className="flex items-center gap-1.5 text-xs" style={{ color: "oklch(0.52 0.06 60)" }}>
              <User className="w-3 h-3 flex-shrink-0" />
              <span className="truncate">{item.author}</span>
            </div>
          )}
          {item.investigator && (
            <div className="flex items-center gap-1.5 text-xs" style={{ color: "oklch(0.60 0.04 60)" }}>
              <BookOpen className="w-3 h-3 flex-shrink-0" />
              <span className="truncate">تحقيق: {item.investigator}</span>
            </div>
          )}
          <div className="flex items-center gap-3 text-xs" style={{ color: "oklch(0.65 0.03 60)" }}>
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
            background: "linear-gradient(90deg, transparent, oklch(0.88 0.04 78), transparent)",
          }}
        />

        {/* Action buttons */}
        <div className="flex items-center gap-1.5">
          {item.link_telegram && (
            <a
              href={item.link_telegram}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs transition-colors hover:opacity-90"
              style={{
                background: "oklch(0.45 0.14 310)",
                color: "white",
              }}
            >
              <Download className="w-3 h-3" />
              تحميل
            </a>
          )}
          {item.link_direct && (
            <a
              href={item.link_direct}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs transition-colors hover:opacity-90"
              style={{
                background: "rgb(139, 105, 20)",
                color: "white",
              }}
            >
              <Download className="w-3 h-3" />
              تحميل
            </a>
          )}
          {item.link_drive && !item.link_direct && !item.link_telegram && (
            <a
              href={item.link_drive}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs transition-colors hover:opacity-90"
              style={{
                background: "oklch(0.40 0.12 155)",
                color: "white",
              }}
            >
              <ExternalLink className="w-3 h-3" />
              درايف
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
