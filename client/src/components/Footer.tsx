/* =============================================
   Footer — مكنز القضاء والأنظمة والمحاماة
   ألوان مطابقة لـ osool.dralhoshan.com
   خلفية بيج دافئ + ذهبي بني
   ============================================= */
import { Mail, Copy, ExternalLink } from "lucide-react";
import { toast } from "sonner";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

const SHARE_URL = typeof window !== "undefined" ? window.location.href : "https://qadaa.dralhoshan.com";
const SHARE_TEXT = "مكنز القضاء والأنظمة والمحاماة — فهرس علمي شامل يضم أكثر من 11,000 مادة";

const FOOTER_BG = "oklch(0.95 0.02 80)";
const BORDER_COLOR = "oklch(0.88 0.04 78)";
const TEXT_MUTED = "oklch(0.52 0.06 60)";
const TEXT_LIGHT = "oklch(0.65 0.03 60)";
const GOLD = "rgb(139, 105, 20)";
const TEXT_DARK = "oklch(0.18 0.04 50)";

// مصادر المواد المعتمدة في المكنز — تحفظ الإحالة إلى المنصة أو القناة الأصلية.
const MAKANEZ_SOURCES = [
  { name: "أرشيف الإنترنت", href: "https://archive.org/" },
  { name: "القانون الدولي العام", href: "https://t.me/ibrazx40" },
  { name: "المكتبة الشاملة", href: "https://t.me/shamela_epub" },
  { name: "المكتبة العلمية", href: "https://t.me/ilmiya_pdf" },
  { name: "المكتبة القانونية الكبرى", href: "https://t.me/great_law" },
  { name: "المكتبة القانونية", href: "https://t.me/iirmll" },
  { name: "المكتبة الوقفية", href: "https://t.me/waqfeya_pdf" },
  { name: "تسهيل الأنظمة", href: "https://t.me/muath_alyahya" },
  { name: "جامعة الرسائل العلمية", href: "https://t.me/Arsail2020" },
  { name: "قسم الأنظمة — جامعة نجران", href: "https://t.me/c/1876374106/23056" },
  { name: "قناة الرسائل العلمية والبحوث المحكمة", href: "https://t.me/c/1453973283/5023" },
  { name: "قناة المجلات والصحف القانونية", href: "https://t.me/LegalMagazinesandNewspapers" },
  { name: "مكتبة الإسكندرية", href: "https://t.me/c/1592768820/107" },
  { name: "مكتبة الباحث العلمي", href: "https://t.me/bahith_pdf" },
  { name: "منصة نظامي للأنظمة السعودية", href: "https://nezams.com/" },
  { name: "موقع بحوث ومجلاته الأكاديمية", href: "https://www.buhooth.link/" },
  { name: "موقع د. عبدالعزيز الدغيثر — شبكة الألوكة", href: "https://www.alukah.net/web/doghaither/" },
];

