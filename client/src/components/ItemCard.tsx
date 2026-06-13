/* =============================================
   ItemCard — مكنز القضاء والأنظمة والمحاماة
   Dark Judicial Majesty Design
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

const MATERIAL_TYPE_COLORS: Record<string, string> = {
  "متن": "text-[oklch(0.72_0.12_75)] bg-[oklch(0.72_0.12_75/0.1)]",
  "شرح": "text-[oklch(0.65_0.12_195)] bg-[oklch(0.55_0.12_195/0.1)]",
  "حاشية": "text-[oklch(0.65_0.12_280)] bg-[oklch(0.45_0.15_280/0.1)]",
  "بحث": "text-[oklch(0.65_0.10_155)] bg-[oklch(0.45_0.12_155/0.1)]",
  "نظم": "text-[oklch(0.65_0.12_310)] bg-[oklch(0.45_0.14_310/0.1)]",
  "وثيقة قضائية": "text-[oklch(0.65_0.10_240)] bg-[oklch(0.45_0.12_240/0.1)]",
  "مقرر دراسي": "text-[oklch(0.65_0.10_50)] bg-[oklch(0.48_0.10_50/0.1)]",
};

export default function ItemCard({ item, index }: ItemCardProps) {
  const badgeClass = getCategoryBadgeClass(item.category);
  const materialColor = MATERIAL_TYPE_COLORS[item.material_type] || "text-[oklch(0.60_0.05_240)] bg-[oklch(0.25_0.04_240/0.5)]";

  const copyLink = () => {
    const link = item.link_telegram || item.link_direct || item.link_drive || "";
    if (link) {
      navigator.clipboard.writeText(link);
      toast.success("تم نسخ الرابط");
    } else {
      toast.error("لا يوجد رابط متاح");
    }
  };

  const primaryLink = item.link_telegram || item.link_direct || item.link_drive;

  return (
    <div
      className={`group relative rounded-xl border transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg ${
        item.is_featured
          ? "featured-card bg-[oklch(0.17_0.03_240)]"
          : "bg-[oklch(0.16_0.025_240)] border-[oklch(0.22_0.03_240)] hover:border-[oklch(0.30_0.04_240)]"
      }`}
      style={{ fontFamily: "Cairo, sans-serif" }}
    >
      {/* Featured badge */}
      {item.is_featured && (
        <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-[oklch(0.72_0.12_75)] flex items-center justify-center shadow-md">
          <Star className="w-3 h-3 text-[oklch(0.12_0.02_240)] fill-current" />
        </div>
      )}

      <div className="p-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2 mb-3">
          {/* Serial number */}
          <span className="flex-shrink-0 w-7 h-7 rounded-lg bg-[oklch(0.20_0.03_240)] border border-[oklch(0.25_0.03_240)] flex items-center justify-center text-[10px] text-[oklch(0.50_0.01_240)]" style={{ fontFamily: "Tajawal, sans-serif" }}>
            {index}
          </span>

          {/* Badges */}
          <div className="flex flex-wrap gap-1 flex-1">
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] border ${badgeClass}`}>
              <Hash className="w-2.5 h-2.5" />
              {item.category.length > 18 ? item.category.slice(0, 18) + "..." : item.category}
            </span>
            {item.material_type && (
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] ${materialColor}`}>
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
          className="text-sm font-bold text-[oklch(0.92_0.01_80)] mb-2 leading-relaxed line-clamp-2 group-hover:text-[oklch(0.82_0.10_75)] transition-colors"
          style={{ fontFamily: "Amiri, serif" }}
        >
          {item.title}
        </h3>

        {/* Meta info */}
        <div className="space-y-1 mb-3">
          {item.author && (
            <div className="flex items-center gap-1.5 text-xs text-[oklch(0.60_0.01_240)]">
              <User className="w-3 h-3 flex-shrink-0" />
              <span className="truncate">{item.author}</span>
            </div>
          )}
          {item.investigator && (
            <div className="flex items-center gap-1.5 text-xs text-[oklch(0.55_0.01_240)]">
              <BookOpen className="w-3 h-3 flex-shrink-0" />
              <span className="truncate">تحقيق: {item.investigator}</span>
            </div>
          )}
          <div className="flex items-center gap-3 text-xs text-[oklch(0.45_0.01_240)]">
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

        {/* Gold divider */}
        <div className="gold-divider mb-3" />

        {/* Action buttons */}
        <div className="flex items-center gap-1.5">
          {item.link_telegram && (
            <a
              href={item.link_telegram}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg bg-[oklch(0.35_0.12_220/0.15)] border border-[oklch(0.45_0.12_220/0.3)] text-[oklch(0.65_0.10_220)] text-xs hover:bg-[oklch(0.35_0.12_220/0.25)] transition-colors"
            >
              <ExternalLink className="w-3 h-3" />
              تيليجرام
            </a>
          )}
          {item.link_direct && (
            <a
              href={item.link_direct}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg bg-[oklch(0.72_0.12_75/0.1)] border border-[oklch(0.72_0.12_75/0.3)] text-[oklch(0.82_0.10_75)] text-xs hover:bg-[oklch(0.72_0.12_75/0.2)] transition-colors"
            >
              <Download className="w-3 h-3" />
              تحميل
            </a>
          )}
          {item.link_drive && !item.link_direct && (
            <a
              href={item.link_drive}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg bg-[oklch(0.45_0.12_155/0.1)] border border-[oklch(0.45_0.12_155/0.3)] text-[oklch(0.60_0.10_155)] text-xs hover:bg-[oklch(0.45_0.12_155/0.2)] transition-colors"
            >
              <ExternalLink className="w-3 h-3" />
              درايف
            </a>
          )}
          <button
            onClick={copyLink}
            className="w-8 h-8 flex items-center justify-center rounded-lg bg-[oklch(0.20_0.03_240)] border border-[oklch(0.25_0.03_240)] text-[oklch(0.55_0.01_240)] hover:text-[oklch(0.72_0.12_75)] hover:border-[oklch(0.72_0.12_75/0.3)] transition-colors"
            title="نسخ الرابط"
          >
            <Copy className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
