/* =============================================
   Navbar — مكنز القضاء والأنظمة والمحاماة
   زر حول المكنز ذهبي صغير مقابل الوضع الليلي، ونافذة تعريفية بهوية عنّابية
   ============================================= */
import { useTheme } from "@/contexts/ThemeContext";
import { Sun, Moon, ShieldCheck } from "lucide-react";
import { useState, useEffect } from "react";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const [scrolled, setScrolled] = useState(false);
  const [aboutOpen, setAboutOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const isDark = theme === "dark";

  return (
    <header
      className="fixed top-0 right-0 left-0 z-50 transition-all duration-300"
      style={{
        background: scrolled
          ? isDark
            ? "oklch(0.14 0.045 22 / 0.97)"
            : "oklch(0.21 0.06 23 / 0.97)"
          : "oklch(0.20 0.055 23 / 0.78)",
        backdropFilter: scrolled ? "blur(12px)" : "none",
        borderBottom: scrolled
          ? isDark
            ? "1px solid oklch(0.62 0.11 72 / 0.45)"
            : "1px solid oklch(0.62 0.11 72 / 0.60)"
          : "1px solid oklch(0.62 0.11 72 / 0.35)",
      }}
    >
      <div className="container">
        <div className="flex items-center justify-between h-16">

          {/* Right: About the thesaurus — identity-colored compact control */}
          <Dialog open={aboutOpen} onOpenChange={setAboutOpen}>
            <button
              onClick={() => setAboutOpen(true)}
              className="inline-flex h-9 items-center gap-1.5 rounded-lg px-3 transition-all hover:opacity-85 active:scale-[0.97]"
              style={{
                background: isDark ? "oklch(0.29 0.07 24)" : "oklch(0.31 0.075 24)",
                border: "1px solid oklch(0.62 0.11 72 / 0.7)",
                color: "oklch(0.78 0.14 76)",
                fontFamily: "Thmanyah Sans, Cairo, sans-serif",
              }}
              title="حول المكنز"
            >
              <ShieldCheck className="h-3.5 w-3.5" />
              <span className="text-[10px] font-semibold">حول المكنز</span>
            </button>

            <DialogContent
              dir="rtl"
              showCloseButton={false}
              className="max-w-md text-right"
              style={{
                background: "oklch(0.23 0.06 23)",
                borderColor: "oklch(0.62 0.11 72 / 0.75)",
                color: "oklch(0.94 0.03 82)",
                fontFamily: "Thmanyah Sans, Cairo, sans-serif",
              }}
            >
              <div className="flex items-center justify-between gap-4 border-b pb-3" style={{ borderColor: "oklch(0.62 0.11 72 / 0.45)" }}>
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-5 w-5" style={{ color: "oklch(0.78 0.14 76)" }} />
                  <DialogTitle className="text-base" style={{ fontFamily: "Thmanyah Serif Display, Amiri, serif", color: "oklch(0.78 0.14 76)" }}>
                    حول المكنز
                  </DialogTitle>
                </div>
                <DialogClose className="text-xl leading-none opacity-65 transition-opacity hover:opacity-100" aria-label="إغلاق">×</DialogClose>
              </div>

              <DialogDescription className="pt-1 text-right text-sm leading-8" style={{ color: "oklch(0.88 0.03 80)", fontFamily: "Thmanyah Sans, Cairo, sans-serif" }}>
                مكنز القضاء والأنظمة والمحاماة فهرسٌ تجميعيٌّ للروابط والإحالات إلى مواد قانونية وقضائية منشورة في مصادر خارجية، أُعدّ لتيسير الوصول وخدمة الباحثين والقضاة والمحامين. لا يدّعي ملكية المواد ولا يضمن محتواها أو دقتها أو بقاء روابطها. تبقى الحقوق لأصحابها، ويتحمل المستخدم مسؤولية التحقق من المادة وحقوق استخدامها، ومن له حق أو ملاحظة فليتواصل عبر البريد الإلكتروني.
              </DialogDescription>

              <div className="flex justify-center pt-2">
                <DialogClose asChild>
                  <button
                    className="rounded-lg px-6 py-2 text-xs font-semibold transition-opacity hover:opacity-85 active:scale-[0.97]"
                    style={{ background: "oklch(0.74 0.13 76)", color: "oklch(0.17 0.05 22)", fontFamily: "Thmanyah Sans, Cairo, sans-serif" }}
                  >
                    فهمت
                  </button>
                </DialogClose>
              </div>
            </DialogContent>
          </Dialog>

          {/* Center: empty spacer */}
          <div className="flex-1" />

          {/* Left: Dark Mode Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="w-9 h-9 rounded-lg flex items-center justify-center transition-colors"
              style={{
                background: isDark ? "oklch(0.29 0.07 24)" : "oklch(0.31 0.075 24)",
                border: "1px solid oklch(0.62 0.11 72 / 0.7)",
                color: "oklch(0.78 0.14 76)",
              }}
              title={isDark ? "الوضع النهاري" : "الوضع الليلي"}
            >
              {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