export default function Footer() {
  const copyLink = () => {
    navigator.clipboard.writeText(SHARE_URL);
    toast.success("تم نسخ الرابط");
  };

  const shareLinks = [
    {
      label: "نسخ الرابط",
      icon: Copy,
      color: "oklch(0.55 0.06 60)",
      action: copyLink,
    },
    {
      label: "واتساب",
      icon: () => (
        <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
        </svg>
      ),
      color: "#25D366",
      href: `https://wa.me/?text=${encodeURIComponent(SHARE_TEXT + "\n" + SHARE_URL)}`,
    },
    {
      label: "تيليجرام",
      icon: () => (
        <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
          <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
        </svg>
      ),
      color: "#0088cc",
      href: `https://t.me/share/url?url=${encodeURIComponent(SHARE_URL)}&text=${encodeURIComponent(SHARE_TEXT)}`,
    },
    {
      label: "تويتر",
      icon: () => (
        <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
        </svg>
      ),
      color: "#000000",
      href: `https://twitter.com/intent/tweet?text=${encodeURIComponent(SHARE_TEXT)}&url=${encodeURIComponent(SHARE_URL)}`,
    },
    {
      label: "فيسبوك",
      icon: () => (
        <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
        </svg>
      ),
      color: "#1877F2",
      href: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(SHARE_URL)}`,
    },
  ];

  return (
    <footer style={{ background: FOOTER_BG, borderTop: `1px solid ${BORDER_COLOR}` }}>
      {/* Share Strip */}
      <div className="py-6" style={{ borderBottom: `1px solid ${BORDER_COLOR}` }}>
        <div className="container">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p
              className="text-sm text-center sm:text-right"
              style={{ fontFamily: "Cairo, sans-serif", color: TEXT_MUTED }}
            >
              ساهم في نشر المكنز
              <span className="mr-1 font-bold" style={{ color: GOLD }}>(الدال على الخير كفاعله)</span>
            </p>
            <div className="flex items-center gap-2">
              {shareLinks.map((link) => {
                const Icon = link.icon;
                if (link.action) {
                  return (
                    <button
                      key={link.label}
                      onClick={link.action}
                      title={link.label}
                      className="w-9 h-9 rounded-full text-white flex items-center justify-center hover:opacity-80 transition-opacity"
                      style={{ background: link.color }}
                    >
                      <Icon />
                    </button>
                  );
                }
                return (
                  <a
                    key={link.label}
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={link.label}
                    className="w-9 h-9 rounded-full text-white flex items-center justify-center hover:opacity-80 transition-opacity"
                    style={{ background: link.color }}
                  >
                    <Icon />
                  </a>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer */}
      <div className="py-8">
        <div className="container">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            {/* Column 1: About */}
            <div>
              <h3
                className="font-bold mb-4 text-sm"
                style={{ fontFamily: "Amiri, serif", color: GOLD }}
              >
                مكنز القضاء والأنظمة والمحاماة
              </h3>
              <p className="text-xs leading-relaxed mb-3" style={{ fontFamily: "Cairo, sans-serif", color: TEXT_MUTED }}>
                فهرس علمي شامل يجمع مصادر فقه القضاء والأنظمة والمحاماة الشرعية والقانونية.
                تم تصنيف هذا الفهرس آلياً وتصحيحه يدوياً بناءً على أسماء الملفات والأوصاف المرفقة بها.
              </p>
              <p className="text-xs" style={{ fontFamily: "Cairo, sans-serif", color: TEXT_LIGHT }}>
                إذا لم تجد كتاباً في قسمه المتوقع، يرجى استخدام شريط البحث العام.
              </p>
            </div>

            {/* Column 2: Links */}
            <div>
              <h3
                className="font-bold mb-4 text-sm"
                style={{ fontFamily: "Amiri, serif", color: GOLD }}
              >
                روابط سريعة
              </h3>
              <div className="space-y-2">
                <a
                  href="https://nsooos.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-xs transition-colors hover:opacity-70"
                  style={{ fontFamily: "Cairo, sans-serif", color: TEXT_MUTED }}
                >
                  <ExternalLink className="w-3 h-3" />
                  منصة نصوص تراثية للباحثين
                </a>
                <a
                  href="https://dralhoshan.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-xs transition-colors hover:opacity-70"
                  style={{ fontFamily: "Cairo, sans-serif", color: TEXT_MUTED }}
                >
                  <ExternalLink className="w-3 h-3" />
                  منصة المكانز العلمية
                </a>
                <a
                  href="mailto:yhoshan@gmail.com"
                  className="flex items-center gap-2 text-xs transition-colors hover:opacity-70"
                  style={{ fontFamily: "Cairo, sans-serif", color: TEXT_MUTED }}
                >
                  <Mail className="w-3 h-3" />
                  yhoshan@gmail.com
                </a>
              </div>
            </div>

            {/* Column 3: Report */}
            <div>
              <h3
                className="font-bold mb-4 text-sm"
                style={{ fontFamily: "Amiri, serif", color: GOLD }}
              >
                الإبلاغ عن روابط معطلة
              </h3>
              <p className="text-xs leading-relaxed mb-3" style={{ fontFamily: "Cairo, sans-serif", color: TEXT_MUTED }}>
                أخي الباحث، إذا واجهتك مشكلة في تحميل أي كتاب أو مادة، يرجى كتابة اسم المادة أو الرابط المعطل وسنقوم بمراجعتها وتحديثها فوراً.
              </p>
              <a
                href={`mailto:yhoshan@gmail.com?subject=رابط معطل في مكنز القضاء&body=اسم المادة أو الرابط المعطل:%0A%0A`}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs transition-all hover:opacity-80"
                style={{
                  fontFamily: "Cairo, sans-serif",
                  background: "oklch(0.93 0.04 80)",
                  border: `1px solid ${BORDER_COLOR}`,
                  color: GOLD,
                }}
              >
                <Mail className="w-3.5 h-3.5" />
                إبلاغ عن رابط معطل
              </a>
            </div>
          </div>

          {/* Divider */}
          <div
            className="mb-6"
            style={{
              height: "1px",
              background: `linear-gradient(90deg, transparent, ${GOLD}, transparent)`,
            }}
          />

          {/* Legal notes */}
          <div className="space-y-2 mb-6">
            <p className="text-xs text-center" style={{ fontFamily: "Cairo, sans-serif", color: TEXT_LIGHT }}>
              حقوق المواد محفوظة لمؤلفيها وناشريها.
              في حال عدم رغبتكم بنشر ما يخصكم، آمل المراسلة على:
              <a href="mailto:yhoshan@gmail.com" className="mr-1 hover:opacity-70 transition-opacity" style={{ color: GOLD }}>yhoshan@gmail.com</a>
            </p>
            <p className="text-xs text-center" style={{ fontFamily: "Cairo, sans-serif", color: TEXT_LIGHT }}>
              هل تبحث في السلاسل التراثية الأخرى؟ انتقل لمنصة نصوص تراثية للباحثين:
              <a href="https://nsooos.com" target="_blank" rel="noopener noreferrer" className="mr-1 hover:opacity-70 transition-opacity" style={{ color: GOLD }}>nsooos.com</a>
            </p>
          </div>

          {/* Sources list — يحفظ الإحالة إلى كل منصة أو قناة استُخدمت منها مواد */}
          <div className="mb-6 max-w-3xl mx-auto">
            <Accordion type="single" collapsible dir="rtl">
              <AccordionItem
                value="makanez-sources"
                className="rounded-xl overflow-hidden"
                style={{ border: `1px solid ${BORDER_COLOR}`, background: "oklch(0.97 0.01 82)" }}
              >
                <AccordionTrigger
                  className="px-4 py-3 hover:no-underline items-center"
                  style={{ fontFamily: "Cairo, sans-serif", color: GOLD }}
                >
                  <span className="flex items-center gap-2 text-sm font-semibold">
                    <ExternalLink className="w-4 h-4" />
                    مصادر المكنز
                    <span className="text-xs font-normal" style={{ color: TEXT_MUTED }}>
                      ({MAKANEZ_SOURCES.length} مصدراً)
                    </span>
                  </span>
                </AccordionTrigger>
                <AccordionContent className="px-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 pt-1" dir="rtl">
                    {MAKANEZ_SOURCES.map((source) => (
                      <a
                        key={source.href}
                        href={source.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-xs transition-opacity hover:opacity-70"
                        style={{ fontFamily: "Cairo, sans-serif", color: TEXT_MUTED }}
                      >
                        <ExternalLink className="w-3 h-3 shrink-0" style={{ color: GOLD }} />
                        <span>{source.name}</span>
                      </a>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>

          {/* Bottom bar: Copyright (right) | Logo (center) | Signature (left) */}
          <div
            className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4"
            style={{ borderTop: `1px solid ${BORDER_COLOR}` }}
          >
            {/* Copyright — right side (RTL: first child) */}
            <p
              className="text-xs text-center"
              style={{ fontFamily: "Tajawal, sans-serif", color: TEXT_LIGHT }}
            >
              جميع الحقوق محفوظة © 2026
              <br />
              مكنز القضاء والأنظمة والمحاماة — د. يوسف بن حمود الحوشان
            </p>

            {/* Makanez Logo — center */}
            <a
              href="https://almakanaz.dralhoshan.com/"
              target="_blank"
              rel="noopener noreferrer"
              title="منصة المكانز العلمية"
              className="opacity-80 hover:opacity-100 hover:scale-105 transition-all"
            >
              <img
                src="https://zadwarod.dralhoshan.com/manus-storage/makanez-icon_85f25650.png"
                alt="منصة المكانز"
                className="h-11 sm:h-9 w-auto object-contain"
              />
            </a>

            {/* Signature — left side (RTL: last child) */}
            <a
              href="https://dralhoshan.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="opacity-80 hover:opacity-100 transition-opacity"
            >
              <img
                src="/manus-storage/signature-hoshan_0c8875c4.webp"
                alt="د. يوسف بن حمود الحوشان"
                className="h-12 w-auto object-contain"
                style={{ filter: "invert(1) brightness(2)" }}
              />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
